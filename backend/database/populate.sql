-- POPULAÇÃO INICIAL DO BANCO DE DADOS POSTGRESQL PARA SUREBETS SYSTEM
-- encoding: UTF-8

INSERT INTO users (username, email, password_hash, role, is_active)
VALUES
    ('admin', 'admin@surebets.com', '$2b$12$hashadmin', 'admin', TRUE),
    ('operador', 'operador@surebets.com', '$2b$12$hashoperador', 'operator', TRUE),
    ('visualizador', 'visualizador@surebets.com', '$2b$12$hashviewer', 'viewer', TRUE)
ON CONFLICT (username) DO NOTHING;

INSERT INTO leagues (name, sport, country, is_active) VALUES
    ('Premier League', 'Futebol', 'Inglaterra', TRUE),
    ('NBA', 'Basquete', 'EUA', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO events (external_id, league_id, home_team, away_team, start_time, status, is_active)
VALUES
    ('EVT001', 1, 'Manchester United', 'Chelsea', '2025-06-15 16:00:00', 'upcoming', TRUE),
    ('EVT002', 2, 'Lakers', 'Celtics', '2025-06-16 20:00:00', 'upcoming', TRUE)
ON CONFLICT (external_id) DO NOTHING;

INSERT INTO bookmakers (name, api_key, is_active) VALUES
    ('Bet365', 'api_key_bet365', TRUE),
    ('Pinnacle', 'api_key_pinnacle', TRUE)
ON CONFLICT (name) DO NOTHING;

INSERT INTO markets (name, sport, is_active) VALUES
    ('Resultado Final', 'Futebol', TRUE),
    ('Total de Pontos', 'Basquete', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO selections (event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
    (1, 1, 1, 'Vitória Manchester United', 2.10, TRUE),
    (1, 1, 2, 'Vitória Chelsea', 3.20, TRUE),
    (2, 2, 1, 'Mais de 200 pontos', 1.90, TRUE),
    (2, 2, 2, 'Menos de 200 pontos', 2.00, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO surebets (event_id, detected_at, profit, details) VALUES
    (1, '2025-06-10 12:00:00', 5.50, '{"type": "arbitrage", "desc": "Exemplo de surebet"}')
ON CONFLICT DO NOTHING;
