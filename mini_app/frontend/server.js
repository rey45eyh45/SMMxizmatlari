import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import initSqlJs from 'sql.js';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// JSON parsing
app.use(express.json());

// Database - SQLite with sql.js
const DATABASE_PATH = process.env.DATABASE_PATH || './smm_bot.db';
let db = null;

// Initialize database
async function initDb() {
  try {
    const SQL = await initSqlJs();
    
    // Try to load existing database
    if (fs.existsSync(DATABASE_PATH)) {
      const fileBuffer = fs.readFileSync(DATABASE_PATH);
      db = new SQL.Database(fileBuffer);
      console.log('Loaded existing database');
    } else {
      db = new SQL.Database();
      console.log('Created new database');
    }
    
    // Create table if not exists
    db.run(`
      CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance REAL DEFAULT 0,
        referral_id INTEGER,
        referral_count INTEGER DEFAULT 0,
        referral_earnings REAL DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT,
        phone TEXT
      )
    `);
    
    // Payments table
    db.run(`
      CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        method TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        admin_note TEXT
      )
    `);
    
    saveDb();
    return true;
  } catch (err) {
    console.error('Database error:', err);
    return false;
  }
}

// Save database to file
function saveDb() {
  if (db) {
    try {
      const data = db.export();
      const buffer = Buffer.from(data);
      fs.writeFileSync(DATABASE_PATH, buffer);
    } catch (err) {
      console.error('Error saving database:', err);
    }
  }
}

// Helper to get user from query result
function rowToUser(row) {
  if (!row || row.length === 0) return null;
  const columns = ['user_id', 'username', 'full_name', 'balance', 'referral_id', 'referral_count', 'referral_earnings', 'is_banned', 'created_at', 'phone'];
  const user = {};
  row.forEach((val, idx) => {
    user[columns[idx]] = val;
  });
  return user;
}

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get user by ID
app.get('/api/user/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  try {
    const result = db.exec('SELECT * FROM users WHERE user_id = ?', [userId]);
    
    if (!result.length || !result[0].values.length) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    const user = rowToUser(result[0].values[0]);
    
    res.json({
      success: true,
      user: {
        user_id: user.user_id,
        username: user.username,
        full_name: user.full_name,
        balance: user.balance || 0,
        referral_count: user.referral_count || 0,
        referral_earnings: user.referral_earnings || 0,
        is_banned: !!user.is_banned,
        created_at: user.created_at || ''
      }
    });
  } catch (err) {
    console.error('Error getting user:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Create or get user
app.post('/api/user/create', (req, res) => {
  const { user_id, username, full_name } = req.body;
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  if (!user_id) {
    return res.status(400).json({ success: false, error: 'user_id required' });
  }
  
  try {
    // Check if user exists
    let result = db.exec('SELECT * FROM users WHERE user_id = ?', [user_id]);
    let user = result.length && result[0].values.length ? rowToUser(result[0].values[0]) : null;
    
    if (!user) {
      // Create new user
      const now = new Date().toISOString();
      db.run(`
        INSERT INTO users (user_id, username, full_name, balance, created_at)
        VALUES (?, ?, ?, 0, ?)
      `, [user_id, username || '', full_name || '', now]);
      
      saveDb();
      
      result = db.exec('SELECT * FROM users WHERE user_id = ?', [user_id]);
      user = result.length && result[0].values.length ? rowToUser(result[0].values[0]) : null;
    }
    
    res.json({
      success: true,
      user: {
        user_id: user.user_id,
        username: user.username,
        full_name: user.full_name,
        balance: user.balance || 0,
        referral_count: user.referral_count || 0,
        referral_earnings: user.referral_earnings || 0,
        is_banned: !!user.is_banned,
        created_at: user.created_at || ''
      }
    });
  } catch (err) {
    console.error('Error creating user:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Auth endpoint
app.post('/api/auth', (req, res) => {
  const { init_data } = req.body;
  
  // For now, just parse user from init_data
  // In production, validate with BOT_TOKEN
  try {
    if (!init_data) {
      return res.status(400).json({ success: false, error: 'init_data required' });
    }
    
    const params = new URLSearchParams(init_data);
    const userStr = params.get('user');
    
    if (!userStr) {
      return res.status(400).json({ success: false, error: 'No user in init_data' });
    }
    
    const tgUser = JSON.parse(decodeURIComponent(userStr));
    
    if (!db) {
      return res.status(500).json({ success: false, error: 'Database not available' });
    }
    
    // Get or create user
    let result = db.exec('SELECT * FROM users WHERE user_id = ?', [tgUser.id]);
    let user = result.length && result[0].values.length ? rowToUser(result[0].values[0]) : null;
    
    if (!user) {
      const now = new Date().toISOString();
      const fullName = `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim();
      db.run(`
        INSERT INTO users (user_id, username, full_name, balance, created_at)
        VALUES (?, ?, ?, 0, ?)
      `, [tgUser.id, tgUser.username || '', fullName, now]);
      
      saveDb();
      
      result = db.exec('SELECT * FROM users WHERE user_id = ?', [tgUser.id]);
      user = result.length && result[0].values.length ? rowToUser(result[0].values[0]) : null;
    }
    
    res.json({
      success: true,
      user: {
        user_id: user.user_id,
        username: user.username,
        full_name: user.full_name,
        balance: user.balance || 0,
        referral_count: user.referral_count || 0,
        referral_earnings: user.referral_earnings || 0,
        is_banned: !!user.is_banned,
        created_at: user.created_at || ''
      }
    });
  } catch (err) {
    console.error('Auth error:', err);
    res.status(500).json({ success: false, error: 'Auth failed' });
  }
});

// Get user payments
app.get('/api/payments/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  try {
    const result = db.exec('SELECT * FROM payments WHERE user_id = ? ORDER BY id DESC', [userId]);
    
    const payments = [];
    if (result.length && result[0].values.length) {
      const columns = ['id', 'user_id', 'amount', 'method', 'status', 'created_at', 'admin_note'];
      result[0].values.forEach(row => {
        const payment = {};
        row.forEach((val, idx) => {
          payment[columns[idx]] = val;
        });
        payments.push(payment);
      });
    }
    
    res.json({ success: true, payments });
  } catch (err) {
    console.error('Error getting payments:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Serve static files
app.use(express.static(join(__dirname, 'dist')));

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

// Initialize database and start server
initDb().then(() => {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});