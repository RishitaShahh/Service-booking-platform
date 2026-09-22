import React, { useState, useEffect } from 'react';
import { providersApi } from '../api/providers';
import { StatusBadge } from '../components/StatusBadge';
import { Clock, Calendar, User, Phone, CheckCircle, XCircle } from 'lucide-react';
import { formatDate, formatTime } from '../utils/dateUtils';

export const ProviderManageBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [message, setMessage] = useState('');

  const fetchBookings = async (filter = '') => {
    try {
      setLoading(true);
      const data = await providersApi.getProviderBookings(filter ? { status: filter } : {});
      setBookings(data);
    } catch (err) {
      console.error('Error fetching provider bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings(statusFilter);
  }, [statusFilter]);

  const handleUpdateStatus = async (bookingId, newStatus) => {
    try {
      setUpdatingId(bookingId);
      await providersApi.updateBookingStatus(bookingId, newStatus);
      setMessage(`Booking status updated to "${newStatus}".`);
      fetchBookings(statusFilter);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update booking status.');
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-4 border-b border-gray-200 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <Clock className="w-8 h-8 text-sky-600" />
            <span>Manage Customer Bookings</span>
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Review incoming appointments, confirm reservations, or mark completed sessions
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-2 bg-gray-100 p-1 rounded-xl">
          {['', 'confirmed', 'completed', 'cancelled'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                statusFilter === st
                  ? 'bg-white text-sky-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {st === '' ? 'All Status' : st}
            </button>
          ))}
        </div>
      </div>

      {message && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-800 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span>{message}</span>
          </div>
          <button onClick={() => setMessage('')} className="text-xs font-bold text-green-600">Dismiss</button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
        </div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">No bookings found</h3>
          <p className="text-gray-500 text-sm">
            {statusFilter ? `No ${statusFilter} bookings found for your services.` : 'No incoming customer bookings yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              <div className="space-y-3 flex-grow">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-bold text-gray-900">{booking.service?.name}</h3>
                  <StatusBadge status={booking.status} />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-sky-600 flex-shrink-0" />
                    <span>Customer: <strong className="text-gray-800">{booking.customer?.full_name}</strong></span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Phone className="w-4 h-4 text-sky-600 flex-shrink-0" />
                    <span>Contact: <strong className="text-gray-800">{booking.customer?.phone || booking.customer?.email}</strong></span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-sky-600 flex-shrink-0" />
                    <span>Date: <strong className="text-gray-800">{formatDate(booking.slot?.start_time)}</strong></span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-sky-600 flex-shrink-0" />
                    <span>Time: <strong className="text-gray-800">{formatTime(booking.slot?.start_time)} - {formatTime(booking.slot?.end_time)}</strong></span>
                  </div>
                </div>

                {booking.notes && (
                  <p className="text-xs text-gray-500 bg-gray-50 p-2.5 rounded-lg border border-gray-100 italic">
                    Customer Note: "{booking.notes}"
                  </p>
                )}
              </div>

              {/* Status Actions */}
              <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2 border-t md:border-t-0 pt-4 md:pt-0 border-gray-100">
                {booking.status === 'confirmed' && (
                  <>
                    <button
                      onClick={() => handleUpdateStatus(booking.id, 'completed')}
                      disabled={updatingId === booking.id}
                      className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs font-semibold transition-colors flex items-center space-x-1"
                    >
                      <CheckCircle className="w-3.5 h-3.5 text-blue-600" />
                      <span>Mark Completed</span>
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(booking.id, 'cancelled')}
                      disabled={updatingId === booking.id}
                      className="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 rounded-lg text-xs font-semibold transition-colors flex items-center space-x-1"
                    >
                      <XCircle className="w-3.5 h-3.5 text-red-600" />
                      <span>Cancel</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
