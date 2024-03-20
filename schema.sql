CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL CHECK(LENGTH(password) <= 255)
);
INSERT INTO users (username, password) VALUES ('username', 'password');

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

DELETE FROM notes WHERE id = ?;