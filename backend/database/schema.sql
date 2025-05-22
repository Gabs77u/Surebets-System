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

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_selections_event_id ON selections(event_id);
CREATE INDEX IF NOT EXISTS idx_surebets_event_id ON surebets(event_id);
