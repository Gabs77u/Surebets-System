-- ============================================================================
-- 🗄️ SCHEMA SQLite - SISTEMA DE SUREBETS
-- ============================================================================
-- Schema otimizado para SQLite com melhor performance e funcionalidades

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;

-- ============================================================================
-- 📊 TABELAS PRINCIPAIS
-- ============================================================================

-- Tabela de casas de apostas (bookmakers)
CREATE TABLE IF NOT EXISTS bookmakers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT,
    rate_limit INTEGER DEFAULT 100,
    timeout_seconds INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de esportes
CREATE TABLE IF NOT EXISTS sports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de ligas/campeonatos
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    country TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
    UNIQUE(sport_id, slug)
);

-- Tabela de eventos esportivos
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT,
    league_id INTEGER NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    status TEXT DEFAULT 'upcoming',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE
);

-- Tabela de mercados de apostas
CREATE TABLE IF NOT EXISTS markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de seleções/odds
CREATE TABLE IF NOT EXISTS selections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    bookmaker_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    odds REAL NOT NULL CHECK (odds > 0),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE,
    FOREIGN KEY (bookmaker_id) REFERENCES bookmakers(id) ON DELETE CASCADE,
    UNIQUE(event_id, market_id, bookmaker_id, name)
);

-- ============================================================================
-- 🎯 TABELAS DE ARBITRAGEM
-- ============================================================================

-- Tabela de oportunidades de arbitragem
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    profit_percentage REAL NOT NULL CHECK (profit_percentage >= 0),
    total_implied_probability REAL NOT NULL,
    stakes_json TEXT NOT NULL, -- JSON com distribuição de apostas
    selections_json TEXT NOT NULL, -- JSON com seleções e odds
    is_active BOOLEAN DEFAULT 1,
    expires_at DATETIME,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notified_at DATETIME,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE
);

-- Histórico de arbitragem para análise
CREATE TABLE IF NOT EXISTS arbitrage_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,
    profit_percentage REAL NOT NULL,
    total_implied_probability REAL NOT NULL,
    stakes_json TEXT NOT NULL,
    selections_json TEXT NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities(id) ON DELETE CASCADE
);

-- ============================================================================
-- 👥 TABELAS DE USUÁRIOS
-- ============================================================================

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    email_verified BOOLEAN DEFAULT 0,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões de usuário
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- 💰 TABELAS DE APOSTAS
-- ============================================================================

-- Tabela de apostas realizadas
CREATE TABLE IF NOT EXISTS bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    opportunity_id INTEGER,
    selection_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    expected_return REAL,
    actual_return REAL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'placed', 'won', 'lost', 'cancelled', 'voided')),
    placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    settled_at DATETIME,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities(id) ON DELETE SET NULL,
    FOREIGN KEY (selection_id) REFERENCES selections(id) ON DELETE CASCADE
);

-- ============================================================================
-- 📊 TABELAS DE MONITORAMENTO
-- ============================================================================

-- Histórico de mudanças de odds
CREATE TABLE IF NOT EXISTS odds_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    selection_id INTEGER NOT NULL,
    old_odds REAL NOT NULL,
    new_odds REAL NOT NULL,
    change_percentage REAL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (selection_id) REFERENCES selections(id) ON DELETE CASCADE
);

-- Logs de sistema
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    user_id INTEGER,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Estatísticas de performance
CREATE TABLE IF NOT EXISTS performance_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    details_json TEXT
);

-- ============================================================================
-- 🔍 ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Índices principais
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

-- ============================================================================
-- 🛠️ TRIGGERS PARA AUTOMATIZAÇÃO
-- ============================================================================

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER IF NOT EXISTS update_events_updated_at
    AFTER UPDATE ON events
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE events SET updated_at = datetime('now', 'localtime', '+0.001 seconds') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_selections_updated_at
    AFTER UPDATE ON selections
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE selections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger para registrar mudanças de odds
CREATE TRIGGER IF NOT EXISTS log_odds_changes
    AFTER UPDATE OF odds ON selections
    FOR EACH ROW
    WHEN NEW.odds != OLD.odds
BEGIN
    INSERT INTO odds_history (selection_id, old_odds, new_odds, change_percentage)
    VALUES (NEW.id, OLD.odds, NEW.odds, ((NEW.odds - OLD.odds) / OLD.odds) * 100);
END;

-- ============================================================================
-- 📋 VIEWS PARA RELATÓRIOS
-- ============================================================================

-- View para oportunidades ativas com detalhes
CREATE VIEW IF NOT EXISTS v_active_opportunities AS
SELECT 
    ao.id,
    ao.profit_percentage,
    ao.detected_at,
    e.home_team,
    e.away_team,
    e.start_time,
    s.name as sport_name,
    l.name as league_name,
    m.name as market_name,
    COUNT(DISTINCT JSON_EXTRACT(ao.selections_json, '$[*].bookmaker_id')) as bookmaker_count
FROM arbitrage_opportunities ao
JOIN events e ON ao.event_id = e.id
JOIN leagues l ON e.league_id = l.id
JOIN sports s ON l.sport_id = s.id
JOIN markets m ON ao.market_id = m.id
WHERE ao.is_active = 1 
    AND e.is_active = 1
    AND (ao.expires_at IS NULL OR ao.expires_at > CURRENT_TIMESTAMP)
GROUP BY ao.id
ORDER BY ao.profit_percentage DESC;

-- View para estatísticas de usuários
CREATE VIEW IF NOT EXISTS v_user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(b.id) as total_bets,
    SUM(CASE WHEN b.status = 'won' THEN b.actual_return - b.amount ELSE 0 END) as total_profit,
    AVG(CASE WHEN b.status IN ('won', 'lost') THEN b.actual_return - b.amount END) as avg_profit,
    MAX(b.placed_at) as last_bet_date
FROM users u
LEFT JOIN bets b ON u.id = b.user_id
GROUP BY u.id, u.username;

-- View para performance de bookmakers
CREATE VIEW IF NOT EXISTS v_bookmaker_stats AS
SELECT 
    b.id,
    b.name,
    COUNT(s.id) as total_selections,
    AVG(s.odds) as avg_odds,
    COUNT(CASE WHEN s.is_active = 1 THEN 1 END) as active_selections,
    MAX(s.updated_at) as last_update
FROM bookmakers b
LEFT JOIN selections s ON b.id = s.bookmaker_id
WHERE b.is_active = 1
GROUP BY b.id, b.name;

-- ============================================================================
-- 🔧 CONFIGURAÇÕES FINAIS
-- ============================================================================

-- Atualizar estatísticas de query planner
ANALYZE;
