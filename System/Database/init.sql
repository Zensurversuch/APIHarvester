CREATE TABLE IF NOT EXISTS users (
    userID SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    lastName TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastLogin TIMESTAMP NOT NULL
);

INSERT INTO users (email, password, lastName, firstName, lastLogin) VALUES
('user1@example.com', 'password123', 'Doe', 'John', CURRENT_TIMESTAMP),
('user2@example.com', 'securepass', 'Smith', 'Jane', CURRENT_TIMESTAMP);