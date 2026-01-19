import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useTelegram } from './hooks/useTelegram'
import { AuthProvider } from './providers'

// Pages
import Home from './pages/Home'
import Services from './pages/Services'
import Platform from './pages/Platform'
import ServiceOrder from './pages/ServiceOrder'
import Orders from './pages/Orders'
import Balance from './pages/Balance'
import Deposit from './pages/Deposit'
import ClickDeposit from './pages/ClickDeposit'
import Referral from './pages/Referral'
import SMS from './pages/SMS'
import Premium from './pages/Premium'
import Admin from './pages/Admin'

// Layout
import Layout from './components/Layout'

function App() {
  const { tg, ready } = useTelegram()

  useEffect(() => {
    if (tg) {
      // Expand the app
      tg.expand()
      
      // Set header color
      tg.setHeaderColor('#0088cc')
      
      // Enable closing confirmation
      tg.enableClosingConfirmation()
      
      // Ready
      tg.ready()
    }
  }, [tg, ready])

  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/services" element={<Services />} />
            <Route path="/services/:platformId" element={<Platform />} />
            <Route path="/order/:serviceId" element={<ServiceOrder />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/balance" element={<Balance />} />
            <Route path="/deposit" element={<Deposit />} />
            <Route path="/deposit/click" element={<ClickDeposit />} />
            <Route path="/referral" element={<Referral />} />
            <Route path="/sms" element={<SMS />} />
            <Route path="/premium" element={<Premium />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
