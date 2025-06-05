-- POPULAÇÃO INICIAL PostgreSQL - SISTEMA DE SUREBETS
-- Adaptado de SQLite para PostgreSQL

-- Bookmakers
INSERT INTO bookmakers (id, name, api_url, rate_limit, timeout_seconds, is_active)
VALUES
(1, 'Bet365', 'https://api.bet365.com', 120, 15, TRUE),
(2, 'Betfair', 'https://api.betfair.com', 100, 12, TRUE),
(3, 'Pinnacle', 'https://api.pinnacle.com', 150, 10, TRUE),
(4, 'William Hill', 'https://api.williamhill.com', 90, 20, TRUE),
(5, 'Betway', 'https://api.betway.com', 110, 15, TRUE),
(6, 'Unibet', 'https://api.unibet.com', 80, 18, TRUE)
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;

-- Sports
INSERT INTO sports (id, name, slug, is_active) VALUES
(1, 'Futebol', 'football', TRUE),
(2, 'Basquete', 'basketball', TRUE),
(3, 'Tênis', 'tennis', TRUE),
(4, 'Vôlei', 'volleyball', TRUE),
(5, 'E-Sports', 'esports', TRUE)
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;

-- Leagues
INSERT INTO leagues (id, sport_id, name, slug, country, is_active) VALUES
(1, 1, 'Campeonato Brasileiro Série A', 'brasileirao-a', 'Brasil', TRUE),
(2, 1, 'Premier League', 'premier-league', 'Inglaterra', TRUE),
(3, 1, 'La Liga', 'la-liga', 'Espanha', TRUE),
(4, 1, 'Champions League', 'champions-league', 'Europa', TRUE),
(5, 2, 'NBA', 'nba', 'Estados Unidos', TRUE),
(6, 3, 'ATP Tour', 'atp-tour', 'Mundial', TRUE),
(7, 5, 'League of Legends World Championship', 'lol-worlds', 'Mundial', TRUE)
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;

-- Markets
INSERT INTO markets (id, name, slug, description, is_active) VALUES
(1, 'Resultado Final', '1x2', 'Vitória mandante, empate ou vitória visitante', TRUE),
(2, 'Total de Gols', 'total-goals', 'Acima ou abaixo de um número de gols', TRUE),
(3, 'Ambas Marcam', 'both-teams-score', 'Se ambos os times marcarão gols', TRUE),
(4, 'Handicap Asiático', 'asian-handicap', 'Handicap com vantagem/desvantagem', TRUE),
(5, 'Primeiro Tempo', 'first-half', 'Resultado do primeiro tempo', TRUE)
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;

-- O restante dos inserts (events, selections, arbitrage_opportunities, users, bets, odds_history, system_logs, performance_stats) deve seguir o mesmo padrão, usando ON CONFLICT (id) DO UPDATE SET ... para garantir compatibilidade.
-- Para campos JSON, use ::jsonb.
-- Para datas, mantenha o formato 'YYYY-MM-DD HH:MI:SS'.

-- Exemplo para events:
-- INSERT INTO events (id, external_id, league_id, home_team, away_team, start_time, status, is_active)
-- VALUES (...)
-- ON CONFLICT (id) DO UPDATE SET home_team=EXCLUDED.home_team;

-- Complete os demais inserts conforme necessário.
