import sqlite3
from config import DATABASE_NAME
from datetime import datetime

def init_db():
    """Ma'lumotlar bazasini yaratish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute('''
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
    ''')
    
    # phone ustuni mavjud bo'lmasa qo'shish
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    except:
        pass  # Ustun allaqachon mavjud
    
    # Buyurtmalar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT,
            platform TEXT,
            link TEXT,
            quantity INTEGER,
            price REAL,
            status TEXT DEFAULT 'kutilmoqda',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # To'lovlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            status TEXT DEFAULT 'kutilmoqda',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ==================== INDEXLAR (TEZLIK UCHUN!) ====================
    # Buyurtmalar - user_id bo'yicha qidirish tezlashadi
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
    
    # Buyurtmalar - status bo'yicha qidirish (kutilmoqda, bajarildi, ...)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
    
    # Buyurtmalar - sana bo'yicha qidirish (statistika uchun)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)')
    
    # Buyurtmalar - user_id + status kombinatsiyasi (eng ko'p ishlatiladi)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_status ON orders(user_id, status)')
    
    # To'lovlar - user_id bo'yicha
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)')
    
    # To'lovlar - status bo'yicha
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)')
    
    # Foydalanuvchilar - is_banned bo'yicha
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_banned ON users(is_banned)')
    
    # Foydalanuvchilar - referral_id bo'yicha
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_referral ON users(referral_id)')
    
    # ==================== PREMIUM OBUNA JADVALI ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_type TEXT,
            months INTEGER,
            price REAL,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Premium obuna index
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_premium_user ON premium_subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_premium_status ON premium_subscriptions(status)')
    
    # ==================== PREMIUM SO'ROVLAR JADVALI ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone TEXT,
            months INTEGER,
            price REAL,
            status TEXT DEFAULT 'pending',
            admin_message_id INTEGER,
            created_at TEXT,
            processed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_premium_requests_status ON premium_requests(status)')
    
    # ==================== SOZLAMALAR JADVALI ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    ''')
    
    # Standart sozlamalarni qo'shish (agar yo'q bo'lsa)
    default_settings = [
        ('usd_rate', '12900'),
        ('rub_rate', '140'),
        ('markup_percent', '20'),
        ('card_number', '9860 1234 5678 9012'),
        ('card_holder', 'ADMIN'),
        ('min_deposit', '5000'),
        ('referral_bonus', '500'),
        ('bot_active', '1')
    ]
    
    for key, value in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, updated_at) 
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()


# ==================== SOZLAMALAR FUNKSIYALARI ====================

def get_setting(key, default=None):
    """Sozlamani olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default


def set_setting(key, value):
    """Sozlamani o'zgartirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value, updated_at) 
        VALUES (?, ?, ?)
    ''', (key, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_all_settings():
    """Barcha sozlamalarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    results = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in results}


def add_user(user_id, username, full_name, referral_id=None):
    """Yangi foydalanuvchi qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO users (user_id, username, full_name, referral_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, referral_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Referal bonusi - sozlamalardan olish
        if referral_id:
            # Bonus miqdorini settings dan olish
            bonus = int(get_setting('referral_bonus', '500'))
            
            # Referal sonini oshirish
            cursor.execute('''
                UPDATE users SET referral_count = referral_count + 1 
                WHERE user_id = ?
            ''', (referral_id,))
            
            # Referal egasiga bonus
            cursor.execute('''
                UPDATE users SET balance = balance + ?, referral_earnings = referral_earnings + ?
                WHERE user_id = ?
            ''', (bonus, bonus, referral_id,))
            
            # Yangi foydalanuvchiga ham bonus
            cursor.execute('''
                UPDATE users SET balance = ?
                WHERE user_id = ?
            ''', (bonus, user_id,))
        
        conn.commit()
        
        # Bonus berilganini qaytarish
        bonus_given = referral_id is not None
        conn.close()
        return bonus_given
    
    conn.close()
    return False

def get_user(user_id):
    """Foydalanuvchi ma'lumotlarini olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_phone(phone):
    """Telefon raqam bo'yicha foydalanuvchini topish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Telefon raqamni normalizatsiya qilish
    phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    cursor.execute("SELECT * FROM users WHERE phone = ? OR phone = ?", (phone, '+' + phone))
    user = cursor.fetchone()
    conn.close()
    return user


def update_user_phone(user_id, phone):
    """Foydalanuvchi telefon raqamini yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Telefon raqamni normalizatsiya qilish
    phone = phone.replace(' ', '').replace('-', '')
    if not phone.startswith('+'):
        phone = '+' + phone
    cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
    conn.commit()
    conn.close()


