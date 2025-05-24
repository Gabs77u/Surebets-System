-- População inicial para o banco de dados do Surebets System

-- Eventos esportivos
INSERT INTO events (id, name, market, start_time) VALUES
  (1001, 'Flamengo x Palmeiras', '1X2', '2025-05-25 16:00:00'),
  (1002, 'Corinthians x Santos', '1X2', '2025-05-25 18:00:00'),
  (1003, 'São Paulo x Grêmio', '1X2', '2025-05-26 20:00:00'),
  (1004, 'Chelsea x Arsenal', '1X2', '2025-05-27 15:00:00'),
  (1005, 'Real Madrid x Barcelona', '1X2', '2025-05-28 21:00:00');

-- Seleções (odds)
INSERT INTO selections (id, event_id, name, odds, bookmaker, timestamp) VALUES
  (2001, 1001, 'Flamengo', 2.10, 'Bet365', '2025-05-24 12:00:00'),
  (2002, 1001, 'Empate', 3.30, 'Betfair', '2025-05-24 12:00:00'),
  (2003, 1001, 'Palmeiras', 3.50, 'Pinnacle', '2025-05-24 12:00:00'),
  (2004, 1002, 'Corinthians', 2.50, 'Bet365', '2025-05-24 12:00:00'),
  (2005, 1002, 'Empate', 3.10, 'Super Odds', '2025-05-24 12:00:00'),
  (2006, 1002, 'Santos', 2.90, 'Betfair', '2025-05-24 12:00:00'),
  (2007, 1003, 'São Paulo', 1.95, 'Bet365', '2025-05-24 12:00:00'),
  (2008, 1003, 'Empate', 3.40, 'Pinnacle', '2025-05-24 12:00:00'),
  (2009, 1003, 'Grêmio', 4.00, 'Betfair', '2025-05-24 12:00:00'),
  (2010, 1004, 'Chelsea', 2.80, 'Super Odds', '2025-05-24 12:00:00'),
  (2011, 1004, 'Empate', 3.20, 'Bet365', '2025-05-24 12:00:00'),
  (2012, 1004, 'Arsenal', 2.60, 'Betfair', '2025-05-24 12:00:00'),
  (2013, 1005, 'Real Madrid', 2.40, 'Bet365', '2025-05-24 12:00:00'),
  (2014, 1005, 'Empate', 3.50, 'Pinnacle', '2025-05-24 12:00:00'),
  (2015, 1005, 'Barcelona', 2.80, 'Betfair', '2025-05-24 12:00:00');

-- Surebets detectadas
INSERT INTO surebets (id, event_id, market, profit_percent, arbitrage_index, detected_at) VALUES
  (3001, 1001, '1X2', 3.2, 0.968, '2025-05-24 13:00:00'),
  (3002, 1002, '1X2', 2.7, 0.973, '2025-05-24 13:05:00'),
  (3003, 1003, '1X2', 4.1, 0.961, '2025-05-24 13:10:00'),
  (3004, 1004, '1X2', 2.9, 0.971, '2025-05-24 13:15:00'),
  (3005, 1005, '1X2', 3.5, 0.965, '2025-05-24 13:20:00');

-- Usuários
INSERT INTO users (username, email, password_hash, created_at) VALUES
  ('admin', 'admin@surebets.com', 'hash_admin', '2025-05-24 10:00:00'),
  ('apostador1', 'apostador1@email.com', 'hash_apostador1', '2025-05-24 11:00:00'),
  ('apostador2', 'apostador2@email.com', 'hash_apostador2', '2025-05-24 12:00:00');

-- Apostas realizadas
INSERT INTO bets (user_id, selection_id, amount, placed_at, status) VALUES
  (1, 2001, 100.00, '2025-05-24 13:00:00', 'pending'),
  (2, 2004, 50.00, '2025-05-24 13:05:00', 'pending'),
  (3, 2013, 75.00, '2025-05-24 13:10:00', 'pending');

-- Histórico de odds
INSERT INTO odds_history (selection_id, old_odds, new_odds, changed_at) VALUES
  (2001, 2.00, 2.10, '2025-05-24 12:30:00'),
  (2004, 2.40, 2.50, '2025-05-24 12:40:00'),
  (2013, 2.30, 2.40, '2025-05-24 12:50:00');

-- Logs de detecção de surebets
INSERT INTO surebet_logs (surebet_id, detected_at, details) VALUES
  (3001, '2025-05-24 13:00:00', 'Surebet detectada entre Flamengo e Palmeiras'),
  (3002, '2025-05-24 13:05:00', 'Surebet detectada entre Corinthians e Santos'),
  (3003, '2025-05-24 13:10:00', 'Surebet detectada entre São Paulo e Grêmio');
