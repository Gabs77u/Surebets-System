-- ============================================================================
-- 🗄️ DADOS INICIAIS - SISTEMA DE SUREBETS (SQLite)
-- ============================================================================
-- População inicial otimizada para SQLite com dados de exemplo realistas

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 🏢 CASAS DE APOSTAS
-- ============================================================================

INSERT OR REPLACE INTO bookmakers (id, name, api_url, rate_limit, timeout_seconds, is_active) VALUES
(1, 'Bet365', 'https://api.bet365.com', 120, 15, 1),
(2, 'Betfair', 'https://api.betfair.com', 100, 12, 1),
(3, 'Pinnacle', 'https://api.pinnacle.com', 150, 10, 1),
(4, 'William Hill', 'https://api.williamhill.com', 90, 20, 1),
(5, 'Betway', 'https://api.betway.com', 110, 15, 1),
(6, 'Unibet', 'https://api.unibet.com', 80, 18, 1);

-- ============================================================================
-- ⚽ ESPORTES E LIGAS
-- ============================================================================

INSERT OR REPLACE INTO sports (id, name, slug, is_active) VALUES
(1, 'Futebol', 'football', 1),
(2, 'Basquete', 'basketball', 1),
(3, 'Tênis', 'tennis', 1),
(4, 'Vôlei', 'volleyball', 1),
(5, 'E-Sports', 'esports', 1);

INSERT OR REPLACE INTO leagues (id, sport_id, name, slug, country, is_active) VALUES
(1, 1, 'Campeonato Brasileiro Série A', 'brasileirao-a', 'Brasil', 1),
(2, 1, 'Premier League', 'premier-league', 'Inglaterra', 1),
(3, 1, 'La Liga', 'la-liga', 'Espanha', 1),
(4, 1, 'Champions League', 'champions-league', 'Europa', 1),
(5, 2, 'NBA', 'nba', 'Estados Unidos', 1),
(6, 3, 'ATP Tour', 'atp-tour', 'Mundial', 1),
(7, 5, 'League of Legends World Championship', 'lol-worlds', 'Mundial', 1);

-- ============================================================================
-- 📊 MERCADOS
-- ============================================================================

INSERT OR REPLACE INTO markets (id, name, slug, description, is_active) VALUES
(1, 'Resultado Final', '1x2', 'Vitória mandante, empate ou vitória visitante', 1),
(2, 'Total de Gols', 'total-goals', 'Acima ou abaixo de um número de gols', 1),
(3, 'Ambas Marcam', 'both-teams-score', 'Se ambos os times marcarão gols', 1),
(4, 'Handicap Asiático', 'asian-handicap', 'Handicap com vantagem/desvantagem', 1),
(5, 'Primeiro Tempo', 'first-half', 'Resultado do primeiro tempo', 1);

-- ============================================================================
-- 🏆 EVENTOS ESPORTIVOS
-- ============================================================================

INSERT OR REPLACE INTO events (id, external_id, league_id, home_team, away_team, start_time, status, is_active) VALUES
(1001, 'BRA_FLA_PAL_20250530', 1, 'Flamengo', 'Palmeiras', '2025-05-30 16:00:00', 'upcoming', 1),
(1002, 'BRA_COR_SAN_20250530', 1, 'Corinthians', 'Santos', '2025-05-30 18:00:00', 'upcoming', 1),
(1003, 'BRA_SAO_GRE_20250531', 1, 'São Paulo', 'Grêmio', '2025-05-31 20:00:00', 'upcoming', 1),
(1004, 'ENG_CHE_ARS_20250601', 2, 'Chelsea', 'Arsenal', '2025-06-01 15:00:00', 'upcoming', 1),
(1005, 'ESP_RMA_BAR_20250601', 3, 'Real Madrid', 'Barcelona', '2025-06-01 21:00:00', 'upcoming', 1),
(1006, 'USA_LAL_GSW_20250602', 5, 'Los Angeles Lakers', 'Golden State Warriors', '2025-06-02 02:00:00', 'upcoming', 1),
(1007, 'WTA_SER_DJO_20250602', 6, 'Serena Williams', 'Novak Djokovic', '2025-06-02 14:00:00', 'upcoming', 1);

-- ============================================================================
-- 🎯 SELEÇÕES E ODDS
-- ============================================================================

