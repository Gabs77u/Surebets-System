-- Tabela de eventos
CREATE TABLE IF NOT EXISTS events (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL
);

-- Tabela de seleções (odds)
CREATE TABLE IF NOT EXISTS selections (
    id BIGINT PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    odds FLOAT NOT NULL,
    bookmaker TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Tabela de surebets
CREATE TABLE IF NOT EXISTS surebets (
    id BIGINT PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    market TEXT NOT NULL,
    profit_percent FLOAT NOT NULL,
    arbitrage_index FLOAT NOT NULL,
    detected_at TIMESTAMP NOT NULL
);

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabela de apostas realizadas
CREATE TABLE IF NOT EXISTS bets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    selection_id BIGINT NOT NULL REFERENCES selections(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    placed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'pending'
);

-- Histórico de odds (para auditoria e análise)
CREATE TABLE IF NOT EXISTS odds_history (
    id BIGSERIAL PRIMARY KEY,
    selection_id BIGINT NOT NULL REFERENCES selections(id) ON DELETE CASCADE,
    old_odds FLOAT NOT NULL,
    new_odds FLOAT NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Logs de detecção de surebets
CREATE TABLE IF NOT EXISTS surebet_logs (
    id BIGSERIAL PRIMARY KEY,
    surebet_id BIGINT NOT NULL REFERENCES surebets(id) ON DELETE CASCADE,
    detected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    details TEXT
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_selections_event_id ON selections(event_id);
CREATE INDEX IF NOT EXISTS idx_surebets_event_id ON surebets(event_id);
