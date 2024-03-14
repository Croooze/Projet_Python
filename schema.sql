CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL CHECK(length(password) <= 255)
);
INSERT INTO users (username, password) VALUES ('username', 'password')
