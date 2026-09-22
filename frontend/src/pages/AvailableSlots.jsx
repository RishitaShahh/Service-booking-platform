import React, { useState, useEffect } from 'react';
import { slotsApi } from '../api/slots';
import { servicesApi } from '../api/services';
import { SlotPicker } from '../components/SlotPicker';
import { Calendar, Filter } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { formatCurrency } from '../utils/dateUtils';

export const AvailableSlots = () => {
  const [slots, setSlots] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedServiceId, setSelectedServiceId] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        const [servicesData, slotsData] = await Promise.all([
          servicesApi.getServices(),
          slotsApi.getAvailableSlots()
        ]);
        setServices(servicesData);
        setSlots(slotsData);
      } catch (err) {
        console.error('Error loading slots data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  const handleFilterChange = async (e) => {
    const val = e.target.value;
    setSelectedServiceId(val);
    try {
      setLoading(true);
      const data = await slotsApi.getAvailableSlots(val ? { service_id: val } : {});
      setSlots(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSlot = (slot) => {
    if (slot.service_id) {
      navigate(`/services/${slot.service_id}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 pb-4 border-b border-gray-200 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <Calendar className="w-8 h-8 text-sky-600" />
            <span>Available Time Slots</span>
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Explore open appointment windows across all available services
          </p>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm w-full md:w-auto">
          <Filter className="w-4 h-4 text-sky-600 flex-shrink-0" />
          <select
            value={selectedServiceId}
            onChange={handleFilterChange}
            className="text-sm font-medium text-gray-700 bg-transparent focus:outline-none w-full"
          >
            <option value="">All Services</option>
            {services.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({formatCurrency(s.price)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
        </div>
      ) : (
        <SlotPicker slots={slots} selectedSlotId={null} onSelectSlot={handleSelectSlot} />
      )}
    </div>
  );
};
