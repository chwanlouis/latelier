CREATE TYPE user_level_enum AS ENUM ('BASIC', 'ADMIN');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(1024),
    email VARCHAR(320) NOT NULL UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(32),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    user_level user_level_enum NOT NULL DEFAULT 'BASIC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);