import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

import { ServicesList } from './pages/ServicesList';
import { ServiceDetail } from './pages/ServiceDetail';
import { AvailableSlots } from './pages/AvailableSlots';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { CustomerBookings } from './pages/CustomerBookings';
import { ProviderDashboard } from './pages/ProviderDashboard';
import { ProviderManageServices } from './pages/ProviderManageServices';
import { ProviderManageSlots } from './pages/ProviderManageSlots';
import { ProviderManageBookings } from './pages/ProviderManageBookings';

export const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 flex flex-col justify-between">
          <div>
            <Navbar />
            <main>
              <Routes>
                {/* Public Customer / Visitor Routes */}
                <Route path="/" element={<ServicesList />} />
                <Route path="/services/:id" element={<ServiceDetail />} />
                <Route path="/slots" element={<AvailableSlots />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Customer Protected Routes */}
                <Route
                  path="/my-bookings"
                  element={
                    <ProtectedRoute allowedRole="customer">
                      <CustomerBookings />
                    </ProtectedRoute>
                  }
                />

                {/* Service Provider Protected Routes */}
                <Route
                  path="/provider/dashboard"
                  element={
                    <ProtectedRoute allowedRole="provider">
                      <ProviderDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/provider/services"
                  element={
                    <ProtectedRoute allowedRole="provider">
                      <ProviderManageServices />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/provider/slots"
                  element={
                    <ProtectedRoute allowedRole="provider">
                      <ProviderManageSlots />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/provider/bookings"
                  element={
                    <ProtectedRoute allowedRole="provider">
                      <ProviderManageBookings />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
          </div>

          <footer className="bg-white border-t border-gray-200 py-6 text-center text-xs text-gray-500 mt-12">
            <p>&copy; {new Date().getFullYear()} Service Booking Platform. Decoupled FastAPI + React Architecture.</p>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
