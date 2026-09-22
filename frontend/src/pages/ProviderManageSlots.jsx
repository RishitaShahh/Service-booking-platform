import React, { useState, useEffect } from 'react';
import { slotsApi } from '../api/slots';
import { servicesApi } from '../api/services';
import { PlusCircle, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { formatDate, formatTime } from '../utils/dateUtils';

export const ProviderManageSlots = () => {
  const [slots, setSlots] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState('batch'); // 'batch' or 'single'

  // Batch Form State
  const [batchForm, setBatchForm] = useState({
    service_id: '',
    target_date: new Date().toISOString().split('T')[0],
    start_hour: 9,
    end_hour: 17,
    slot_duration_minutes: 60,
  });

  // Single Form State
  const [singleForm, setSingleForm] = useState({
    service_id: '',
    start_time: '',
    end_time: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [slotsData, servicesData] = await Promise.all([
        slotsApi.getProviderSlots(),
        servicesApi.getProviderServices(),
      ]);
      setSlots(slotsData);
      setServices(servicesData);
    } catch (err) {
      console.error(err);
      setError('Failed to load slots.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setSubmitting(true);

    try {
      const payload = {
        ...batchForm,
        service_id: batchForm.service_id ? Number(batchForm.service_id) : null,
      };
      const created = await slotsApi.batchCreateSlots(payload);
      setSuccessMsg(`Successfully generated ${created.length} time slot windows.`);
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to batch generate time slots.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setSubmitting(true);

    try {
      const payload = {
        service_id: singleForm.service_id ? Number(singleForm.service_id) : null,
        start_time: new Date(singleForm.start_time).toISOString(),
        end_time: new Date(singleForm.end_time).toISOString(),
        status: 'available',
      };
      await slotsApi.createSlot(payload);
      setSuccessMsg('Time slot created successfully.');
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create time slot.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    if (!window.confirm('Delete this unbooked time slot?')) return;
    try {
      await slotsApi.deleteSlot(slotId);
      setSuccessMsg('Time slot deleted.');
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete slot.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
          <PlusCircle className="w-8 h-8 text-sky-600" />
          <span>Manage Time Slot Availability</span>
        </h1>
        <p className="text-gray-600 text-sm mt-1">
          Create single or batch-generate recurring available appointment windows for your services
        </p>
      </div>

      {successMsg && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-800 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg('')} className="text-xs font-bold text-green-600">Dismiss</button>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Generator Form Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
          <h2 className="text-xl font-bold text-gray-900">Generate New Slots</h2>
          
          <div className="flex bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setMode('batch')}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                mode === 'batch' ? 'bg-white text-sky-700 shadow-sm' : 'text-gray-600'
              }`}
            >
              Batch Day Generator
            </button>
            <button
              onClick={() => setMode('single')}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                mode === 'single' ? 'bg-white text-sky-700 shadow-sm' : 'text-gray-600'
              }`}
            >
              Single Custom Window
            </button>
          </div>
        </div>

        {mode === 'batch' ? (
          <form onSubmit={handleBatchSubmit} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Target Service</label>
              <select
                value={batchForm.service_id}
                onChange={(e) => setBatchForm({ ...batchForm, service_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-sky-500"
              >
                <option value="">All Services (Unassigned)</option>
                {services.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Target Date</label>
              <input
                type="date"
                required
                value={batchForm.target_date}
                onChange={(e) => setBatchForm({ ...batchForm, target_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Hours Range</label>
              <div className="flex items-center space-x-1">
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={batchForm.start_hour}
                  onChange={(e) => setBatchForm({ ...batchForm, start_hour: Number(e.target.value) })}
                  className="w-full px-2 py-2 border border-gray-300 rounded-lg text-sm text-center"
                />
                <span className="text-xs text-gray-400">to</span>
                <input
                  type="number"
                  min={1}
                  max={24}
                  value={batchForm.end_hour}
                  onChange={(e) => setBatchForm({ ...batchForm, end_hour: Number(e.target.value) })}
                  className="w-full px-2 py-2 border border-gray-300 rounded-lg text-sm text-center"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Slot Duration</label>
              <select
                value={batchForm.slot_duration_minutes}
                onChange={(e) => setBatchForm({ ...batchForm, slot_duration_minutes: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value={30}>30 mins</option>
                <option value={45}>45 mins</option>
                <option value={60}>60 mins (1 hr)</option>
                <option value={90}>90 mins (1.5 hrs)</option>
                <option value={120}>120 mins (2 hrs)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-sky-600 hover:bg-sky-700 text-white font-semibold py-2 px-4 rounded-lg shadow-sm text-sm transition-colors disabled:opacity-50"
              >
                {submitting ? 'Generating...' : 'Generate Batch'}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSingleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Target Service</label>
              <select
                value={singleForm.service_id}
                onChange={(e) => setSingleForm({ ...singleForm, service_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Services</option>
                {services.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Start Time</label>
              <input
                type="datetime-local"
                required
                value={singleForm.start_time}
                onChange={(e) => setSingleForm({ ...singleForm, start_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">End Time</label>
              <input
                type="datetime-local"
                required
                value={singleForm.end_time}
                onChange={(e) => setSingleForm({ ...singleForm, end_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-sky-600 hover:bg-sky-700 text-white font-semibold py-2 px-4 rounded-lg shadow-sm text-sm transition-colors"
              >
                {submitting ? 'Creating...' : 'Create Window'}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Existing Created Slots */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-4">
        <div className="flex justify-between items-center border-b border-gray-100 pb-3">
          <h2 className="text-xl font-bold text-gray-900">Your Created Time Slots</h2>
          <span className="text-xs text-gray-500">{slots.length} total slots</span>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
          </div>
        ) : slots.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No time slots created yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {slots.map((slot) => (
              <div
                key={slot.id}
                className={`p-3 rounded-xl border text-sm flex justify-between items-center ${
                  slot.status === 'booked'
                    ? 'bg-sky-50 border-sky-200'
                    : 'bg-white border-gray-200'
                }`}
              >
                <div>
                  <div className="font-semibold text-gray-800 text-xs">
                    {formatDate(slot.start_time)} • {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </div>
                  <div className="text-[11px] text-gray-500 mt-0.5 capitalize">
                    Status: <span className={slot.status === 'booked' ? 'text-sky-700 font-bold' : 'text-green-600 font-bold'}>{slot.status}</span>
                    {slot.service?.name && ` (${slot.service.name})`}
                  </div>
                </div>

                {slot.status !== 'booked' && (
                  <button
                    onClick={() => handleDeleteSlot(slot.id)}
                    className="text-gray-400 hover:text-red-600 p-1 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
