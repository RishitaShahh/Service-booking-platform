import React, { useState } from 'react';
import { Calendar, Clock, DollarSign, User, X, AlertCircle } from 'lucide-react';
import { formatDate, formatTime, formatCurrency } from '../utils/dateUtils';

export const BookingModal = ({ isOpen, onClose, service, slot, onConfirm, isSubmitting, error }) => {
  const [notes, setNotes] = useState('');

  if (!isOpen || !service || !slot) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onConfirm({ notes });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-2xl relative border border-gray-100 animate-in fade-in zoom-in duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-xl font-bold text-gray-900 mb-4 border-b border-gray-100 pb-3">
          Confirm Your Appointment
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        <div className="bg-sky-50 rounded-lg p-4 mb-6 space-y-2 text-sm text-gray-700">
          <div className="font-semibold text-gray-900 text-base mb-1">{service.name}</div>
          
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-sky-600" />
            <span>Provider: <strong>{service.provider?.full_name}</strong></span>
          </div>

          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-sky-600" />
            <span>Date: <strong>{formatDate(slot.start_time)}</strong></span>
          </div>

          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-sky-600" />
            <span>Time: <strong>{formatTime(slot.start_time)} - {formatTime(slot.end_time)}</strong></span>
          </div>

          <div className="flex items-center space-x-2 border-t border-sky-200/60 pt-2 mt-2">
            <DollarSign className="w-4 h-4 text-sky-600" />
            <span className="text-base font-extrabold text-sky-700">Total Price: {formatCurrency(service.price)}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Special Instructions or Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Any specific requests or access details..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 text-sm"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-medium text-white bg-sky-600 hover:bg-sky-700 disabled:opacity-50 rounded-lg shadow-sm transition-colors flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Booking...</span>
                </>
              ) : (
                <span>Confirm Booking</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