def update_balance(user_id, amount):
    """Balansni yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET balance = balance + ? WHERE user_id = ?
    ''', (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    """Balansni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_order(user_id, service_type, link, quantity, price):
    """Yangi buyurtma qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, service_type, link, quantity, price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, service_type, link, quantity, price, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

def get_user_orders(user_id):
    """Foydalanuvchi buyurtmalarini olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
    ''', (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def add_payment(user_id, amount, method):
    """Yangi to'lov qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (user_id, amount, method, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, amount, method, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()
    return payment_id

def get_referral_stats(user_id):
    """Referal statistikasini olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT referral_count, referral_earnings FROM users WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 0)

def get_all_users():
    """Barcha foydalanuvchilarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

def update_order_status(order_id, status):
    """Buyurtma holatini yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def update_order_api_id(order_id, api_order_id, panel_name=None):
    """Buyurtmaga API order ID va panel nomi qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # api_order_id ustuni mavjud bo'lmasa qo'shamiz
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN api_order_id INTEGER")
    except:
        pass
    # panel_name ustuni mavjud bo'lmasa qo'shamiz
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN panel_name TEXT")
    except:
        pass
    
    if panel_name:
        cursor.execute("UPDATE orders SET api_order_id = ?, panel_name = ? WHERE id = ?", (api_order_id, panel_name, order_id))
    else:
        cursor.execute("UPDATE orders SET api_order_id = ? WHERE id = ?", (api_order_id, order_id))
    conn.commit()
    conn.close()

def get_pending_orders():
    """Kutilayotgan buyurtmalarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # panel_name ustunini tekshirish
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN panel_name TEXT")
    except:
        pass
    cursor.execute("SELECT id, api_order_id, user_id, panel_name FROM orders WHERE status IN ('pending', 'processing', 'In progress') AND api_order_id IS NOT NULL")
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_orders_by_status(status):
    """Status bo'yicha buyurtmalarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, service_type, quantity, price, status, created_at FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT 20", (status,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_user_orders_admin(user_id):
    """Admin uchun foydalanuvchi buyurtmalari"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, service_type, quantity, price, status, created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_user_payments_admin(user_id):
    """Admin uchun foydalanuvchi to'lovlari"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, method, status, created_at FROM payments WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_payments_by_status(status):
    """Status bo'yicha to'lovlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, amount, method, status, created_at FROM payments WHERE status = ? ORDER BY created_at DESC LIMIT 20", (status,))
    payments = cursor.fetchall()
    conn.close()
    return payments


def approve_payment(payment_id):
    """To'lovni tasdiqlash va balansga qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, amount, status FROM payments WHERE id = ?", (payment_id,))
    payment = cursor.fetchone()
    
    if not payment:
        conn.close()
        return False, "To'lov topilmadi"
    
    user_id, amount, status = payment
    
    if status == 'approved':
        conn.close()
        return False, "Bu to'lov allaqachon tasdiqlangan"
    
    # To'lovni tasdiqlash
    cursor.execute("UPDATE payments SET status = 'approved' WHERE id = ?", (payment_id,))
    # Balansga qo'shish
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    
    conn.commit()
    conn.close()
    return True, user_id


def reject_payment(payment_id):
    """To'lovni rad etish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
    cursor.execute("SELECT user_id FROM payments WHERE id = ?", (payment_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else None


def cancel_order_and_refund(order_id):
    """Buyurtmani bekor qilish va pul qaytarish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, price, status FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return False, "Buyurtma topilmadi", None
    
    user_id, price, status = order
    
    if status == 'canceled':
        conn.close()
        return False, "Bu buyurtma allaqachon bekor qilingan", None
    
    # Buyurtmani bekor qilish
    cursor.execute("UPDATE orders SET status = 'canceled' WHERE id = ?", (order_id,))
    # Pulni qaytarish
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (price, user_id))
    
    conn.commit()
    conn.close()
    return True, price, user_id


def get_banned_users():
    """Bloklangan foydalanuvchilarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, created_at FROM users WHERE is_banned = 1")
    users = cursor.fetchall()
    conn.close()
    return users


def get_users_with_balance():
    """Balansi bor foydalanuvchilar"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE balance > 0")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]


def get_users_with_orders():
    """Buyurtma bergan foydalanuvchilar"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM orders")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]


def get_top_orders_users(limit=15):
    """Eng ko'p buyurtma bergan foydalanuvchilar"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.username, u.full_name, COUNT(o.id) as order_count, SUM(o.price) as total_spent
        FROM users u
        LEFT JOIN orders o ON u.user_id = o.user_id
        GROUP BY u.user_id
        ORDER BY order_count DESC
        LIMIT ?
    """, (limit,))
    users = cursor.fetchall()
    conn.close()
    return users


# ==================== PREMIUM OBUNA FUNKSIYALARI ====================

def add_premium_subscription(user_id, plan_type, months, price):
    """Premium obuna qo'shish"""
    from datetime import timedelta
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    end_date = (now + timedelta(days=months * 30)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO premium_subscriptions (user_id, plan_type, months, price, start_date, end_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
    ''', (user_id, plan_type, months, price, start_date, end_date, start_date))
    
    conn.commit()
    subscription_id = cursor.lastrowid
    conn.close()
    return subscription_id


