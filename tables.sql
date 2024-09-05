CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    flight_number TEXT,
    destination TEXT,
    departure_date TEXT,
    class TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
