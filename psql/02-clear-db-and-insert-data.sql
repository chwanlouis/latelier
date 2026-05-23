-- Clear the database
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- Insert sample data
--INSERT INTO users (username, password_hash, email, first_name, last_name, phone, user_level)
--VALUES
--('john_doe', 'hashed_password_1', 'john.doe@example.com', 'John', 'Doe', '1234567890', 'BASIC'),
--('admin_user', 'hashed_password_2', 'admin@example.com', 'Admin', 'User', '0987654321', 'ADMIN');