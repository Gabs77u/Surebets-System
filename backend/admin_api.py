from flask import Flask, jsonify, request
from config import settings
from backend.notification_system import notify_all
from backend.database.database import Database
from datetime import datetime

app = Flask(__name__)

# Função utilitária para internacionalização de mensagens
LANGUAGES = {
    'pt': {
        'missing_field': 'Campo obrigatório ausente',
        'bet_inserted': 'Aposta inserida no banco!',
        'error': 'Erro',
        'notification_sent': 'Notificação enviada!',
        'fail_register_event': 'Falha ao registrar evento.'
    },
    'en': {
        'missing_field': 'Required field missing',
        'bet_inserted': 'Bet inserted in database!',
        'error': 'Error',
        'notification_sent': 'Notification sent!',
        'fail_register_event': 'Failed to register event.'
    }
}

def get_lang():
    return request.headers.get('Accept-Language', 'pt')[:2]

@app.route('/api/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if request.method == 'GET':
        # Retorna configurações atuais
        return jsonify({
            'APP_NAME': settings.APP_NAME,
            'DEBUG': settings.DEBUG,
            'PORT': settings.PORT,
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
            'WHATSAPP_API_URL': settings.WHATSAPP_API_URL,
            'WHATSAPP_TOKEN': settings.WHATSAPP_TOKEN,
            'WHATSAPP_PHONE': settings.WHATSAPP_PHONE,
            'CACHE_TIMEOUT': settings.CACHE_TIMEOUT,
            'POSTGRES_URL': settings.POSTGRES_URL,
            'SECRET_KEY': settings.SECRET_KEY,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS
        })
    elif request.method == 'POST':
        # Aqui você pode implementar lógica para atualizar configurações
        # (exemplo: salvar em arquivo/env)
        lang = get_lang()
        status_msg = {
            'pt': 'Configurações salvas (mock)!',
            'en': 'Settings saved (mock)!'
        }
        return jsonify({'status': status_msg.get(lang, status_msg['pt'])}), 200

@app.route('/api/admin/test-notification', methods=['POST'])
def admin_test_notification():
    data = request.json
    msg = data.get('message', LANGUAGES[get_lang()]['notification_sent'])
    try:
        notify_all(msg)
        return jsonify({'status': LANGUAGES[get_lang()]['notification_sent']}), 200
    except Exception as e:
        return jsonify({'error': f"{LANGUAGES[get_lang()]['error']}: {str(e)}"}), 500

@app.route('/api/admin/db-overview', methods=['GET'])
def admin_db_overview():
    db = Database()
    try:
        events = db.fetch('SELECT * FROM events LIMIT 10')
        surebets = db.fetch('SELECT * FROM surebets LIMIT 10')
        return jsonify({'events': events, 'surebets': surebets})
    except Exception as e:
        return jsonify({'error': f"{LANGUAGES[get_lang()]['error']}: {str(e)}"}), 500
    finally:
        db.close()

@app.route('/api/admin/insert-bet', methods=['POST'])
def admin_insert_bet():
    data = request.json
    # Validação avançada
    required = ["event", "market", "selection", "odd", "bookmaker"]
    for field in required:
        if not data.get(field):
            return jsonify({'error': f"{LANGUAGES[get_lang()]['missing_field']}: {field}"}), 400
    try:
        db = Database()
        # Inserção de evento (ou busca se já existe)
        event_name = data["event"]
        market = data["market"]
        db.execute("""
            INSERT INTO events (id, name, market, start_time)
            VALUES (floor(extract(epoch from now())), %s, %s, now())
            ON CONFLICT (name, market) DO NOTHING
        """, (event_name, market))
        # Busca o id do evento
        event_row = db.fetch("SELECT id FROM events WHERE name=%s AND market=%s ORDER BY start_time DESC LIMIT 1", (event_name, market))
        if not event_row:
            return jsonify({'error': LANGUAGES[get_lang()]['fail_register_event']}), 500
        event_id = event_row[0]['id']
        # Inserção da seleção
        selection = data["selection"]
        odd = float(data["odd"])
        bookmaker = data["bookmaker"]
        db.execute("""
            INSERT INTO selections (id, event_id, name, odds, bookmaker, timestamp)
            VALUES (floor(extract(epoch from now())*1000), %s, %s, %s, %s, now())
            ON CONFLICT (id) DO NOTHING
        """, (event_id, selection, odd, bookmaker))
        db.close()
        return jsonify({'status': LANGUAGES[get_lang()]['bet_inserted']}), 200
    except Exception as e:
        return jsonify({'error': f"{LANGUAGES[get_lang()]['error']}: {str(e)}"}), 500

@app.route('/api/admin/suggestions', methods=['GET'])
def admin_suggestions():
    """Sugestões baseadas em histórico de apostas."""
    try:
        db = Database()
        # Sugestão de eventos mais frequentes
        events = db.fetch("SELECT name, COUNT(*) as freq FROM events GROUP BY name ORDER BY freq DESC LIMIT 5")
        # Sugestão de seleções mais comuns
        selections = db.fetch("SELECT name, COUNT(*) as freq FROM selections GROUP BY name ORDER BY freq DESC LIMIT 5")
        # Sugestão de odds médias por seleção
        odds = db.fetch("SELECT name, ROUND(AVG(odds),2) as avg_odd FROM selections GROUP BY name ORDER BY avg_odd DESC LIMIT 5")
        db.close()
        return jsonify({
            'events': events,
            'selections': selections,
            'odds': odds
        })
    except Exception as e:
        return jsonify({'error': f"{LANGUAGES[get_lang()]['error']}: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
