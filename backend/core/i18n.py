"""
Sistema unificado de internacionalização para o Surebets Hunter Pro.

Consolida todas as traduções e funcionalidades de idioma em um módulo centralizado.
Remove redundâncias entre diferentes partes do sistema.
"""

from typing import Dict, List, Optional
import os
from config.config_loader import CONFIG

# Dicionário centralizado com todas as traduções do sistema
LANGUAGES = {
    "pt": {
        # Dashboard e UI principal
        "dashboard_title": "🤑 Surebets Hunter Pro",
        "filters": "Filtros Ativos",
        "sport": "Esporte",
        "bookmakers": "Casas de Apostas",
        "min_profit": "Lucro Mínimo (%)",
        "real_time_opportunities": "Oportunidades em Tempo Real",
        "search_event_market": "Buscar evento ou mercado...",
        "update_now": "Atualizar Agora",
        "details": "Detalhes da Oportunidade",
        "close": "Fechar",
        "admin": "Administração",
        "settings": "Configurações Gerais",
        "save_settings": "Salvar Configurações",
        "notifications": "Notificações",
        "send_test": "Enviar Teste",
        "login": "Entrar",
        "logout": "Sair",
        "username": "Nome de usuário",
        "password": "Senha",
        "cancel": "Cancelar",
        # Jogos e eventos
        "games": "Jogos",
        "live_games": "Jogos ao Vivo",
        "upcoming_games": "Próximos Jogos",
        "status": "Status",
        "start_time": "Início",
        "event": "Evento",
        "market": "Mercado",
        "selection": "Seleção",
        "odd": "Odd",
        "actions": "Ações",
        # Apostas e inserção de dados
        "insert_bet": "Inserir Nova Aposta",
        "success_bet": "Aposta inserida com sucesso!",
        "fill_all": "Preencha todos os campos!",
        "invalid_odd": "Odd inválida!",
        "odd_gt_1": "Odd deve ser maior que 1.00!",
        "error": "Erro",
        "profit": "Lucro (%)",
        # Banco de dados e administração
        "db": "Banco de Dados",
        "missing_field": "Campo obrigatório ausente",
        "bet_inserted": "Aposta inserida no banco!",
        "notification_sent": "Notificação enviada!",
        "fail_register_event": "Falha ao registrar evento.",
        "unauthorized": "Acesso não autorizado. Requer login.",
        # Autenticação
        "login_success": "Login realizado com sucesso!",
        "login_failed": "Falha no login. Verifique suas credenciais.",
        "logout_success": "Logout realizado com sucesso!",
        "settings_saved": "Configurações salvas!",
        # Erros e mensagens do sistema
        "test_sent": "Notificação enviada!",
        "test_fail": "Falha ao enviar notificação.",
        # Interface Tkinter
        "games_tab": "Jogos",
        "admin_tab": "Administração",
        "search": "Buscar",
        "bookmaker": "Casa de Apostas",
    },
    "en": {
        # Dashboard e UI principal
        "dashboard_title": "🤑 Surebets Hunter Pro",
        "filters": "Active Filters",
        "sport": "Sport",
        "bookmakers": "Bookmakers",
        "min_profit": "Minimum Profit (%)",
        "real_time_opportunities": "Real-Time Opportunities",
        "search_event_market": "Search for event or market...",
        "update_now": "Update Now",
        "details": "Opportunity Details",
        "close": "Close",
        "admin": "Administration",
        "settings": "General Settings",
        "save_settings": "Save Settings",
        "notifications": "Notifications",
        "send_test": "Send Test",
        "login": "Login",
        "logout": "Logout",
        "username": "Username",
        "password": "Password",
        "cancel": "Cancel",
        # Jogos e eventos
        "games": "Games",
        "live_games": "Live Games",
        "upcoming_games": "Upcoming Games",
        "status": "Status",
        "start_time": "Start Time",
        "event": "Event",
        "market": "Market",
        "selection": "Selection",
        "odd": "Odd",
        "actions": "Actions",
        # Apostas e inserção de dados
        "insert_bet": "Insert New Bet",
        "success_bet": "Bet successfully inserted!",
        "fill_all": "Fill in all fields!",
        "invalid_odd": "Invalid odd!",
        "odd_gt_1": "Odd must be greater than 1.00!",
        "error": "Error",
        "profit": "Profit (%)",
        # Banco de dados e administração
        "db": "Database",
        "missing_field": "Required field missing",
        "bet_inserted": "Bet inserted in database!",
        "notification_sent": "Notification sent!",
        "fail_register_event": "Failed to register event.",
        "unauthorized": "Unauthorized access. Login required.",
        # Autenticação
        "login_success": "Login successful!",
        "login_failed": "Login failed. Check your credentials.",
        "logout_success": "Logout successful!",
        "settings_saved": "Settings saved!",
        # Erros e mensagens do sistema
        "test_sent": "Notification sent!",
        "test_fail": "Failed to send notification.",
        # Interface Tkinter
        "games_tab": "Games",
        "admin_tab": "Administration",
        "search": "Search",
        "bookmaker": "Bookmaker",
    },
    "pt-br": {
        # Traduções em português brasileiro (pode ser igual ao "pt" ou customizado)
        "dashboard_title": "🤑 Surebets Hunter Pro",
        "filters": "Filtros Ativos",
        "sport": "Esporte",
        "bookmakers": "Casas de Apostas",
        "min_profit": "Lucro Mínimo (%)",
        "real_time_opportunities": "Oportunidades em Tempo Real",
        "search_event_market": "Buscar evento ou mercado...",
        "update_now": "Atualizar Agora",
        "details": "Detalhes da Oportunidade",
        "close": "Fechar",
        "admin": "Administração",
        "settings": "Configurações Gerais",
        "save_settings": "Salvar Configurações",
        "notifications": "Notificações",
        "send_test": "Enviar Teste",
        "login": "Entrar",
        "logout": "Sair",
        "username": "Nome de usuário",
        "password": "Senha",
        "cancel": "Cancelar",
        # Jogos e eventos
        "games": "Jogos",
        "live_games": "Jogos ao Vivo",
        "upcoming_games": "Próximos Jogos",
        "status": "Status",
        "start_time": "Início",
        "event": "Evento",
        "market": "Mercado",
        "selection": "Seleção",
        "odd": "Odd",
        "actions": "Ações",
        # Apostas e inserção de dados
        "insert_bet": "Inserir Nova Aposta",
        "success_bet": "Aposta inserida com sucesso!",
        "fill_all": "Preencha todos os campos!",
        "invalid_odd": "Odd inválida!",
        "odd_gt_1": "Odd deve ser maior que 1.00!",
        "error": "Erro",
        "profit": "Lucro (%)",
        # Banco de dados e administração
        "db": "Banco de Dados",
        "missing_field": "Campo obrigatório ausente",
        "bet_inserted": "Aposta inserida no banco!",
        "notification_sent": "Notificação enviada!",
        "fail_register_event": "Falha ao registrar evento.",
        "unauthorized": "Acesso não autorizado. Requer login.",
        # Autenticação
        "login_success": "Login realizado com sucesso!",
        "login_failed": "Falha no login. Verifique suas credenciais.",
        "logout_success": "Logout realizado com sucesso!",
        "settings_saved": "Configurações salvas!",
        # Erros e mensagens do sistema
        "test_sent": "Notificação enviada!",
        "test_fail": "Falha ao enviar notificação.",
        # Interface Tkinter
        "games_tab": "Jogos",
        "admin_tab": "Administração",
        "search": "Buscar",
        "bookmaker": "Casa de Apostas",
    },
}

