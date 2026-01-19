import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegram } from '../hooks/useTelegram';
import { adminAPI } from '../lib/api';

// ==================== TYPES ====================
interface DashboardData {
  users: { total: number; today: number };
  orders: { total: number; today: number; pending: number; processing: number; completed: number; canceled: number };
  revenue: { total: number; today: number };
  payments: { pending: number; total_deposits: number };
  weekly_stats: { date: string; orders: number; revenue: number }[];
}

interface User {
  user_id: number;
  username: string;
  full_name: string;
  balance: number;
  created_at: string;
  is_blocked: boolean;
  phone_number: string;
  orders_count: number;
  total_spent: number;
}

interface Order {
  id: number;
  user_id: number;
  service: string;
  link: string;
  quantity: number;
  price: number;
  status: string;
  created_at: string;
  username: string;
  full_name: string;
}

interface Payment {
  id: number;
  user_id: number;
  amount: number;
  method: string;
  status: string;
  created_at: string;
  username: string;
  full_name: string;
}

type TabType = 'dashboard' | 'users' | 'orders' | 'payments' | 'settings';

// ==================== MAIN COMPONENT ====================
const Admin: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useTelegram();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  
  // Pagination & filters
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Modals
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [balanceAmount, setBalanceAmount] = useState('');
  
  const adminId = user?.id || 0;
  const adminHash = 'dev_hash';

  // ==================== API CALLS ====================
  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getDashboard(adminId, adminHash);
      if (response.success) setDashboard(response.data);
    } catch (err) {
      setError('Dashboard yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [adminId]);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getUsers(adminId, adminHash, currentPage, 15, searchQuery);
      if (response.success) {
        setUsers(response.data.users);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError('Foydalanuvchilar yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [adminId, currentPage, searchQuery]);

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getOrders(adminId, adminHash, currentPage, 15, statusFilter);
      if (response.success) {
        setOrders(response.data.orders);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError('Buyurtmalar yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [adminId, currentPage, statusFilter]);

  const fetchPayments = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getPayments(adminId, adminHash, currentPage, 15, statusFilter);
      if (response.success) {
        setPayments(response.data.payments);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError("To'lovlar yuklanmadi");
    } finally {
      setLoading(false);
    }
  }, [adminId, currentPage, statusFilter]);

  // Initial & tab change
  useEffect(() => {
    setCurrentPage(1);
    setStatusFilter('');
    switch (activeTab) {
      case 'dashboard': fetchDashboard(); break;
      case 'users': fetchUsers(); break;
      case 'orders': fetchOrders(); break;
      case 'payments': fetchPayments(); break;
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'users') fetchUsers();
    else if (activeTab === 'orders') fetchOrders();
    else if (activeTab === 'payments') fetchPayments();
  }, [currentPage, searchQuery, statusFilter]);

  // ==================== HANDLERS ====================
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    setSidebarOpen(false);
  };

  const handleBalanceChange = async () => {
    if (!selectedUser || !balanceAmount) return;
    try {
      await adminAPI.changeBalance(adminId, adminHash, selectedUser.user_id, parseFloat(balanceAmount), 'Admin panel');
      setSelectedUser(null);
      setBalanceAmount('');
      fetchUsers();
      fetchDashboard();
    } catch (err) {
      setError("Balans o'zgartirilmadi");
    }
  };

  const handleApprovePayment = async (id: number) => {
    try {
      await adminAPI.approvePayment(adminId, adminHash, id);
      fetchPayments();
      fetchDashboard();
    } catch (err) {
      setError("To'lov tasdiqlanmadi");
    }
  };

  const handleRejectPayment = async (id: number) => {
    try {
      await adminAPI.rejectPayment(adminId, adminHash, id);
      fetchPayments();
    } catch (err) {
      setError("Xatolik yuz berdi");
    }
  };

  // ==================== HELPERS ====================
  const formatNumber = (n: number) => new Intl.NumberFormat('uz-UZ').format(n);
  const formatDate = (d: string) => {
    if (!d) return '-';
    return new Date(d).toLocaleDateString('uz-UZ', {
      day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit'
    });
  };

  const menuItems = [
    { id: 'dashboard' as TabType, icon: '📊', label: 'Dashboard', badge: null },
    { id: 'users' as TabType, icon: '👥', label: 'Foydalanuvchilar', badge: dashboard?.users.total },
    { id: 'orders' as TabType, icon: '📦', label: 'Buyurtmalar', badge: dashboard?.orders.pending },
    { id: 'payments' as TabType, icon: '💳', label: "To'lovlar", badge: dashboard?.payments.pending },
    { id: 'settings' as TabType, icon: '⚙️', label: 'Sozlamalar', badge: null },
  ];

  // ==================== COMPONENTS ====================
  const StatusBadge = ({ status }: { status: string }) => {
    const styles: Record<string, string> = {
      pending: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      completed: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      canceled: 'bg-red-500/20 text-red-400 border-red-500/30',
      approved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      rejected: 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    const labels: Record<string, string> = {
      pending: '⏳ Kutilmoqda',
      processing: '🔄 Jarayonda',
      completed: '✅ Bajarildi',
      canceled: '❌ Bekor',
      approved: '✅ Tasdiqlangan',
      rejected: '❌ Rad etilgan',
    };
    return (
      <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${styles[status] || 'bg-gray-500/20 text-gray-400'}`}>
        {labels[status] || status}
      </span>
    );
  };

  const StatCard = ({ icon, label, value, subValue, color }: any) => (
    <div className={`bg-gradient-to-br ${color} rounded-2xl p-4 border border-white/10`}>
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        {subValue && <span className="text-xs text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded-full">+{subValue}</span>}
      </div>
      <p className="text-2xl font-bold text-white mt-2">{formatNumber(value)}</p>
      <p className="text-white/60 text-sm">{label}</p>
    </div>
  );

  const Pagination = () => totalPages > 1 && (
    <div className="flex items-center justify-center gap-2 mt-4">
      <button
        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
        disabled={currentPage === 1}
        className="w-10 h-10 rounded-xl bg-white/5 text-white disabled:opacity-30 hover:bg-white/10 transition-all"
      >
        ←
      </button>
      <div className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm">
        {currentPage} / {totalPages}
      </div>
      <button
        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
        disabled={currentPage === totalPages}
        className="w-10 h-10 rounded-xl bg-white/5 text-white disabled:opacity-30 hover:bg-white/10 transition-all"
      >
        →
      </button>
    </div>
  );

  // ==================== RENDER ====================
  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full w-72 bg-[#111111] border-r border-white/10 z-50 transform transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {/* Sidebar Header */}
        <div className="p-5 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <span className="text-lg">🔐</span>
              </div>
              <div>
                <h2 className="font-bold text-white">Admin Panel</h2>
                <p className="text-xs text-white/50">SMM Xizmatlari</p>
              </div>
            </div>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-white/70 hover:bg-white/10"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="p-3 space-y-1">
          {menuItems.map(item => (
            <button
              key={item.id}
              onClick={() => handleTabChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === item.id 
                  ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white border border-purple-500/30' 
                  : 'text-white/70 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="flex-1 text-left font-medium">{item.label}</span>
              {item.badge && item.badge > 0 && (
                <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-purple-500 text-white">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
          <button 
            onClick={() => navigate('/')}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/50 hover:bg-white/5 hover:text-white transition-all"
          >
            <span>🏠</span>
            <span>Asosiy sahifaga</span>
          </button>
        </div>
      </aside>

      {/* Header */}
      <header className="sticky top-0 z-30 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/10">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            {/* Hamburger Menu */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="w-10 h-10 rounded-xl bg-white/5 flex flex-col items-center justify-center gap-1.5 hover:bg-white/10 transition-all"
            >
              <span className="w-5 h-0.5 bg-white rounded-full"></span>
              <span className="w-5 h-0.5 bg-white rounded-full"></span>
              <span className="w-5 h-0.5 bg-white rounded-full"></span>
            </button>
            <div>
              <h1 className="font-bold text-white">{menuItems.find(m => m.id === activeTab)?.label}</h1>
              <p className="text-xs text-white/50">{menuItems.find(m => m.id === activeTab)?.icon} Boshqaruv</p>
            </div>
          </div>
          
          {/* Header Actions */}
          <div className="flex items-center gap-2">
            {dashboard?.payments.pending ? (
              <div className="px-3 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
                <span className="text-amber-400 text-sm font-medium">{dashboard.payments.pending}</span>
              </div>
            ) : null}
            <button 
              onClick={() => { fetchDashboard(); if(activeTab !== 'dashboard') { activeTab === 'users' ? fetchUsers() : activeTab === 'orders' ? fetchOrders() : fetchPayments(); }}}
              className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-white hover:bg-white/10 transition-all"
            >
              🔄
            </button>
          </div>
        </div>
      </header>

      {/* Error Toast */}
      {error && (
        <div className="fixed top-20 left-4 right-4 z-50 bg-red-500/90 backdrop-blur text-white px-4 py-3 rounded-xl flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-white/80 hover:text-white">✕</button>
        </div>
      )}

      {/* Main Content */}
      <main className="p-4 pb-24">
        {/* Loading */}
        {loading && !dashboard && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin"></div>
            <p className="text-white/50 mt-4">Yuklanmoqda...</p>
          </div>
        )}

        {/* Dashboard */}
        {activeTab === 'dashboard' && dashboard && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
              <StatCard icon="👥" label="Foydalanuvchilar" value={dashboard.users.total} subValue={dashboard.users.today} color="from-blue-600/20 to-blue-900/20" />
              <StatCard icon="📦" label="Buyurtmalar" value={dashboard.orders.total} subValue={dashboard.orders.today} color="from-emerald-600/20 to-emerald-900/20" />
              <StatCard icon="💰" label="Daromad" value={dashboard.revenue.total} subValue={null} color="from-amber-600/20 to-amber-900/20" />
              <StatCard icon="💳" label="Kutilayotgan" value={dashboard.payments.pending} subValue={null} color="from-purple-600/20 to-purple-900/20" />
            </div>

            {/* Order Status */}
            <div className="bg-[#111] rounded-2xl border border-white/10 p-4">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <span>📊</span> Buyurtmalar holati
              </h3>
              <div className="space-y-3">
                {[
                  { label: 'Kutilmoqda', value: dashboard.orders.pending, color: 'bg-amber-500', icon: '⏳' },
                  { label: 'Jarayonda', value: dashboard.orders.processing, color: 'bg-blue-500', icon: '🔄' },
                  { label: 'Bajarildi', value: dashboard.orders.completed, color: 'bg-emerald-500', icon: '✅' },
                  { label: 'Bekor qilingan', value: dashboard.orders.canceled, color: 'bg-red-500', icon: '❌' },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-3">
                    <span className="text-lg">{item.icon}</span>
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-white/70">{item.label}</span>
                        <span className="text-white font-medium">{formatNumber(item.value)}</span>
                      </div>
                      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${item.color} rounded-full transition-all`}
                          style={{ width: `${Math.min(100, (item.value / Math.max(dashboard.orders.total, 1)) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Weekly Chart */}
            <div className="bg-[#111] rounded-2xl border border-white/10 p-4">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <span>📈</span> Oxirgi 7 kun
              </h3>
              <div className="flex items-end gap-2 h-32">
                {dashboard.weekly_stats.slice(0, 7).reverse().map((day, i) => {
                  const maxOrders = Math.max(...dashboard.weekly_stats.map(d => d.orders || 1));
                  const height = (day.orders / maxOrders) * 100;
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2">
                      <div className="w-full bg-white/5 rounded-lg overflow-hidden flex-1 flex items-end">
                        <div 
                          className="w-full bg-gradient-to-t from-purple-500 to-blue-500 rounded-lg transition-all"
                          style={{ height: `${Math.max(height, 5)}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-white/50">{day.date.slice(8)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Users */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            {/* Search */}
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30">🔍</span>
              <input
                type="text"
                placeholder="ID, username yoki ism qidirish..."
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                className="w-full bg-[#111] border border-white/10 rounded-xl pl-12 pr-4 py-3 text-white placeholder:text-white/30 focus:border-purple-500/50 focus:outline-none"
              />
            </div>

            {/* Users List */}
            {!loading && (
              <div className="space-y-2">
                {users.map(u => (
                  <div 
                    key={u.user_id}
                    onClick={() => setSelectedUser(u)}
                    className="bg-[#111] border border-white/10 rounded-xl p-4 hover:border-purple-500/30 cursor-pointer transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center text-lg">
                        {u.full_name?.charAt(0) || '👤'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">{u.full_name || 'Noma\'lum'}</p>
                        <p className="text-sm text-white/50">@{u.username || u.user_id}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-emerald-400">{formatNumber(u.balance)}</p>
                        <p className="text-xs text-white/50">{u.orders_count} buyurtma</p>
                      </div>
                    </div>
                    {u.is_blocked && (
                      <div className="mt-2 px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-lg inline-block">
                        🚫 Bloklangan
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            <Pagination />
          </div>
        )}

        {/* Orders */}
        {activeTab === 'orders' && (
          <div className="space-y-4">
            {/* Status Filter */}
            <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
              {[
                { value: '', label: 'Barchasi' },
                { value: 'pending', label: '⏳ Kutilmoqda' },
                { value: 'processing', label: '🔄 Jarayonda' },
                { value: 'completed', label: '✅ Bajarildi' },
                { value: 'canceled', label: '❌ Bekor' },
              ].map(f => (
                <button
                  key={f.value}
                  onClick={() => { setStatusFilter(f.value); setCurrentPage(1); }}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                    statusFilter === f.value
                      ? 'bg-purple-500 text-white'
                      : 'bg-[#111] text-white/70 hover:text-white border border-white/10'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Orders List */}
            {!loading && (
              <div className="space-y-2">
                {orders.map(order => (
                  <div key={order.id} className="bg-[#111] border border-white/10 rounded-xl p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="text-white font-mono text-sm">#{order.id}</span>
                        <span className="text-white/30 mx-2">•</span>
                        <span className="text-white/50 text-sm">{order.full_name || order.username}</span>
                      </div>
                      <StatusBadge status={order.status} />
                    </div>
                    <p className="text-white/80 text-sm truncate mb-2">{order.service}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-white/50">{formatNumber(order.quantity)} dona</span>
                      <span className="text-emerald-400 font-medium">{formatNumber(order.price)} so'm</span>
                    </div>
                    <p className="text-white/30 text-xs mt-2">{formatDate(order.created_at)}</p>
                  </div>
                ))}
              </div>
            )}
            <Pagination />
          </div>
        )}

        {/* Payments */}
        {activeTab === 'payments' && (
          <div className="space-y-4">
            {/* Filter */}
            <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
              {[
                { value: '', label: 'Barchasi' },
                { value: 'pending', label: '⏳ Kutilmoqda' },
                { value: 'approved', label: '✅ Tasdiqlangan' },
                { value: 'rejected', label: '❌ Rad etilgan' },
              ].map(f => (
                <button
                  key={f.value}
                  onClick={() => { setStatusFilter(f.value); setCurrentPage(1); }}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                    statusFilter === f.value
                      ? 'bg-purple-500 text-white'
                      : 'bg-[#111] text-white/70 hover:text-white border border-white/10'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Payments List */}
            {!loading && (
              <div className="space-y-2">
                {payments.map(payment => (
                  <div key={payment.id} className="bg-[#111] border border-white/10 rounded-xl p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-medium text-white">{payment.full_name || payment.username}</p>
                        <p className="text-sm text-white/50">{payment.method}</p>
                      </div>
                      <StatusBadge status={payment.status} />
                    </div>
                    
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-2xl font-bold text-emerald-400">{formatNumber(payment.amount)}</span>
                      <span className="text-white/30 text-sm">{formatDate(payment.created_at)}</span>
                    </div>

                    {payment.status === 'pending' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleApprovePayment(payment.id)}
                          className="flex-1 py-2.5 rounded-xl bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition-all"
                        >
                          ✅ Tasdiqlash
                        </button>
                        <button
                          onClick={() => handleRejectPayment(payment.id)}
                          className="flex-1 py-2.5 rounded-xl bg-red-500/20 text-red-400 font-medium border border-red-500/30 hover:bg-red-500/30 transition-all"
                        >
                          ❌ Rad etish
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            <Pagination />
          </div>
        )}

        {/* Settings */}
        {activeTab === 'settings' && (
          <div className="space-y-4">
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <span>⚙️</span> Tizim sozlamalari
              </h3>
              <p className="text-white/50 text-sm">
                Sozlamalar Telegram botda boshqariladi.<br/>
                Bot ichida <code className="bg-white/10 px-2 py-0.5 rounded">/admin</code> buyrug'ini yuboring.
              </p>
            </div>

            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <span>📡</span> API holati
              </h3>
              <div className="space-y-3">
                {[
                  { name: 'Peakerr SMM', status: true },
                  { name: 'SMMMain', status: true },
                  { name: 'VAK-SMS', status: true },
                  { name: '5SIM', status: false },
                  { name: 'SMSPVA', status: true },
                  { name: 'Click', status: false },
                ].map(api => (
                  <div key={api.name} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                    <span className="text-white/70">{api.name}</span>
                    <span className={api.status ? 'text-emerald-400' : 'text-amber-400'}>
                      {api.status ? '✅ Ishlayapti' : '⚠️ Sozlanmagan'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* User Detail Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end justify-center">
          <div className="w-full max-w-lg bg-[#111] rounded-t-3xl border-t border-white/10 max-h-[85vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-[#111] p-4 border-b border-white/10 flex items-center justify-between">
              <h3 className="font-bold text-white text-lg">Foydalanuvchi ma'lumotlari</h3>
              <button 
                onClick={() => { setSelectedUser(null); setBalanceAmount(''); }}
                className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-white/70"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 space-y-4">
              {/* User Info */}
              <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-2xl">
                  {selectedUser.full_name?.charAt(0) || '👤'}
                </div>
                <div>
                  <p className="font-bold text-white text-lg">{selectedUser.full_name || 'Noma\'lum'}</p>
                  <p className="text-white/50">@{selectedUser.username || selectedUser.user_id}</p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-emerald-400">{formatNumber(selectedUser.balance)}</p>
                  <p className="text-white/50 text-sm">Balans</p>
                </div>
                <div className="bg-white/5 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-white">{selectedUser.orders_count}</p>
                  <p className="text-white/50 text-sm">Buyurtmalar</p>
                </div>
              </div>

              {/* Details */}
              <div className="bg-white/5 rounded-xl divide-y divide-white/5">
                <div className="flex justify-between p-3">
                  <span className="text-white/50">ID</span>
                  <span className="text-white font-mono">{selectedUser.user_id}</span>
                </div>
                <div className="flex justify-between p-3">
                  <span className="text-white/50">Telefon</span>
                  <span className="text-white">{selectedUser.phone_number || '-'}</span>
                </div>
                <div className="flex justify-between p-3">
                  <span className="text-white/50">Sarfladi</span>
                  <span className="text-white">{formatNumber(selectedUser.total_spent)} so'm</span>
                </div>
                <div className="flex justify-between p-3">
                  <span className="text-white/50">Ro'yxatdan</span>
                  <span className="text-white">{formatDate(selectedUser.created_at)}</span>
                </div>
              </div>

              {/* Balance Change */}
              <div className="bg-white/5 rounded-xl p-4">
                <p className="text-white font-medium mb-3">💰 Balansni o'zgartirish</p>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={balanceAmount}
                    onChange={(e) => setBalanceAmount(e.target.value)}
                    placeholder="Summa (+/-)"
                    className="flex-1 bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:border-purple-500/50 focus:outline-none"
                  />
                  <button
                    onClick={handleBalanceChange}
                    disabled={!balanceAmount}
                    className="px-6 py-3 rounded-xl bg-purple-500 text-white font-medium disabled:opacity-30 hover:bg-purple-600 transition-all"
                  >
                    ✓
                  </button>
                </div>
                <p className="text-white/30 text-xs mt-2">
                  Qo'shish uchun musbat, ayirish uchun manfiy son kiriting
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
