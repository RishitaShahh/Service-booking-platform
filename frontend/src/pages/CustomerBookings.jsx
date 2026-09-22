import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { bookingsApi } from '../api/bookings';
import { StatusBadge } from '../components/StatusBadge';
import { Calendar, Clock, User, XCircle, CheckCircle } from 'lucide-react';
import { formatDate, formatTime, formatCurrency } from '../utils/dateUtils';

export const CustomerBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);
  const [message, setMessage] = useState('');
  const location = useLocation();

  const fetchBookings = async (filter = '') => {
    try {
      setLoading(true);
      const data = await bookingsApi.getCustomerBookings(filter ? { status: filter } : {});
      setBookings(data);
    } catch (err) {
      console.error('Error loading customer bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (location.state?.bookingSuccess) {
      setMessage('Appointment successfully booked! Your reservation is confirmed.');
    }
    fetchBookings(statusFilter);
  }, [statusFilter, location.state]);

  const handleCancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking? The slot will be released for other customers.')) {
      return;
    }

    try {
      setCancellingId(bookingId);
      await bookingsApi.cancelBooking(bookingId);
      setMessage('Booking cancelled successfully and time slot released back to available status.');
      fetchBookings(statusFilter);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to cancel booking.');
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 pb-4 border-b border-gray-200 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <Clock className="w-8 h-8 text-sky-600" />
            <span>My Bookings History</span>
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            View and manage all your scheduled appointments and reservation history
          </p>
        </div>

        {/* Status Filter Tabs */}
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
        <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-800 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            <span>{message}</span>
          </div>
          <button onClick={() => setMessage('')} className="text-green-600 font-bold hover:underline text-xs">
            Dismiss
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
        </div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">No Bookings Found</h3>
          <p className="text-gray-500 text-sm">
            {statusFilter
              ? `You have no ${statusFilter} bookings.`
              : "You haven't booked any appointments yet."}
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
                    <span>Provider: <strong className="text-gray-800">{booking.provider?.full_name}</strong></span>
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
                    Note: "{booking.notes}"
                  </p>
                )}
              </div>

              {/* Price & Action */}
              <div className="flex flex-row md:flex-col items-center md:items-end justify-between border-t md:border-t-0 pt-4 md:pt-0 border-gray-100 gap-3">
                <div className="text-right">
                  <span className="text-xs text-gray-400 block">Total Price</span>
                  <span className="text-xl font-extrabold text-sky-600">
                    {formatCurrency(booking.service?.price)}
                  </span>
                </div>

                {booking.status === 'confirmed' && (
                  <button
                    onClick={() => handleCancelBooking(booking.id)}
                    disabled={cancellingId === booking.id}
                    className="flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {cancellingId === booking.id ? (
                      <span>Cancelling...</span>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4 text-red-600" />
                        <span>Cancel Booking</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
