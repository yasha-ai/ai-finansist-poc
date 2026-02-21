const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./data.db');

db.serialize(() => {
  // Users table
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      telegram_id INTEGER UNIQUE NOT NULL,
      username TEXT,
      first_name TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Certificates table
  db.run(`
    CREATE TABLE IF NOT EXISTS certificates (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      price INTEGER NOT NULL,
      ai_prompt TEXT,
      image_url TEXT,
      active BOOLEAN DEFAULT 1
    )
  `);

  // Purchases table
  db.run(`
    CREATE TABLE IF NOT EXISTS purchases (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      certificate_id INTEGER NOT NULL,
      amount INTEGER NOT NULL,
      status TEXT DEFAULT 'pending',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (certificate_id) REFERENCES certificates(id)
    )
  `);

  // Raffles table
  db.run(`
    CREATE TABLE IF NOT EXISTS raffles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      certificate_id INTEGER NOT NULL,
      winner_id INTEGER,
      status TEXT DEFAULT 'active',
      ends_at DATETIME NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (certificate_id) REFERENCES certificates(id),
      FOREIGN KEY (winner_id) REFERENCES users(id)
    )
  `);

  // Seed sample certificates
  db.run(`
    INSERT OR IGNORE INTO certificates (id, title, description, price, ai_prompt) VALUES
    (1, 'Базовая финансовая грамотность', 'Консультация с AI по основам личных финансов', 1000, 'Ты финансовый советник. Помоги пользователю с базовыми вопросами бюджета и накоплений.'),
    (2, 'Инвестиции для начинающих', 'AI-советник по инвестициям и пассивному доходу', 2500, 'Ты эксперт по инвестициям. Объясни пользователю основы инвестирования простым языком.'),
    (3, 'Налоговая оптимизация', 'Консультация по налогам и легальной оптимизации', 5000, 'Ты налоговый консультант. Помоги пользователю разобраться с налогами и вычетами.')
  `);

  console.log('✅ Database initialized with sample data');
});

db.close();