def get_user_premium(user_id):
    """Foydalanuvchining aktiv premium obunasini olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, plan_type, months, price, start_date, end_date, status
        FROM premium_subscriptions
        WHERE user_id = ? AND status = 'active' AND end_date > datetime('now')
        ORDER BY end_date DESC
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def check_premium_status(user_id):
    """Foydalanuvchi premium ekanligini tekshirish"""
    premium = get_user_premium(user_id)
    return premium is not None


def get_premium_remaining_days(user_id):
    """Premium kunlar qolganini hisoblash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT end_date FROM premium_subscriptions
        WHERE user_id = ? AND status = 'active' AND end_date > datetime('now')
        ORDER BY end_date DESC
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        from datetime import datetime as dt
        end_date = dt.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        remaining = (end_date - dt.now()).days
        return max(0, remaining)
    return 0


def get_all_premium_users():
    """Barcha premium foydalanuvchilarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT user_id FROM premium_subscriptions
        WHERE status = 'active' AND end_date > datetime('now')
    ''')
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]


def get_premium_stats():
    """Premium statistikasi"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Jami premium sotilgan
    cursor.execute("SELECT COUNT(*) FROM premium_subscriptions")
    total_sold = cursor.fetchone()[0]
    
    # Aktiv premium
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) FROM premium_subscriptions
        WHERE status = 'active' AND end_date > datetime('now')
    ''')
    active_count = cursor.fetchone()[0]
    
    # Jami daromad
    cursor.execute("SELECT SUM(price) FROM premium_subscriptions")
    total_revenue = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        'total_sold': total_sold,
        'active_count': active_count,
        'total_revenue': total_revenue
    }


# ==================== PREMIUM SO'ROVLAR FUNKSIYALARI ====================

def add_premium_request(user_id, phone, months, price):
    """Premium so'rov qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO premium_requests (user_id, phone, months, price, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    ''', (user_id, phone, months, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id


def get_premium_request(request_id):
    """Premium so'rovni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM premium_requests WHERE id = ?", (request_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_premium_request_status(request_id, status, admin_message_id=None):
    """Premium so'rov holatini yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if admin_message_id:
        cursor.execute('''
            UPDATE premium_requests SET status = ?, admin_message_id = ?, processed_at = ?
            WHERE id = ?
        ''', (status, admin_message_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id))
    else:
        cursor.execute('''
            UPDATE premium_requests SET status = ?, processed_at = ?
            WHERE id = ?
        ''', (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id))
    
    conn.commit()
    conn.close()


def get_pending_premium_requests():
    """Kutilayotgan premium so'rovlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pr.*, u.full_name, u.username 
        FROM premium_requests pr
        LEFT JOIN users u ON pr.user_id = u.user_id
        WHERE pr.status = 'pending'
        ORDER BY pr.created_at DESC
    ''')
    results = cursor.fetchall()
    conn.close()
    return results
