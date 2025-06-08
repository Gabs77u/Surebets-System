-- SCHEMA PostgreSQL - SISTEMA DE SUREBETS

-- Este arquivo é usado para criar o schema do banco de dados PostgreSQL em ambiente de produção e testes.



-- Tabelas principais

CREATE TABLE IF NOT EXISTS bookmakers (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,

    api_url TEXT,

    rate_limit INTEGER DEFAULT 100,

    timeout_seconds INTEGER DEFAULT 10,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS sports (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,

    slug TEXT NOT NULL UNIQUE,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS leagues (

    id SERIAL PRIMARY KEY,

    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,

    name TEXT NOT NULL,

    slug TEXT NOT NULL,

    country TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sport_id, slug)

);



CREATE TABLE IF NOT EXISTS events (

    id SERIAL PRIMARY KEY,

    external_id TEXT,

    league_id INTEGER NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,

    home_team TEXT NOT NULL,

    away_team TEXT NOT NULL,

    start_time TIMESTAMP NOT NULL,

    status TEXT DEFAULT 'upcoming',

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS markets (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,

    slug TEXT NOT NULL UNIQUE,

    description TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS selections (

    id SERIAL PRIMARY KEY,

    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,

    bookmaker_id INTEGER NOT NULL REFERENCES bookmakers(id) ON DELETE CASCADE,

    name TEXT NOT NULL,

    odds REAL NOT NULL CHECK (odds > 0),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(event_id, market_id, bookmaker_id, name)

);



CREATE TABLE IF NOT EXISTS arbitrage_opportunities (

    id SERIAL PRIMARY KEY,

    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,

    profit_percentage REAL NOT NULL CHECK (profit_percentage >= 0),

    total_implied_probability REAL NOT NULL,

    stakes_json JSONB NOT NULL,

    selections_json JSONB NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    expires_at TIMESTAMP,

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    notified_at TIMESTAMP

);



CREATE TABLE IF NOT EXISTS arbitrage_history (

    id SERIAL PRIMARY KEY,

    opportunity_id INTEGER NOT NULL REFERENCES arbitrage_opportunities(id) ON DELETE CASCADE,

    profit_percentage REAL NOT NULL,

    total_implied_probability REAL NOT NULL,

    stakes_json JSONB NOT NULL,

    selections_json JSONB NOT NULL,

    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS users (

    id SERIAL PRIMARY KEY,

    username TEXT NOT NULL UNIQUE,

    email TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    first_name TEXT,

    last_name TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    is_admin BOOLEAN DEFAULT FALSE,

    email_verified BOOLEAN DEFAULT FALSE,

    last_login TIMESTAMP,

    role TEXT DEFAULT 'user',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS user_sessions (

    id TEXT PRIMARY KEY,

    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    ip_address TEXT,

    user_agent TEXT,

    expires_at TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS bets (

    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    opportunity_id INTEGER REFERENCES arbitrage_opportunities(id) ON DELETE SET NULL,

    selection_id INTEGER NOT NULL REFERENCES selections(id) ON DELETE CASCADE,

    amount REAL NOT NULL CHECK (amount > 0),

    expected_return REAL,

    actual_return REAL,

    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'placed', 'won', 'lost', 'cancelled', 'voided')),

    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    settled_at TIMESTAMP,

    notes TEXT

);



CREATE TABLE IF NOT EXISTS odds_history (

    id SERIAL PRIMARY KEY,

    selection_id INTEGER NOT NULL REFERENCES selections(id) ON DELETE CASCADE,

    old_odds REAL NOT NULL,

    new_odds REAL NOT NULL,

    change_percentage REAL,

    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS system_logs (

    id SERIAL PRIMARY KEY,

    level TEXT NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),

    module TEXT NOT NULL,

    message TEXT NOT NULL,

    details JSONB,

    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    ip_address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS performance_stats (

    id SERIAL PRIMARY KEY,

    metric_name TEXT NOT NULL,

    metric_value REAL NOT NULL,

    metric_unit TEXT,

    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    details_json JSONB

);



-- Índices

CREATE INDEX IF NOT EXISTS idx_events_league_start_time ON events(league_id, start_time);

CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);

CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);

CREATE INDEX IF NOT EXISTS idx_selections_event_market ON selections(event_id, market_id);

CREATE INDEX IF NOT EXISTS idx_selections_bookmaker ON selections(bookmaker_id);

CREATE INDEX IF NOT EXISTS idx_selections_odds ON selections(odds);

CREATE INDEX IF NOT EXISTS idx_selections_active ON selections(is_active);

CREATE INDEX IF NOT EXISTS idx_arbitrage_event_market ON arbitrage_opportunities(event_id, market_id);

CREATE INDEX IF NOT EXISTS idx_arbitrage_profit ON arbitrage_opportunities(profit_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_arbitrage_detected ON arbitrage_opportunities(detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_arbitrage_active ON arbitrage_opportunities(is_active);

CREATE INDEX IF NOT EXISTS idx_bets_user ON bets(user_id);

CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status);

CREATE INDEX IF NOT EXISTS idx_bets_placed_at ON bets(placed_at DESC);

CREATE INDEX IF NOT EXISTS idx_odds_history_selection ON odds_history(selection_id);

CREATE INDEX IF NOT EXISTS idx_odds_history_changed_at ON odds_history(changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);

CREATE INDEX IF NOT EXISTS idx_system_logs_module ON system_logs(module);

CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);



-- Views e triggers devem ser adaptadas manualmente conforme necessidade.

-- Triggers de update automático de updated_at podem ser feitas com funções PL/pgSQL.

-- Views com JSON devem usar funções nativas do PostgreSQL (jsonb_array_elements, etc).

