import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { servicesApi } from '../api/services';
import { slotsApi } from '../api/slots';
import { bookingsApi } from '../api/bookings';
import { useAuth } from '../context/AuthContext';
import { SlotPicker } from '../components/SlotPicker';
import { BookingModal } from '../components/BookingModal';
import { Clock, DollarSign, User, Calendar, CheckCircle2, ArrowLeft, AlertCircle } from 'lucide-react';
import { formatCurrency } from '../utils/dateUtils';

export const ServiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isCustomer } = useAuth();

  const [service, setService] = useState(null);
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [bookingError, setBookingError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [serviceData, slotsData] = await Promise.all([
          servicesApi.getServiceById(id),
          slotsApi.getAvailableSlots({ service_id: id })
        ]);
        setService(serviceData);
        setSlots(slotsData);
      } catch (err) {
        console.error(err);
        setError('Failed to load service details or available slots.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSelectSlot = (slot) => {
    setSelectedSlot(slot);
  };

  const handleOpenBookingModal = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!isCustomer) {
      alert('Only customers can book service appointments. Please sign in with a customer account.');
      return;
    }
    if (!selectedSlot) {
      alert('Please select a time slot first.');
      return;
    }
    setBookingError('');
    setIsModalOpen(true);
  };

  const handleConfirmBooking = async ({ notes }) => {
    try {
      setSubmitting(true);
      setBookingError('');

      await bookingsApi.createBooking({
        service_id: Number(id),
        slot_id: selectedSlot.id,
        notes: notes
      });

      setIsModalOpen(false);
      navigate('/my-bookings', { state: { bookingSuccess: true } });
    } catch (err) {
      console.error(err);
      setBookingError(err.response?.data?.detail || 'Failed to complete booking. Please try another slot.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Service Not Found</h2>
        <p className="text-gray-600 mb-6">{error || 'The requested service could not be loaded.'}</p>
        <Link to="/" className="inline-flex items-center space-x-2 text-sky-600 font-semibold hover:underline">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Catalog</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Link to="/" className="inline-flex items-center space-x-1 text-sm font-medium text-gray-600 hover:text-sky-600 mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to All Services</span>
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Service Details */}
        <div className="lg:col-span-1 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-fit space-y-6">
          <div>
            <span className="inline-block bg-sky-100 text-sky-800 text-xs font-semibold px-2.5 py-1 rounded-full mb-3">
              Active Service
            </span>
            <h1 className="text-2xl font-bold text-gray-900">{service.name}</h1>
          </div>

          <div className="border-t border-b border-gray-100 py-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 flex items-center space-x-1">
                <DollarSign className="w-4 h-4 text-sky-600" />
                <span>Price</span>
              </span>
              <span className="text-xl font-extrabold text-sky-600">{formatCurrency(service.price)}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 flex items-center space-x-1">
                <Clock className="w-4 h-4 text-sky-600" />
                <span>Duration</span>
              </span>
              <span className="text-sm font-semibold text-gray-800">{service.duration_minutes} minutes</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 flex items-center space-x-1">
                <User className="w-4 h-4 text-sky-600" />
                <span>Provider</span>
              </span>
              <span className="text-sm font-semibold text-gray-800">{service.provider?.full_name || 'N/A'}</span>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2">Description</h3>
            <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
              {service.description || 'No detailed description provided.'}
            </p>
          </div>

          {/* Book Action Button */}
          <div className="pt-2">
            <button
              onClick={handleOpenBookingModal}
              disabled={!selectedSlot}
              className="w-full bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white font-bold py-3 px-4 rounded-xl shadow-md transition-colors text-sm flex items-center justify-center space-x-2"
            >
              <CheckCircle2 className="w-5 h-5" />
              <span>{selectedSlot ? 'Proceed to Book Appointment' : 'Select a Time Slot Below'}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Time Slot Selection */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-3">
              <div>
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-sky-600" />
                  <span>Select an Available Time Slot</span>
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Choose a date and time that fits your schedule
                </p>
              </div>

              {selectedSlot && (
                <span className="text-xs bg-sky-50 text-sky-700 border border-sky-200 font-semibold px-3 py-1 rounded-full">
                  1 Slot Selected
                </span>
              )}
            </div>

            <SlotPicker
              slots={slots}
              selectedSlotId={selectedSlot?.id}
              onSelectSlot={handleSelectSlot}
            />
          </div>
        </div>
      </div>

      {/* Confirmation Booking Modal */}
      <BookingModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        service={service}
        slot={selectedSlot}
        onConfirm={handleConfirmBooking}
        isSubmitting={submitting}
        error={bookingError}
      />
    </div>
  );
};
