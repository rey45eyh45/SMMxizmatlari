# SMM Mini App

Telegram Mini App for SMM Services Bot - built with modern technologies.

## 📋 Features

- 🛒 Order SMM services (Telegram, Instagram, YouTube, TikTok)
- 📱 Virtual phone numbers for SMS verification
- 💳 Balance management and payments
- 👥 Referral system
- ⭐ Telegram Premium subscriptions
- 📊 Order tracking

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Database (shared with main bot)
- **Pydantic v2** - Data validation
- **HTTPX** - Async HTTP client
- **Python-Jose** - JWT tokens

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Server state
- **Zustand** - Client state
- **Framer Motion** - Animations
- **React Router DOM** - Routing

## 🚀 Setup

### Backend

1. Navigate to backend folder:
```bash
cd mini_app/backend
```

2. Create virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///../../smm_bot.db
JWT_SECRET=your-secret-key-here
PEAKERR_API_KEY=your_peakerr_key
SMMMAIN_API_KEY=your_smmmain_key
VAK_SMS_API_KEY=your_vak_key
FIVESIM_API_KEY=your_5sim_key
SMSPVA_API_KEY=your_smspva_key
```

5. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to frontend folder:
```bash
cd mini_app/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
```

4. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 📁 Project Structure

```
mini_app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Database operations
│   │   ├── models.py          # Pydantic schemas
│   │   ├── auth.py            # Telegram auth & JWT
│   │   ├── services.py        # Services configuration
│   │   ├── smm_api.py         # SMM panel API clients
│   │   ├── sms_api.py         # SMS service API clients
│   │   ├── main.py            # FastAPI application
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── user.py
│   │       ├── services.py
│   │       ├── orders.py
│   │       ├── payments.py
│   │       └── sms.py
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/        # UI components
    │   ├── pages/             # Page components
    │   ├── hooks/             # Custom hooks
    │   ├── lib/               # API client
    │   ├── store/             # Zustand store
    │   ├── types/             # TypeScript types
    │   ├── App.tsx
    │   ├── main.tsx
    │   └── index.css
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.ts
    └── tsconfig.json
```

## 🔗 Telegram Integration

### Adding Mini App to Bot

1. Go to @BotFather
2. Select your bot
3. Click "Bot Settings" → "Menu Button"
4. Set the URL to your hosted Mini App

### WebApp Data Validation

The backend validates Telegram WebApp `initData` to ensure requests come from Telegram:

```python
from app.auth import verify_telegram_webapp
user_data = verify_telegram_webapp(init_data, bot_token)
```

## 📝 API Endpoints

### Authentication
- `POST /api/auth/telegram` - Authenticate with Telegram initData

### User
- `GET /api/user/me` - Get current user
- `GET /api/user/balance` - Get balance
- `GET /api/user/referral` - Get referral stats

### Services
- `GET /api/services/platforms` - List platforms
- `GET /api/services/platform/{id}` - Get platform services
- `GET /api/services/service/{id}` - Get service details

### Orders
- `POST /api/orders/create` - Create order
- `GET /api/orders/my` - Get my orders
- `GET /api/orders/{id}/status` - Get order status

### Payments
- `GET /api/payments/methods` - Get payment methods
- `POST /api/payments/create` - Create payment request
- `GET /api/payments/my` - Get my payments

### SMS
- `GET /api/sms/platforms` - List SMS platforms
- `GET /api/sms/countries` - List countries
- `GET /api/sms/prices/{platform}/{country}` - Get prices
- `POST /api/sms/buy` - Buy number

## 🚢 Deployment

### Railway

1. Create new project on Railway
2. Add PostgreSQL (or use SQLite)
3. Set environment variables
4. Deploy backend from `/mini_app/backend`
5. Deploy frontend from `/mini_app/frontend`
6. Update Mini App URL in BotFather

### Vercel (Frontend only)

```bash
cd mini_app/frontend
npm run build
vercel deploy
```

## 📄 License

MIT License - feel free to use this code for your projects.

## 🤝 Support

For questions and support, contact the bot owner.
