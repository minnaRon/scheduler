CREATE TABLE users (id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role INTEGER DEFAULT 2,
                    contact_info TEXT,
                    founded TIMESTAMP
);
CREATE TABLE group_info (id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    admin_info TEXT,
                    password TEXT NOT NULL,
                    founded TIMESTAMP, 
                    founder_id INTEGER
);
CREATE TABLE events (id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    min_participants INTEGER,
                    max_participants INTEGER,
                    event_level INTEGER DEFAULT 0
);
CREATE TABLE entries (id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users,
                            event_id INTEGER REFERENCES events,
                            date DATE,
                            start_time TIME, 
                            finish_time TIME, 
                            active INTEGER DEFAULT 1, 
                            extra_participants INTEGER DEFAULT 0,
                            weekly INTEGER
);
CREATE TABLE messages (id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users, 
                        entries_id INTEGER REFERENCES entries,
                        event_id INTEGER REFERENCES events,
                        content TEXT, 
                        sent_at TIMESTAMP
);     
CREATE TABLE users_in_events (id SERIAL PRIMARY KEY,
                                event_id INTEGER REFERENCES events,
                                user_id INTEGER REFERENCES users,
                                user_level INTEGER DEFAULT 0,
                                role INTEGER DEFAULT 2
);
CREATE TABLE friends (id SERIAL PRIMARY KEY,
                        user_id1 INTEGER REFERENCES users, 
                        user_id2 INTEGER REFERENCES users, 
                        active INTEGER DEFAULT 0
);