-- Flamengo x Palmeiras
INSERT OR REPLACE INTO selections (id, event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
(2001, 1001, 1, 1, 'Flamengo', 2.10, 1),
(2002, 1001, 1, 2, 'Empate', 3.30, 1),
(2003, 1001, 1, 3, 'Palmeiras', 3.50, 1),
(2004, 1001, 1, 4, 'Flamengo', 2.05, 1),
(2005, 1001, 1, 5, 'Empate', 3.40, 1),
(2006, 1001, 1, 6, 'Palmeiras', 3.60, 1);

-- Corinthians x Santos
INSERT OR REPLACE INTO selections (id, event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
(2007, 1002, 1, 1, 'Corinthians', 2.50, 1),
(2008, 1002, 1, 2, 'Empate', 3.10, 1),
(2009, 1002, 1, 3, 'Santos', 2.90, 1),
(2010, 1002, 1, 4, 'Corinthians', 2.45, 1),
(2011, 1002, 1, 5, 'Empate', 3.20, 1),
(2012, 1002, 1, 6, 'Santos', 2.95, 1);

-- São Paulo x Grêmio
INSERT OR REPLACE INTO selections (id, event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
(2013, 1003, 1, 1, 'São Paulo', 1.95, 1),
(2014, 1003, 1, 2, 'Empate', 3.40, 1),
(2015, 1003, 1, 3, 'Grêmio', 4.00, 1),
(2016, 1003, 1, 4, 'São Paulo', 1.90, 1),
(2017, 1003, 1, 5, 'Empate', 3.50, 1),
(2018, 1003, 1, 6, 'Grêmio', 4.20, 1);

-- Chelsea x Arsenal
INSERT OR REPLACE INTO selections (id, event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
(2019, 1004, 1, 1, 'Chelsea', 2.80, 1),
(2020, 1004, 1, 2, 'Empate', 3.20, 1),
(2021, 1004, 1, 3, 'Arsenal', 2.60, 1),
(2022, 1004, 1, 4, 'Chelsea', 2.75, 1),
(2023, 1004, 1, 5, 'Empate', 3.30, 1),
(2024, 1004, 1, 6, 'Arsenal', 2.65, 1);

-- Real Madrid x Barcelona
INSERT OR REPLACE INTO selections (id, event_id, market_id, bookmaker_id, name, odds, is_active) VALUES
(2025, 1005, 1, 1, 'Real Madrid', 2.40, 1),
(2026, 1005, 1, 2, 'Empate', 3.50, 1),
(2027, 1005, 1, 3, 'Barcelona', 2.80, 1),
(2028, 1005, 1, 4, 'Real Madrid', 2.35, 1),
(2029, 1005, 1, 5, 'Empate', 3.60, 1),
(2030, 1005, 1, 6, 'Barcelona', 2.85, 1);

-- ============================================================================
-- 🎯 OPORTUNIDADES DE ARBITRAGEM
-- ============================================================================

INSERT OR REPLACE INTO arbitrage_opportunities (id, event_id, market_id, profit_percentage, total_implied_probability, stakes_json, selections_json, is_active, expires_at, detected_at) VALUES
(3001, 1001, 1, 3.2, 96.8, 
 '{"stakes":[{"bookmaker":"Bet365","selection":"Flamengo","amount":476.19,"percentage":47.62},{"bookmaker":"Pinnacle","selection":"Palmeiras","amount":285.71,"percentage":28.57},{"bookmaker":"Betfair","selection":"Empate","amount":238.10,"percentage":23.81}]}',
 '{"selections":[{"bookmaker":"Bet365","selection":"Flamengo","odds":2.20},{"bookmaker":"Pinnacle","selection":"Palmeiras","odds":4.50},{"bookmaker":"Betfair","selection":"Empate","odds":4.80}]}',
 1, '2025-05-30 15:50:00', '2025-05-29 14:00:00'),

(3002, 1002, 1, 2.7, 97.3,
 '{"stakes":[{"bookmaker":"William Hill","selection":"Corinthians","amount":408.16,"percentage":40.82},{"bookmaker":"Santos","selection":"Santos","amount":338.98,"percentage":33.90},{"bookmaker":"Unibet","selection":"Empate","amount":252.52,"percentage":25.25}]}',
 '{"selections":[{"bookmaker":"William Hill","selection":"Corinthians","odds":2.45},{"bookmaker":"Santos","selection":"Santos","odds":2.95},{"bookmaker":"Unibet","selection":"Empate","odds":3.20}]}',
 1, '2025-05-30 17:50:00', '2025-05-29 14:15:00'),

(3003, 1003, 1, 4.1, 95.9,
 '{"stakes":[{"bookmaker":"William Hill","selection":"São Paulo","amount":526.32,"percentage":52.63},{"bookmaker":"Unibet","selection":"Grêmio","amount":238.10,"percentage":23.81},{"bookmaker":"Unibet","selection":"Empate","amount":235.08,"percentage":23.51}]}',
 '{"selections":[{"bookmaker":"William Hill","selection":"São Paulo","odds":1.90},{"bookmaker":"Unibet","selection":"Grêmio","odds":4.20},{"bookmaker":"Unibet","selection":"Empate","odds":3.50}]}',
 1, '2025-05-31 19:50:00', '2025-05-29 14:30:00');

-- ============================================================================
-- 👥 USUÁRIOS DO SISTEMA
-- ============================================================================

INSERT OR REPLACE INTO users (id, username, email, password_hash, first_name, last_name, is_active, is_admin, email_verified) VALUES
(1, 'admin', 'admin@surebets.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG', 'Administrador', 'Sistema', 1, 1, 1),
(2, 'apostador1', 'carlos@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG', 'Carlos', 'Silva', 1, 0, 1),
(3, 'apostador2', 'maria@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG', 'Maria', 'Santos', 1, 0, 1),
(4, 'trader_pro', 'joao@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQ3V8Yb5mQNXkkG', 'João', 'Trader', 1, 0, 1);

-- ============================================================================
-- 💰 APOSTAS REALIZADAS
-- ============================================================================

INSERT OR REPLACE INTO bets (id, user_id, opportunity_id, selection_id, amount, expected_return, status, placed_at) VALUES
(1, 2, 3001, 2001, 476.19, 1000.00, 'pending', '2025-05-29 14:05:00'),
(2, 2, 3001, 2003, 285.71, 1000.00, 'pending', '2025-05-29 14:05:00'),
(3, 2, 3001, 2002, 238.10, 785.13, 'pending', '2025-05-29 14:05:00'),
(4, 3, 3002, 2010, 408.16, 1000.00, 'pending', '2025-05-29 14:20:00'),
(5, 3, 3002, 2012, 338.98, 1000.00, 'pending', '2025-05-29 14:20:00'),
(6, 4, 3003, 2016, 526.32, 1000.00, 'pending', '2025-05-29 14:35:00');

-- ============================================================================
-- 📊 HISTÓRICO DE ODDS
-- ============================================================================

INSERT OR REPLACE INTO odds_history (id, selection_id, old_odds, new_odds, change_percentage, changed_at) VALUES
(1, 2001, 2.00, 2.10, 5.0, '2025-05-29 12:30:00'),
(2, 2004, 2.00, 2.05, 2.5, '2025-05-29 12:35:00'),
(3, 2007, 2.40, 2.50, 4.17, '2025-05-29 12:40:00'),
(4, 2010, 2.40, 2.45, 2.08, '2025-05-29 12:45:00'),
(5, 2013, 2.00, 1.95, -2.5, '2025-05-29 12:50:00'),
(6, 2016, 2.00, 1.90, -5.0, '2025-05-29 12:55:00'),
(7, 2025, 2.30, 2.40, 4.35, '2025-05-29 13:00:00'),
(8, 2028, 2.30, 2.35, 2.17, '2025-05-29 13:05:00');

-- ============================================================================
-- 📋 LOGS DO SISTEMA
-- ============================================================================

INSERT OR REPLACE INTO system_logs (id, level, module, message, details, user_id, created_at) VALUES
(1, 'INFO', 'arbitrage', 'Nova oportunidade de arbitragem detectada', '{"event_id": 1001, "profit": 3.2}', NULL, '2025-05-29 14:00:00'),
(2, 'INFO', 'arbitrage', 'Nova oportunidade de arbitragem detectada', '{"event_id": 1002, "profit": 2.7}', NULL, '2025-05-29 14:15:00'),
(3, 'INFO', 'arbitrage', 'Nova oportunidade de arbitragem detectada', '{"event_id": 1003, "profit": 4.1}', NULL, '2025-05-29 14:30:00'),
(4, 'INFO', 'auth', 'Usuário logado no sistema', '{"username": "apostador1"}', 2, '2025-05-29 14:00:00'),
(5, 'INFO', 'auth', 'Usuário logado no sistema', '{"username": "apostador2"}', 3, '2025-05-29 14:15:00'),
(6, 'INFO', 'betting', 'Aposta realizada', '{"bet_id": 1, "amount": 476.19}', 2, '2025-05-29 14:05:00');

-- ============================================================================
-- 📊 ESTATÍSTICAS DE PERFORMANCE
-- ============================================================================

INSERT OR REPLACE INTO performance_stats (id, metric_name, metric_value, metric_unit, recorded_at, details_json) VALUES
(1, 'arbitrage_detection_time', 150.5, 'ms', '2025-05-29 14:00:00', '{"event_count": 7, "bookmaker_count": 6}'),
(2, 'odds_update_frequency', 30.0, 'seconds', '2025-05-29 14:00:00', '{"total_selections": 30}'),
(3, 'active_opportunities', 3.0, 'count', '2025-05-29 14:30:00', '{"total_profit": 9.0}'),
(4, 'user_engagement', 4.0, 'active_users', '2025-05-29 14:30:00', '{"total_bets": 6}'),
(5, 'system_uptime', 99.9, 'percentage', '2025-05-29 14:30:00', '{"downtime_minutes": 1.44}');

-- ============================================================================
-- 🔧 ATUALIZAR ESTATÍSTICAS
-- ============================================================================

ANALYZE;
