"""
Frontend Tkinter unificado para o Surebets Hunter Pro.

Este arquivo substitui o tinker_ui.py original, usando o sistema de
internacionalização unificado e conectando-se às APIs unificadas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import locale
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import subprocess
import sys
import os
import time
import logging

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar sistema de internacionalização unificado
from backend.core.i18n import get_text, I18n, DEFAULT_LANGUAGE

# Inicializar sistema de internacionalização
i18n = I18n()

# Detectar idioma do sistema
lang = locale.getdefaultlocale()[0]
lang = 'pt' if lang and lang.startswith('pt') else 'en'
i18n.set_language(lang)

API_BASE = 'http://localhost:5000/api'

# Configuração do logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("surebets_app.log"),
        logging.StreamHandler()
    ]
)


class SurebetsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(i18n.t('dashboard_title'))
        self.geometry('1100x700')
        self.resizable(True, True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.create_surebets_tab()
        self.create_games_tab()
        self.create_admin_tab()
        self.create_graphs_tab()

    def create_surebets_tab(self):
        """Cria a aba de surebets usando o sistema unificado."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=i18n.t('dashboard_title'))

        # Filtros
        filter_frame = ttk.LabelFrame(frame, text=i18n.t('filters'))
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Esporte
        ttk.Label(filter_frame, text=i18n.t('sport')).grid(row=0, column=0, padx=2, pady=2)
        self.sport_var = tk.StringVar(value='soccer')
        self.sport_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sport_var,
            values=['soccer', 'tennis', 'basketball'],
            state='readonly'
        )
        self.sport_combo.grid(row=0, column=1, padx=2, pady=2)

        # Casas de apostas
        ttk.Label(filter_frame, text=i18n.t('bookmakers')).grid(row=0, column=2, padx=2, pady=2)
        self.bookmaker_var = tk.StringVar()
        self.bookmaker_combo = ttk.Entry(filter_frame, textvariable=self.bookmaker_var)
        self.bookmaker_combo.grid(row=0, column=3, padx=2, pady=2)

        # Lucro mínimo
        ttk.Label(filter_frame, text=i18n.t('min_profit')).grid(row=0, column=4, padx=2, pady=2)
        self.min_profit_var = tk.DoubleVar(value=2.0)
        self.min_profit_spin = ttk.Spinbox(
            filter_frame,
            from_=0,
            to=20,
            increment=0.5,
            textvariable=self.min_profit_var,
            width=5
        )
        self.min_profit_spin.grid(row=0, column=5, padx=2, pady=2)

        # Busca
        ttk.Label(filter_frame, text=i18n.t('search')).grid(row=0, column=6, padx=2, pady=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=0, column=7, padx=2, pady=2)

        # Botão atualizar
        ttk.Button(
            filter_frame,
            text=i18n.t('update_now'),
            command=self.update_surebets_table
        ).grid(row=0, column=8, padx=2, pady=2)

        # Tabela de oportunidades
        self.surebets_tree = ttk.Treeview(
            frame,
            columns=('event', 'market', 'profit', 'bookmakers', 'actions'),
            show='headings'
        )

        for col in self.surebets_tree['columns']:
            header_text = i18n.t(col) if i18n.t(col) != col else col.title()
            self.surebets_tree.heading(col, text=header_text)
            self.surebets_tree.column(col, width=150)

        self.surebets_tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.surebets_tree.bind('<Double-1>', self.show_surebet_details)

        # Status
        self.surebets_status = tk.Label(frame, text='', fg='blue')
        self.surebets_status.pack()

        # Atualização automática
        self.update_surebets_table()

    def update_surebets_table(self):
        """Atualiza a tabela de surebets."""
        # Capturar valores dos filtros
        sport = self.sport_var.get()
        min_profit = self.min_profit_var.get()
        bookmakers = [b.strip() for b in self.bookmaker_var.get().split(',') if b.strip()]
        search = self.search_var.get().lower()

        def fetch(sport, min_profit, bookmakers, search):
            try:
                payload = {
                    'sports': [sport],
                    'min_profit': min_profit,
                    'bookmakers': bookmakers
                }
                resp = requests.post(f'{API_BASE}/opportunities', json=payload, timeout=3)
                data = resp.json()

                # Corrigir para acessar a lista de oportunidades corretamente
                opportunities = data.get('opportunities', [])

                # Filtrar por busca
                if search:
                    opportunities = [
                        item for item in opportunities
                        if search in item['event'].lower() or search in item['market'].lower()
                    ]

                def update_table():
                    self.surebets_tree.delete(*self.surebets_tree.get_children())
                    for item in opportunities:
                        self.surebets_tree.insert(
                            '', 'end',
                            values=(
                                item['event'],
                                item['market'],
                                f"{item['profit']:.2f}%",
                                item.get('bookmaker', 'N/A'),
                                i18n.t('details')
                            )
                        )
                    self.surebets_status.config(text='')

                try:
                    self.after(0, update_table)
                except RuntimeError:
                    pass

            except Exception as e:
                def show_error():
                    self.surebets_tree.delete(*self.surebets_tree.get_children())
                    self.surebets_status.config(text=f"{i18n.t('error')}: {e}")

                try:
                    self.after(0, show_error)
                except RuntimeError:
                    pass

            # Reagendar próxima atualização
            try:
                self.after(5000, self.update_surebets_table)
            except RuntimeError:
                pass

        threading.Thread(target=fetch, args=(sport, min_profit, bookmakers, search), daemon=True).start()

    def show_surebet_details(self, event):
        """Exibe detalhes de uma surebet selecionada."""
        item_id = self.surebets_tree.focus()
        if not item_id:
            return

        values = self.surebets_tree.item(item_id, 'values')
        details = (
            f"{i18n.t('event')}: {values[0]}\n"
            f"{i18n.t('market')}: {values[1]}\n"
            f"{i18n.t('profit')}: {values[2]}\n"
            f"{i18n.t('bookmakers')}: {values[3]}"
        )
        messagebox.showinfo(i18n.t('details'), details)

    def create_games_tab(self):
        """Cria a aba de jogos."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=i18n.t('games_tab'))

        # Jogos ao vivo
        live_label = ttk.Label(frame, text=i18n.t('live_games'), font=('Arial', 14, 'bold'))
        live_label.pack(pady=5)

        self.live_tree = ttk.Treeview(
            frame,
            columns=('event', 'status', 'start_time', 'bookmaker'),
            show='headings'
        )

        for col in self.live_tree['columns']:
            header_text = i18n.t(col) if i18n.t(col) != col else col.title()
            self.live_tree.heading(col, text=header_text)
            self.live_tree.column(col, width=180)

        self.live_tree.pack(fill='x', padx=10)

        # Próximos jogos
        up_label = ttk.Label(frame, text=i18n.t('upcoming_games'), font=('Arial', 14, 'bold'))
        up_label.pack(pady=5)

        self.up_tree = ttk.Treeview(
            frame,
            columns=('event', 'status', 'start_time', 'bookmaker'),
            show='headings'
        )

        for col in self.up_tree['columns']:
            header_text = i18n.t(col) if i18n.t(col) != col else col.title()
            self.up_tree.heading(col, text=header_text)
            self.up_tree.column(col, width=180)

        self.up_tree.pack(fill='x', padx=10)

        # Atualização automática
        self.update_games_tables()

    def update_games_tables(self):
        """Atualiza as tabelas de jogos."""
        def fetch():
            try:
                live = requests.get(f'{API_BASE}/games/live', timeout=3).json().get('games', [])
                up = requests.get(f'{API_BASE}/games/upcoming', timeout=3).json().get('games', [])

                def update_tables():
                    # Atualizar jogos ao vivo
                    self.live_tree.delete(*self.live_tree.get_children())
                    for g in live:
                        self.live_tree.insert(
                            '', 'end',
                            values=(
                                g.get('name'),
                                g.get('status'),
                                g.get('start_time'),
                                g.get('bookmaker')
                            )
                        )

                    # Atualizar próximos jogos
                    self.up_tree.delete(*self.up_tree.get_children())
                    for g in up:
                        self.up_tree.insert(
                            '', 'end',
                            values=(
                                g.get('name'),
                                g.get('status'),
                                g.get('start_time'),
                                g.get('bookmaker')
                            )
                        )

                self.after(0, update_tables)

            except Exception as e:
                def show_error():
                    self.live_tree.delete(*self.live_tree.get_children())
                    self.up_tree.delete(*self.up_tree.get_children())

                self.after(0, show_error)

            # Reagendar próxima atualização
            self.after(5000, self.update_games_tables)

        threading.Thread(target=fetch, daemon=True).start()

    def create_admin_tab(self):
        """Cria a aba de administração."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=i18n.t('admin_tab'))

        # Configurações
        settings_label = ttk.Label(frame, text=i18n.t('settings'), font=('Arial', 13, 'bold'))
        settings_label.pack(pady=5)

        self.settings_text = tk.Text(frame, height=6, width=100)
        self.settings_text.pack()

        ttk.Button(frame, text=i18n.t('save_settings'), command=self.save_settings).pack(pady=2)

        # Notificações
        notif_label = ttk.Label(frame, text=i18n.t('notifications'), font=('Arial', 13, 'bold'))
        notif_label.pack(pady=5)

        self.notif_entry = tk.Entry(frame, width=60)
        self.notif_entry.pack()

        ttk.Button(frame, text=i18n.t('send_test'), command=self.send_test_notification).pack(pady=2)

        # Visão geral do banco de dados
        db_label = ttk.Label(frame, text=i18n.t('db'), font=('Arial', 13, 'bold'))
        db_label.pack(pady=5)

        self.db_text = tk.Text(frame, height=6, width=100)
        self.db_text.pack()

        ttk.Button(frame, text=i18n.t('update_now'), command=self.load_db_overview).pack(pady=2)

        # Inserir aposta
        bet_label = ttk.Label(frame, text=i18n.t('insert_bet'), font=('Arial', 13, 'bold'))
        bet_label.pack(pady=5)

        # Campos da aposta
        bet_frame = ttk.Frame(frame)
        bet_frame.pack(pady=5)

        self.bet_event = tk.Entry(bet_frame, width=20)
        self.bet_event.pack(side='left', padx=2)

        self.bet_market = tk.Entry(bet_frame, width=10)
        self.bet_market.pack(side='left', padx=2)

        self.bet_selection = tk.Entry(bet_frame, width=10)
        self.bet_selection.pack(side='left', padx=2)

        self.bet_odd = tk.Entry(bet_frame, width=8)
        self.bet_odd.pack(side='left', padx=2)

        self.bet_bookmaker = tk.Entry(bet_frame, width=12)
        self.bet_bookmaker.pack(side='left', padx=2)

        ttk.Button(bet_frame, text=i18n.t('insert_bet'), command=self.insert_bet).pack(side='left', padx=2)

        self.bet_status = tk.Label(frame, text='', fg='green')
        self.bet_status.pack(pady=2)

        # Carregar dados iniciais
        self.load_settings()
        self.load_db_overview()

    def load_settings(self):
        """Carrega as configurações do sistema."""
        try:
            data = requests.get(f'{API_BASE}/admin/settings').json()
            self.settings_text.delete('1.0', tk.END)
            self.settings_text.insert(tk.END, str(data))
        except Exception:
            self.settings_text.delete('1.0', tk.END)
            self.settings_text.insert(tk.END, i18n.t('error'))

    def save_settings(self):
        """Salva as configurações do sistema."""
        try:
            # Mock request para a API unificada
            requests.post(f'{API_BASE}/admin/settings', json={})
            messagebox.showinfo(i18n.t('settings'), i18n.t('success_bet'))
        except Exception:
            messagebox.showerror(i18n.t('error'), i18n.t('error'))

    def send_test_notification(self):
        """Envia uma notificação de teste."""
        msg = self.notif_entry.get()
        if not msg:
            messagebox.showwarning(i18n.t('error'), i18n.t('fill_all'))
            return

        try:
            requests.post(f'{API_BASE}/admin/test-notification', json={'message': msg})
            messagebox.showinfo(i18n.t('notifications'), i18n.t('success_bet'))
        except Exception:
            messagebox.showerror(i18n.t('error'), i18n.t('error'))

    def load_db_overview(self):
        """Carrega a visão geral do banco de dados."""
        try:
            data = requests.get(f'{API_BASE}/admin/db-overview').json()
            self.db_text.delete('1.0', tk.END)
            self.db_text.insert(tk.END, str(data))
        except Exception:
            self.db_text.delete('1.0', tk.END)
            self.db_text.insert(tk.END, i18n.t('error'))

    def insert_bet(self):
        """Insere uma nova aposta no sistema."""
        event = self.bet_event.get()
        market = self.bet_market.get()
        selection = self.bet_selection.get()
        odd = self.bet_odd.get()
        bookmaker = self.bet_bookmaker.get()

        if not all([event, market, selection, odd, bookmaker]):
            self.bet_status.config(text=i18n.t('fill_all'), fg='red')
            return

        try:
            odd = float(odd)
            if odd < 1.01:
                self.bet_status.config(text=i18n.t('odd_gt_1'), fg='red')
                return
        except Exception:
            self.bet_status.config(text=i18n.t('invalid_odd'), fg='red')
            return

        try:
            resp = requests.post(f'{API_BASE}/admin/insert-bet', json={
                'event': event,
                'market': market,
                'selection': selection,
                'odd': odd,
                'bookmaker': bookmaker
            })

            if resp.status_code == 200:
                self.bet_status.config(text=i18n.t('success_bet'), fg='green')
                # Limpar campos
                self.bet_event.delete(0, tk.END)
                self.bet_market.delete(0, tk.END)
                self.bet_selection.delete(0, tk.END)
                self.bet_odd.delete(0, tk.END)
                self.bet_bookmaker.delete(0, tk.END)
            else:
                self.bet_status.config(text=i18n.t('error'), fg='red')

        except Exception:
            self.bet_status.config(text=i18n.t('error'), fg='red')

    def create_graphs_tab(self):
        """Cria a aba de gráficos."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Gráficos')

        # Gráfico de evolução de odds
        odds_label = ttk.Label(frame, text='Evolução das Odds', font=('Arial', 13, 'bold'))
        odds_label.pack(pady=5)

        odds_fig, odds_ax = plt.subplots(figsize=(6, 3))

        try:
            odds_data = requests.get(f'{API_BASE}/odds-history').json()
            for event in odds_data:
                odds_ax.plot(event['timestamps'], event['odds'], marker='o', label=event['event'])
            odds_ax.set_title('Evolução das Odds')
            odds_ax.set_xlabel('Tempo')
            odds_ax.set_ylabel('Odd')
            odds_ax.legend()
        except Exception as e:
            odds_ax.text(0.5, 0.5, f'Erro ao carregar dados: {e}', ha='center')

        canvas1 = FigureCanvasTkAgg(odds_fig, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(pady=10)

        # Gráfico de distribuição de oportunidades
        dist_label = ttk.Label(frame, text='Distribuição de Oportunidades', font=('Arial', 13, 'bold'))
        dist_label.pack(pady=5)

        dist_fig, dist_ax = plt.subplots(figsize=(6, 3))

        try:
            dist_data = requests.get(f'{API_BASE}/opportunity-distribution').json()
            labels = list(dist_data.keys())
            sizes = list(dist_data.values())
            dist_ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            dist_ax.set_title('Distribuição de Oportunidades por Esporte')
        except Exception as e:
            dist_ax.text(0.5, 0.5, f'Erro ao carregar dados: {e}', ha='center')

        canvas2 = FigureCanvasTkAgg(dist_fig, master=frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(pady=10)


def wait_backend_ready(url, timeout=20):
    """Aguarda o backend estar pronto."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False


if __name__ == '__main__':
    # Iniciar o backend automaticamente (versão unificada)
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'apps', 'dashboard.py')
    backend_path = os.path.abspath(backend_path)
    python_exe = sys.executable

    try:
        subprocess.Popen([python_exe, backend_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logging.error(f'Não foi possível iniciar o backend automaticamente: {e}')

    # Aguardar o backend responder
    logging.info('Aguardando backend unificado iniciar...')
    if not wait_backend_ready(f'{API_BASE}/games/live'):
        logging.error('Backend unificado não respondeu a tempo. Fechando...')
        sys.exit(1)

    logging.info('Backend unificado iniciado com sucesso!')
    app = SurebetsApp()
    app.mainloop()