# Idioma padrão do sistema
DEFAULT_LANGUAGE = CONFIG["ui"].get("language", "pt")


def get_text(key: str, lang: Optional[str] = None) -> str:
    """
    Obtém o texto traduzido para uma chave específica.

    Args:
        key: A chave do texto no dicionário de traduções
        lang: O código do idioma a ser usado (padrão: idioma do sistema)

    Returns:
        O texto traduzido ou a própria chave se não encontrado
    """
    if lang is None:
        lang = DEFAULT_LANGUAGE

    # Garante que usamos um idioma suportado
    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE

    # Retorna a tradução ou a chave se não encontrada
    return LANGUAGES[lang].get(key, key)


def get_supported_languages() -> List[str]:
    """
    Retorna a lista de idiomas suportados.

    Returns:
        Lista de códigos de idioma suportados
    """
    return list(LANGUAGES.keys())


def get_language_dict(lang: Optional[str] = None) -> Dict[str, str]:
    """
    Retorna o dicionário completo de traduções para um idioma.

    Args:
        lang: O código do idioma (padrão: idioma do sistema)

    Returns:
        Dicionário com todas as traduções do idioma
    """
    if lang is None:
        lang = DEFAULT_LANGUAGE

    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE

    return LANGUAGES[lang]


def set_system_language(lang: str) -> bool:
    """
    Define o idioma padrão do sistema.

    Args:
        lang: Código do idioma a ser definido

    Returns:
        True se o idioma foi definido com sucesso, False caso contrário
    """
    global DEFAULT_LANGUAGE

    if lang in LANGUAGES:
        DEFAULT_LANGUAGE = lang
        os.environ["SYSTEM_LANGUAGE"] = lang
        return True

    return False


# Função de compatibilidade para código existente
def get_lang() -> str:
    """
    Obtém o idioma atual do sistema.
    Função de compatibilidade com código existente.

    Returns:
        Código do idioma atual
    """
    return DEFAULT_LANGUAGE


# Classe para facilitar o uso em diferentes contextos
class I18n:
    """Classe utilitária para internacionalização."""

    def __init__(self, lang: Optional[str] = None):
        self.lang = lang or DEFAULT_LANGUAGE

    def t(self, key: str) -> str:
        """Traduz uma chave para o idioma configurado."""
        return get_text(key, self.lang)

    def set_language(self, lang: str) -> bool:
        """Define o idioma para esta instância."""
        if lang in LANGUAGES:
            self.lang = lang
            return True
        return False

    def get_dict(self) -> Dict[str, str]:
        """Retorna o dicionário de traduções para o idioma atual."""
        return get_language_dict(self.lang)
