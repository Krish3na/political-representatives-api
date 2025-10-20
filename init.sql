-- Initialize the legislators database
-- Create the database if it doesn't exist (PostgreSQL compatible)
SELECT 'CREATE DATABASE legislators_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'legislators_db')\gexec

-- Create the legislators table
CREATE TABLE IF NOT EXISTS legislators (
    govtrack_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birthday DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    type VARCHAR(10) NOT NULL,
    state VARCHAR(2) NOT NULL,
    district VARCHAR(10),
    party VARCHAR(50) NOT NULL,
    url VARCHAR(500),
    notes TEXT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_legislators_state ON legislators(state);
CREATE INDEX IF NOT EXISTS idx_legislators_party ON legislators(party);
CREATE INDEX IF NOT EXISTS idx_legislators_type ON legislators(type);
CREATE INDEX IF NOT EXISTS idx_legislators_birthday ON legislators(birthday);
