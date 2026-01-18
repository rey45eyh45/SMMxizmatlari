import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import initSqlJs from 'sql.js';
import fs from 'fs';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Bot config for sending receipts
const BOT_TOKEN = process.env.BOT_TOKEN || '';
const ADMIN_ID = process.env.ADMIN_ID || '';

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
    
    // Orders table
    db.run(`
      CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id TEXT,
        service_name TEXT,
        link TEXT,
        quantity INTEGER,
        price REAL,
        status TEXT DEFAULT 'pending',
        api_order_id TEXT,
        start_count INTEGER,
        remains INTEGER,
        created_at TEXT
      )
    `);
    
    // Premium table
    db.run(`
      CREATE TABLE IF NOT EXISTS premium_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        months INTEGER,
        price REAL,
        status TEXT DEFAULT 'pending',
        activated_at TEXT,
        expires_at TEXT,
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

// Get user orders
app.get('/api/orders/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  try {
    const result = db.exec('SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC', [userId]);
    
    const orders = [];
    if (result.length && result[0].values.length) {
      const columns = ['id', 'user_id', 'service_id', 'service_name', 'link', 'quantity', 'price', 'status', 'api_order_id', 'start_count', 'remains', 'created_at'];
      result[0].values.forEach(row => {
        const order = {};
        row.forEach((val, idx) => {
          order[columns[idx]] = val;
        });
        orders.push(order);
      });
    }
    
    res.json({ success: true, orders });
  } catch (err) {
    console.error('Error getting orders:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Get premium plans (static) - MUST BE BEFORE :userId route
app.get('/api/premium/plans', (req, res) => {
  const plans = [
    { months: 1, price: 45000, original_price: 55000, discount_percent: 18, popular: false, best_value: false },
    { months: 3, price: 120000, original_price: 165000, discount_percent: 27, popular: true, best_value: false },
    { months: 6, price: 210000, original_price: 330000, discount_percent: 36, popular: false, best_value: true },
    { months: 12, price: 380000, original_price: 660000, discount_percent: 42, popular: false, best_value: false },
  ];
  res.json({ success: true, plans });
});

// Get premium status
app.get('/api/premium/:userId', (req, res) => {
  const userId = parseInt(req.params.userId);
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  try {
    // Get active premium subscription
    const now = new Date().toISOString();
    const result = db.exec(
      `SELECT * FROM premium_subscriptions 
       WHERE user_id = ? AND status = 'active' AND expires_at > ? 
       ORDER BY expires_at DESC LIMIT 1`, 
      [userId, now]
    );
    
    let premium = null;
    if (result.length && result[0].values.length) {
      const columns = ['id', 'user_id', 'months', 'price', 'status', 'activated_at', 'expires_at', 'created_at', 'admin_note'];
      const row = result[0].values[0];
      premium = {};
      row.forEach((val, idx) => {
        premium[columns[idx]] = val;
      });
    }
    
    if (premium) {
      const expiresAt = new Date(premium.expires_at);
      const daysLeft = Math.ceil((expiresAt - new Date()) / (1000 * 60 * 60 * 24));
      
      res.json({
        success: true,
        is_premium: true,
        days_left: daysLeft,
        expires_at: premium.expires_at,
        activated_at: premium.activated_at
      });
    } else {
      res.json({
        success: true,
        is_premium: false,
        days_left: 0
      });
    }
  } catch (err) {
    console.error('Error getting premium status:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Request premium (sends to admin)
app.post('/api/premium/request', (req, res) => {
  const { user_id, months, price } = req.body;
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  if (!user_id || !months || !price) {
    return res.status(400).json({ success: false, error: 'Missing required fields' });
  }
  
  try {
    const now = new Date().toISOString();
    db.run(`
      INSERT INTO premium_subscriptions (user_id, months, price, status, created_at)
      VALUES (?, ?, ?, 'pending', ?)
    `, [user_id, months, price, now]);
    
    saveDb();
    
    res.json({ success: true, message: 'Premium request submitted' });
  } catch (err) {
    console.error('Error creating premium request:', err);
    res.status(500).json({ success: false, error: 'Database error' });
  }
});

// Get payment methods
app.get('/api/payment/methods', (req, res) => {
  const methods = [
    { id: 'card', name: 'Karta orqali', card_number: '9860 1901 0198 2212', card_holder: 'IDEAL SMM', min_amount: 5000 },
  ];
  res.json({ success: true, methods });
});

// Create payment request
app.post('/api/payment/create', (req, res) => {
  const { user_id, amount, method } = req.body;
  
  console.log('Creating payment:', { user_id, amount, method });
  
  if (!db) {
    return res.status(500).json({ success: false, error: 'Database not available' });
  }
  
  if (!user_id || !amount || !method) {
    return res.status(400).json({ success: false, error: 'Missing required fields' });
  }
  
  if (amount < 5000) {
    return res.status(400).json({ success: false, error: 'Minimum amount is 5000' });
  }
  
  try {
    const now = new Date().toISOString();
    db.run(`
      INSERT INTO payments (user_id, amount, method, status, created_at)
      VALUES (?, ?, ?, 'pending', ?)
    `, [user_id, amount, method, now]);
    
    saveDb();
    
    // Get the created payment ID - sql.js specific way
    const result = db.exec('SELECT MAX(id) as id FROM payments WHERE user_id = ?', [user_id]);
    let paymentId = 0;
    
    if (result.length && result[0].values.length) {
      paymentId = result[0].values[0][0];
    }
    
    console.log('Payment created with ID:', paymentId);
    
    res.json({ 
      success: true, 
      message: 'Payment request created',
      payment_id: paymentId
    });
  } catch (err) {
    console.error('Error creating payment:', err);
    res.status(500).json({ success: false, error: 'Database error: ' + err.message });
  }
});

// Upload receipt image and send to admin via Telegram Bot
import multer from 'multer';
import FormData from 'form-data';

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB max
});

// Error handler for multer
const uploadMiddleware = (req, res, next) => {
  upload.single('receipt')(req, res, (err) => {
    if (err) {
      console.error('Multer error:', err);
      return res.status(400).json({ success: false, error: 'File upload error: ' + err.message });
    }
    next();
  });
};

app.post('/api/payment/upload-receipt', uploadMiddleware, async (req, res) => {
  console.log('Upload receipt endpoint called');
  
  try {
    const { payment_id, user_id, amount, full_name } = req.body;
    const file = req.file;
    
    console.log('Request body:', { payment_id, user_id, amount, full_name });
    console.log('File:', file ? { name: file.originalname, size: file.size } : 'No file');
    
    if (!file) {
      return res.status(400).json({ success: false, error: 'No file uploaded' });
    }
    
    if (!BOT_TOKEN) {
      console.error('BOT_TOKEN not configured');
      return res.status(500).json({ success: false, error: 'Bot token missing' });
    }
    
    if (!ADMIN_ID) {
      console.error('ADMIN_ID not configured');
      return res.status(500).json({ success: false, error: 'Admin ID missing' });
    }
    
    // Send photo to admin via Telegram Bot API
    const caption = `📸 <b>Mini App To'lov Cheki!</b>\n\n` +
      `👤 Foydalanuvchi: ${full_name || 'Noma\'lum'}\n` +
      `🆔 ID: ${user_id}\n` +
      `📝 To'lov ID: #${payment_id}\n` +
      `💰 Summa: ${parseInt(amount || 0).toLocaleString()} so'm\n` +
      `📍 Usul: Karta orqali\n\n` +
      `⏳ Tekshirishni kutmoqda...`;
    
    // Add inline keyboard for admin
    const keyboard = JSON.stringify({
      inline_keyboard: [
        [{ text: '✅ Tasdiqlash', callback_data: `miniapp_approve_${user_id}_${payment_id}` }],
        [{ text: '❌ Rad etish', callback_data: `miniapp_reject_${user_id}_${payment_id}` }]
      ]
    });
    
    // Use form-data package for multipart upload
    const formData = new FormData();
    formData.append('chat_id', ADMIN_ID);
    formData.append('caption', caption);
    formData.append('parse_mode', 'HTML');
    formData.append('reply_markup', keyboard);
    formData.append('photo', file.buffer, {
      filename: file.originalname || 'receipt.jpg',
      contentType: file.mimetype
    });
    
    console.log('Sending to Telegram via axios...');
    
    const response = await axios.post(
      `https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto`,
      formData,
      {
        headers: {
          ...formData.getHeaders()
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      }
    );
    
    console.log('Telegram response:', response.data);
    
    if (response.data.ok) {
      // Update payment status
      if (db) {
        db.run('UPDATE payments SET status = ? WHERE id = ?', ['receipt_sent', payment_id]);
        saveDb();
      }
      
      res.json({ success: true, message: 'Receipt sent to admin' });
    } else {
      console.error('Telegram API error:', response.data);
      res.status(500).json({ success: false, error: response.data.description || 'Failed to send receipt' });
    }
  } catch (err) {
    console.error('Error uploading receipt:', err.response?.data || err.message || err);
    res.status(500).json({ success: false, error: 'Server error: ' + (err.response?.data?.description || err.message || 'Unknown error') });
  }
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Global error:', err);
  res.status(500).json({ success: false, error: 'Server error: ' + (err.message || 'Unknown error') });
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
    console.log('BOT_TOKEN:', BOT_TOKEN ? 'Set (' + BOT_TOKEN.substring(0, 10) + '...)' : 'NOT SET');
    console.log('ADMIN_ID:', ADMIN_ID || 'NOT SET');
  });
});