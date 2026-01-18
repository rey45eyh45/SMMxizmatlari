import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import sqlite3 from 'better-sqlite3';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// JSON parsing
app.use(express.json());

// Database - SQLite (shared with bot via volume or separate)
const DATABASE_PATH = process.env.DATABASE_PATH || './smm_bot.db';

// Initialize database
function initDb() {
  try {
    const db = sqlite3(DATABASE_PATH);
    db.exec(`
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
    return db;
  } catch (err) {
    console.error('Database error:', err);
    return null;
  }
}

const db = initDb();

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
    const user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(userId);
    
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
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
    let user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(user_id);
    
    if (!user) {
      // Create new user
      const now = new Date().toISOString();
      db.prepare(`
        INSERT INTO users (user_id, username, full_name, balance, created_at)
        VALUES (?, ?, ?, 0, ?)
      `).run(user_id, username || '', full_name || '', now);
      
      user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(user_id);
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
    let user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(tgUser.id);
    
    if (!user) {
      const now = new Date().toISOString();
      const fullName = `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim();
      db.prepare(`
        INSERT INTO users (user_id, username, full_name, balance, created_at)
        VALUES (?, ?, ?, 0, ?)
      `).run(tgUser.id, tgUser.username || '', fullName, now);
      
      user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(tgUser.id);
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

// Serve static files
app.use(express.static(join(__dirname, 'dist')));

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
