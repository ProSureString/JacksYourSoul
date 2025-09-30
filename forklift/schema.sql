-- souls go her or sumshit

CREATE TABLE IF NOT EXISTS souls (
    discord_id TEXT PRIMARY KEY,
    discord_name TEXT NOT NULL,
    email TEXT,
    access_token TEXT NOT NULL, --yoinkity
    refresh_token TEXT, --yoinkity^2
    balance INTEGER DEFAULT 0,
    guilds_data TEXT, -- JSON blobbity of theri servs lol :3
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT --yummy or som shish
);

CREATE TABLE IF NOT EXISTS pending_registrations (
    code TEXT PRIMARY KEY,
    discord_id TEXT, --pending for referal, maybe
    discord_name TEXT,
    referrer_id TEXT, -- who referred them, if anyone
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL, --  blackjack, referral, admin_gift, etc
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    metadata TEXT, -- nya :3
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    FOREIGN KEY (discord_id) REFERENCES souls(discord_id)
);

CREATE TABLE IF NOT EXISTS blackjack_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    bet INTEGER NOT NULL,
    player_hand TEXT NOT NULL,
    dealer_hand TEXT NOT NULL,
    result TEXT NOT NULL, -- win, lose, push
    winnings INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES souls(discord_id)
);


--index for speeeddyyyyy :3 br vrom
CREATE INDEX IF NOT EXISTS idx_souls_balance ON souls(balance DESC);
CREATE INDEX IF NOT EXISTS idx_souls_created ON souls(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_registrations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_discord ON transactions(discord_id, created_at DESC);