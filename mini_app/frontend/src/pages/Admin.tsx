import React, { useState, useEffect, useCallback } from 'react';
import { useTelegram } from '../hooks/useTelegram';
import { adminAPI } from '../lib/api';
import { Card, Button, Loading, Input } from '../components';

// Dashboard statistikasi interfeysi
interface DashboardData {
  users: { total: number; today: number };
  orders: { total: number; today: number; pending: number; processing: number; completed: number; canceled: number };
  revenue: { total: number; today: number };
  payments: { pending: number; total_deposits: number };
  weekly_stats: { date: string; orders: number; revenue: number }[];
}

// User interfeysi
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

// Order interfeysi
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

// Payment interfeysi
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

const Admin: React.FC = () => {
  const { user } = useTelegram();
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  
  // Pagination
  const [userPage, setUserPage] = useState(1);
  const [orderPage, setOrderPage] = useState(1);
  const [paymentPage, setPaymentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [orderStatus, setOrderStatus] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  
  // Selected user for detail view
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [balanceChange, setBalanceChange] = useState('');
  
  const adminId = user?.id || 0;
  const adminHash = 'dev_hash'; // Development mode

  // Fetch dashboard
  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getDashboard(adminId, adminHash);
      if (response.success) {
        setDashboard(response.data);
      }
    } catch (err) {
      setError('Dashboard yuklanmadi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [adminId]);

  // Fetch users
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getUsers(adminId, adminHash, userPage, 20, searchQuery);
      if (response.success) {
        setUsers(response.data.users);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError('Foydalanuvchilar yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [adminId, userPage, searchQuery]);

  // Fetch orders
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getOrders(adminId, adminHash, orderPage, 20, orderStatus);
      if (response.success) {
        setOrders(response.data.orders);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError('Buyurtmalar yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [adminId, orderPage, orderStatus]);

  // Fetch payments
  const fetchPayments = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getPayments(adminId, adminHash, paymentPage, 20, paymentStatus);
      if (response.success) {
        setPayments(response.data.payments);
        setTotalPages(response.data.pages);
      }
    } catch (err) {
      setError("To'lovlar yuklanmadi");
    } finally {
      setLoading(false);
    }
  }, [adminId, paymentPage, paymentStatus]);

  // Initial load
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  // Tab change handler
  useEffect(() => {
    switch (activeTab) {
      case 'dashboard':
        fetchDashboard();
        break;
      case 'users':
        fetchUsers();
        break;
      case 'orders':
        fetchOrders();
        break;
      case 'payments':
        fetchPayments();
        break;
    }
  }, [activeTab, fetchDashboard, fetchUsers, fetchOrders, fetchPayments]);

  // Change user balance
  const handleBalanceChange = async (userId: number, amount: number) => {
    try {
      await adminAPI.changeBalance(adminId, adminHash, userId, amount, 'Admin panel orqali');
      fetchUsers();
      setSelectedUser(null);
      setBalanceChange('');
    } catch (err) {
      setError('Balans o\'zgartirilmadi');
    }
  };

  // Approve payment
  const handleApprovePayment = async (paymentId: number) => {
    try {
      await adminAPI.approvePayment(adminId, adminHash, paymentId);
      fetchPayments();
      fetchDashboard();
    } catch (err) {
      setError("To'lov tasdiqlanmadi");
    }
  };

  // Reject payment
  const handleRejectPayment = async (paymentId: number) => {
    try {
      await adminAPI.rejectPayment(adminId, adminHash, paymentId);
      fetchPayments();
    } catch (err) {
      setError("To'lov rad etilmadi");
    }
  };

  // Format number
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('uz-UZ').format(num);
  };

  // Format date
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('uz-UZ', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Status badge
  const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      processing: 'bg-blue-500/20 text-blue-400',
      completed: 'bg-green-500/20 text-green-400',
      canceled: 'bg-red-500/20 text-red-400',
      approved: 'bg-green-500/20 text-green-400',
      rejected: 'bg-red-500/20 text-red-400',
      partial: 'bg-orange-500/20 text-orange-400'
    };
    const labels: Record<string, string> = {
      pending: 'Kutilmoqda',
      processing: 'Jarayonda',
      completed: 'Bajarildi',
      canceled: 'Bekor',
      approved: 'Tasdiqlangan',
      rejected: 'Rad etilgan',
      partial: 'Qisman'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-500/20 text-gray-400'}`}>
        {labels[status] || status}
      </span>
    );
  };

  // Tabs
  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'users', label: 'Foydalanuvchilar', icon: '👥' },
    { id: 'orders', label: 'Buyurtmalar', icon: '📦' },
    { id: 'payments', label: "To'lovlar", icon: '💳' },
    { id: 'settings', label: 'Sozlamalar', icon: '⚙️' }
  ];

  if (loading && !dashboard) {
    return <Loading text="Admin panel yuklanmoqda..." />;
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] pb-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4">
        <h1 className="text-xl font-bold text-white">🔐 Admin Panel</h1>
        <p className="text-white/70 text-sm">SMM Xizmatlari boshqaruvi</p>
      </div>

      {/* Error */}
      {error && (
        <div className="m-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-white">✕</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex overflow-x-auto p-2 gap-2 bg-[#1a1a1a] border-b border-white/10">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white'
                : 'bg-white/5 text-white/60 hover:bg-white/10'
            }`}
          >
            <span>{tab.icon}</span>
            <span className="text-sm font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && dashboard && (
          <div className="space-y-4">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-3">
              <Card className="bg-gradient-to-br from-blue-600/20 to-blue-600/5 border-blue-500/30">
                <div className="p-4">
                  <p className="text-blue-400 text-xs font-medium">👥 Foydalanuvchilar</p>
                  <p className="text-2xl font-bold text-white mt-1">{formatNumber(dashboard.users.total)}</p>
                  <p className="text-green-400 text-xs mt-1">+{dashboard.users.today} bugun</p>
                </div>
              </Card>

              <Card className="bg-gradient-to-br from-green-600/20 to-green-600/5 border-green-500/30">
                <div className="p-4">
                  <p className="text-green-400 text-xs font-medium">📦 Buyurtmalar</p>
                  <p className="text-2xl font-bold text-white mt-1">{formatNumber(dashboard.orders.total)}</p>
                  <p className="text-green-400 text-xs mt-1">+{dashboard.orders.today} bugun</p>
                </div>
              </Card>

              <Card className="bg-gradient-to-br from-yellow-600/20 to-yellow-600/5 border-yellow-500/30">
                <div className="p-4">
                  <p className="text-yellow-400 text-xs font-medium">💰 Umumiy daromad</p>
                  <p className="text-2xl font-bold text-white mt-1">{formatNumber(dashboard.revenue.total)}</p>
                  <p className="text-xs text-white/50">so'm</p>
                </div>
              </Card>

              <Card className="bg-gradient-to-br from-purple-600/20 to-purple-600/5 border-purple-500/30">
                <div className="p-4">
                  <p className="text-purple-400 text-xs font-medium">💳 Kutilayotgan</p>
                  <p className="text-2xl font-bold text-white mt-1">{dashboard.payments.pending}</p>
                  <p className="text-xs text-white/50">to'lov</p>
                </div>
              </Card>
            </div>

            {/* Order Stats */}
            <Card>
              <div className="p-4">
                <h3 className="font-semibold text-white mb-3">📊 Buyurtma holatlari</h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-yellow-400 text-sm">⏳ Kutilmoqda</span>
                    <span className="text-white font-medium">{dashboard.orders.pending}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-400 text-sm">🔄 Jarayonda</span>
                    <span className="text-white font-medium">{dashboard.orders.processing}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-green-400 text-sm">✅ Bajarildi</span>
                    <span className="text-white font-medium">{dashboard.orders.completed}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-red-400 text-sm">❌ Bekor qilingan</span>
                    <span className="text-white font-medium">{dashboard.orders.canceled}</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Weekly Chart */}
            <Card>
              <div className="p-4">
                <h3 className="font-semibold text-white mb-3">📈 Oxirgi 7 kun</h3>
                <div className="space-y-2">
                  {dashboard.weekly_stats.slice(0, 7).reverse().map(day => (
                    <div key={day.date} className="flex items-center gap-2">
                      <span className="text-white/50 text-xs w-20">{day.date.slice(5)}</span>
                      <div className="flex-1 bg-white/10 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-purple-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, (day.orders / Math.max(...dashboard.weekly_stats.map(d => d.orders || 1))) * 100)}%` }}
                        />
                      </div>
                      <span className="text-white text-xs w-8 text-right">{day.orders}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            {/* Search */}
            <div className="flex gap-2">
              <Input
                placeholder="ID, username yoki ism qidirish..."
                value={searchQuery}
                onChange={(value) => setSearchQuery(value)}
                className="flex-1"
              />
              <Button onClick={fetchUsers} variant="primary" className="px-4">
                🔍
              </Button>
            </div>

            {/* Users List */}
            {loading ? (
              <Loading text="Yuklanmoqda..." />
            ) : (
              <div className="space-y-2">
                {users.map(u => (
                  <Card key={u.user_id} className="hover:border-purple-500/50 cursor-pointer" onClick={() => setSelectedUser(u)}>
                    <div className="p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-white">{u.full_name || 'Noma\'lum'}</p>
                          <p className="text-white/50 text-xs">@{u.username || u.user_id}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-green-400 font-medium">{formatNumber(u.balance)} so'm</p>
                          <p className="text-white/50 text-xs">{u.orders_count} buyurtma</p>
                        </div>
                      </div>
                      {u.is_blocked && (
                        <span className="mt-2 inline-block px-2 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">
                          Bloklangan
                        </span>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <Button
                  disabled={userPage === 1}
                  onClick={() => setUserPage(p => p - 1)}
                  variant="secondary"
                  size="sm"
                >
                  ◀️
                </Button>
                <span className="text-white px-4 py-2">{userPage} / {totalPages}</span>
                <Button
                  disabled={userPage === totalPages}
                  onClick={() => setUserPage(p => p + 1)}
                  variant="secondary"
                  size="sm"
                >
                  ▶️
                </Button>
              </div>
            )}
          </div>
        )}

        {/* User Detail Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md max-h-[80vh] overflow-y-auto">
              <div className="p-4">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{selectedUser.full_name}</h3>
                    <p className="text-white/50 text-sm">@{selectedUser.username || selectedUser.user_id}</p>
                  </div>
                  <button onClick={() => setSelectedUser(null)} className="text-white/50 text-xl">✕</button>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b border-white/10">
                    <span className="text-white/70">ID:</span>
                    <span className="text-white font-mono">{selectedUser.user_id}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/10">
                    <span className="text-white/70">Balans:</span>
                    <span className="text-green-400 font-medium">{formatNumber(selectedUser.balance)} so'm</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/10">
                    <span className="text-white/70">Buyurtmalar:</span>
                    <span className="text-white">{selectedUser.orders_count}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/10">
                    <span className="text-white/70">Sarfladi:</span>
                    <span className="text-white">{formatNumber(selectedUser.total_spent)} so'm</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/10">
                    <span className="text-white/70">Ro'yxatdan:</span>
                    <span className="text-white text-sm">{formatDate(selectedUser.created_at)}</span>
                  </div>
                </div>

                {/* Balance change */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-white/70 text-sm mb-2">Balansni o'zgartirish:</p>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      placeholder="Summa (+/-)"
                      value={balanceChange}
                      onChange={(value) => setBalanceChange(value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={() => handleBalanceChange(selectedUser.user_id, parseInt(balanceChange))}
                      variant="primary"
                      disabled={!balanceChange}
                    >
                      ✓
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {['', 'pending', 'processing', 'completed', 'canceled'].map(status => (
                <button
                  key={status}
                  onClick={() => { setOrderStatus(status); setOrderPage(1); }}
                  className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap ${
                    orderStatus === status
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-white/70'
                  }`}
                >
                  {status === '' ? 'Barchasi' : status === 'pending' ? 'Kutilmoqda' : status === 'processing' ? 'Jarayonda' : status === 'completed' ? 'Bajarildi' : 'Bekor'}
                </button>
              ))}
            </div>

            {/* Orders List */}
            {loading ? (
              <Loading text="Yuklanmoqda..." />
            ) : (
              <div className="space-y-2">
                {orders.map(order => (
                  <Card key={order.id}>
                    <div className="p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium text-white">#{order.id}</p>
                          <p className="text-white/50 text-xs">{order.full_name || order.username}</p>
                        </div>
                        <StatusBadge status={order.status} />
                      </div>
                      <p className="text-white/70 text-sm truncate">{order.service}</p>
                      <div className="flex justify-between mt-2 text-sm">
                        <span className="text-white/50">{formatNumber(order.quantity)} dona</span>
                        <span className="text-green-400">{formatNumber(order.price)} so'm</span>
                      </div>
                      <p className="text-white/30 text-xs mt-1">{formatDate(order.created_at)}</p>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <Button disabled={orderPage === 1} onClick={() => setOrderPage(p => p - 1)} variant="secondary" size="sm">◀️</Button>
                <span className="text-white px-4 py-2">{orderPage} / {totalPages}</span>
                <Button disabled={orderPage === totalPages} onClick={() => setOrderPage(p => p + 1)} variant="secondary" size="sm">▶️</Button>
              </div>
            )}
          </div>
        )}

        {/* Payments Tab */}
        {activeTab === 'payments' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {['', 'pending', 'approved', 'rejected'].map(status => (
                <button
                  key={status}
                  onClick={() => { setPaymentStatus(status); setPaymentPage(1); }}
                  className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap ${
                    paymentStatus === status
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-white/70'
                  }`}
                >
                  {status === '' ? 'Barchasi' : status === 'pending' ? 'Kutilmoqda' : status === 'approved' ? 'Tasdiqlangan' : 'Rad etilgan'}
                </button>
              ))}
            </div>

            {/* Payments List */}
            {loading ? (
              <Loading text="Yuklanmoqda..." />
            ) : (
              <div className="space-y-2">
                {payments.map(payment => (
                  <Card key={payment.id}>
                    <div className="p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium text-white">{payment.full_name || payment.username}</p>
                          <p className="text-white/50 text-xs">{payment.method}</p>
                        </div>
                        <StatusBadge status={payment.status} />
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-green-400 font-medium text-lg">{formatNumber(payment.amount)} so'm</span>
                        <span className="text-white/30 text-xs">{formatDate(payment.created_at)}</span>
                      </div>
                      
                      {/* Action buttons for pending */}
                      {payment.status === 'pending' && (
                        <div className="flex gap-2 mt-3">
                          <Button
                            onClick={() => handleApprovePayment(payment.id)}
                            variant="primary"
                            size="sm"
                            className="flex-1 bg-green-600 hover:bg-green-700"
                          >
                            ✅ Tasdiqlash
                          </Button>
                          <Button
                            onClick={() => handleRejectPayment(payment.id)}
                            variant="danger"
                            size="sm"
                            className="flex-1"
                          >
                            ❌ Rad etish
                          </Button>
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <Button disabled={paymentPage === 1} onClick={() => setPaymentPage(p => p - 1)} variant="secondary" size="sm">◀️</Button>
                <span className="text-white px-4 py-2">{paymentPage} / {totalPages}</span>
                <Button disabled={paymentPage === totalPages} onClick={() => setPaymentPage(p => p + 1)} variant="secondary" size="sm">▶️</Button>
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-4">
            <Card>
              <div className="p-4">
                <h3 className="font-semibold text-white mb-4">⚙️ Tizim sozlamalari</h3>
                <p className="text-white/50 text-sm">
                  Sozlamalar botda boshqariladi. Telegram botda /admin buyrug'ini ishlating.
                </p>
              </div>
            </Card>

            <Card>
              <div className="p-4">
                <h3 className="font-semibold text-white mb-4">📊 API holati</h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center py-2">
                    <span className="text-white/70">Peakerr SMM</span>
                    <span className="text-green-400">✅ Ishlayapti</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-white/70">SMMMain</span>
                    <span className="text-green-400">✅ Ishlayapti</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-white/70">VAK-SMS</span>
                    <span className="text-green-400">✅ Ishlayapti</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-white/70">Click</span>
                    <span className="text-yellow-400">⚠️ Sozlanmagan</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
