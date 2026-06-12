DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS user_level_enum;


CREATE TYPE user_level_enum AS ENUM ('basic', 'admin');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    hashed_password VARCHAR(1024),
    email VARCHAR(320) NOT NULL UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(32),
    whatsapp_number VARCHAR(32),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    user_group user_level_enum NOT NULL DEFAULT 'basic',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);