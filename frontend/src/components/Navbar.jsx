import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Calendar, Clock, LayoutDashboard, LogOut, PlusCircle, User, Wrench } from 'lucide-react';

export const Navbar = () => {
  const { user, isAuthenticated, isCustomer, isProvider, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 text-sky-600 font-bold text-xl">
              <Calendar className="w-7 h-7 text-sky-600" />
              <span>Bookify</span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex ml-10 space-x-4">
              <Link
                to="/"
                className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Services
              </Link>

              {isCustomer && (
                <Link
                  to="/my-bookings"
                  className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1"
                >
                  <Clock className="w-4 h-4" />
                  <span>My Bookings</span>
                </Link>
              )}

              {isProvider && (
                <>
                  <Link
                    to="/provider/dashboard"
                    className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1"
                  >
                    <LayoutDashboard className="w-4 h-4" />
                    <span>Dashboard</span>
                  </Link>
                  <Link
                    to="/provider/services"
                    className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1"
                  >
                    <Wrench className="w-4 h-4" />
                    <span>Manage Services</span>
                  </Link>
                  <Link
                    to="/provider/slots"
                    className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1"
                  >
                    <PlusCircle className="w-4 h-4" />
                    <span>Manage Slots</span>
                  </Link>
                  <Link
                    to="/provider/bookings"
                    className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1"
                  >
                    <Clock className="w-4 h-4" />
                    <span>Manage Bookings</span>
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* User Status / Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-700 bg-gray-100 px-3 py-1.5 rounded-full">
                  <User className="w-4 h-4 text-sky-600" />
                  <span className="font-medium">{user?.full_name}</span>
                  <span className="text-xs bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full capitalize">
                    {user?.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-500 hover:text-red-600 text-sm font-medium transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-sky-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="bg-sky-600 hover:bg-sky-700 text-white px-4 py-2 rounded-md text-sm font-medium shadow-sm transition-colors"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
