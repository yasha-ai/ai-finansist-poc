require('dotenv').config();
const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const OpenAI = require('openai');

const app = express();
const db = new sqlite3.Database('./data.db');
const openai = process.env.OPENAI_API_KEY 
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) 
  : null;

app.use(cors());
app.use(express.json());

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get certificates
app.get('/api/certificates', (req, res) => {
  db.all('SELECT * FROM certificates WHERE active = 1', [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json({ certificates: rows });
  });
});

// Get certificate by ID
app.get('/api/certificates/:id', (req, res) => {
  db.get('SELECT * FROM certificates WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: 'Certificate not found' });
    }
    res.json({ certificate: row });
  });
});

// Create purchase
app.post('/api/purchases', (req, res) => {
  const { telegram_id, certificate_id, amount } = req.body;

  // Get or create user
  db.get('SELECT * FROM users WHERE telegram_id = ?', [telegram_id], (err, user) => {
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    db.run(
      'INSERT INTO purchases (user_id, certificate_id, amount, status) VALUES (?, ?, ?, ?)',
      [user.id, certificate_id, amount, 'pending'],
      function(err) {
        if (err) {
          return res.status(500).json({ error: err.message });
        }
        res.json({ 
          purchase_id: this.lastID,
          status: 'pending',
          message: 'Purchase created. Payment integration coming soon!' 
        });
      }
    );
  });
});

// AI Chat endpoint
app.post('/api/ai/chat', async (req, res) => {
  const { certificate_id, message } = req.body;

  if (!openai) {
    return res.json({ 
      response: 'AI-консультант временно недоступен. В полной версии здесь будет персональный финансовый советник на базе GPT/GigaChat.',
      certificate: 'demo'
    });
  }

  // Get certificate prompt
  db.get('SELECT * FROM certificates WHERE id = ?', [certificate_id], async (err, cert) => {
    if (!cert) {
      return res.status(404).json({ error: 'Certificate not found' });
    }

    try {
      const completion = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: cert.ai_prompt },
          { role: 'user', content: message }
        ],
        max_tokens: 500
      });

      res.json({ 
        response: completion.choices[0].message.content,
        certificate: cert.title
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
});

// Get user purchases
app.get('/api/users/:telegram_id/purchases', (req, res) => {
  db.get('SELECT * FROM users WHERE telegram_id = ?', [req.params.telegram_id], (err, user) => {
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    db.all(
      `SELECT p.*, c.title as certificate_title 
       FROM purchases p 
       JOIN certificates c ON p.certificate_id = c.id 
       WHERE p.user_id = ? 
       ORDER BY p.created_at DESC`,
      [user.id],
      (err, rows) => {
        if (err) {
          return res.status(500).json({ error: err.message });
        }
        res.json({ purchases: rows });
      }
    );
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 API server running on port ${PORT}`);
});
