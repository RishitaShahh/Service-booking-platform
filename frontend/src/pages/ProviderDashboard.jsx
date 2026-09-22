import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { providersApi } from '../api/providers';
import { StatusBadge } from '../components/StatusBadge';
import {
  LayoutDashboard,
  Wrench,
  Calendar,
  Clock,
  DollarSign,
  TrendingUp,
  PlusCircle,
  ArrowRight,
  User,
  CheckCircle2,
} from 'lucide-react';
import { formatDate, formatTime, formatCurrency } from '../utils/dateUtils';

export const ProviderDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const data = await providersApi.getDashboardSummary();
        setSummary(data);
      } catch (err) {
        console.error('Error loading provider dashboard summary:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Welcome Banner */}
      <div className="bg-gradient-to-r from-sky-700 to-indigo-800 rounded-2xl p-8 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center space-x-2 bg-sky-500/30 text-sky-100 px-3 py-1 rounded-full text-xs font-semibold mb-3">
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Service Provider Control Center</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">Provider Dashboard</h1>
          <p className="text-sky-100 text-sm mt-1">
            Monitor your schedule, revenue metrics, service offerings, and slot availability in real time.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/provider/services"
            className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2.5 rounded-xl text-xs font-semibold transition-colors flex items-center space-x-1.5"
          >
            <Wrench className="w-4 h-4" />
            <span>Add Service</span>
          </Link>
          <Link
            to="/provider/slots"
            className="bg-sky-500 hover:bg-sky-400 text-white px-4 py-2.5 rounded-xl text-xs font-semibold shadow-md transition-colors flex items-center space-x-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Generate Slots</span>
          </Link>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Revenue</p>
            <h3 className="text-2xl font-extrabold text-gray-900 mt-1">
              {formatCurrency(summary?.total_revenue)}
            </h3>
            <p className="text-xs text-green-600 mt-1 flex items-center">
              <TrendingUp className="w-3.5 h-3.5 mr-1" />
              Confirmed & completed
            </p>
          </div>
          <div className="w-12 h-12 bg-green-100 text-green-600 rounded-xl flex items-center justify-center">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Upcoming Bookings</p>
            <h3 className="text-2xl font-extrabold text-sky-600 mt-1">
              {summary?.upcoming_bookings_count || 0}
            </h3>
            <p className="text-xs text-gray-500 mt-1">Active reservations</p>
          </div>
          <div className="w-12 h-12 bg-sky-100 text-sky-600 rounded-xl flex items-center justify-center">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Available Slots</p>
            <h3 className="text-2xl font-extrabold text-amber-600 mt-1">
              {summary?.available_slots || 0}
            </h3>
            <p className="text-xs text-gray-500 mt-1">Out of {summary?.total_slots || 0} total slots</p>
          </div>
          <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-xl flex items-center justify-center">
            <Calendar className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Active Services</p>
            <h3 className="text-2xl font-extrabold text-indigo-600 mt-1">
              {summary?.total_services || 0}
            </h3>
            <p className="text-xs text-gray-500 mt-1">Catalog items</p>
          </div>
          <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center">
            <Wrench className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Upcoming Bookings Section */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-100 pb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
              <Clock className="w-5 h-5 text-sky-600" />
              <span>Upcoming Schedule (Your Bookings)</span>
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Strictly scoped to services & slots owned by your account
            </p>
          </div>

          <Link
            to="/provider/bookings"
            className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center space-x-1"
          >
            <span>Manage All Bookings</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {!summary?.upcoming_bookings || summary.upcoming_bookings.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-xl border border-gray-100">
            <CheckCircle2 className="w-10 h-10 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600 font-medium">No upcoming appointments scheduled.</p>
            <p className="text-xs text-gray-500 mt-1">Generate new time slots to open up bookings for customers.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {summary.upcoming_bookings.map((booking) => (
              <div key={booking.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-bold text-gray-900">{booking.service?.name}</span>
                    <StatusBadge status={booking.status} />
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                    <span className="flex items-center space-x-1">
                      <User className="w-3.5 h-3.5 text-sky-600" />
                      <span>Customer: <strong>{booking.customer?.full_name}</strong> ({booking.customer?.email})</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Calendar className="w-3.5 h-3.5 text-sky-600" />
                      <span>{formatDate(booking.slot?.start_time)}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-sky-600" />
                      <span>{formatTime(booking.slot?.start_time)} - {formatTime(booking.slot?.end_time)}</span>
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-base font-bold text-sky-600">{formatCurrency(booking.service?.price)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
