import React from 'react';
import { Calendar as CalendarIcon, Clock, CheckCircle } from 'lucide-react';
import { formatDate, formatTime } from '../utils/dateUtils';

export const SlotPicker = ({ slots, selectedSlotId, onSelectSlot }) => {
  if (!slots || slots.length === 0) {
    return (
      <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
        <Clock className="w-10 h-10 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600 font-medium">No available time slots found.</p>
        <p className="text-xs text-gray-500 mt-1">Please check back later or select another provider.</p>
      </div>
    );
  }

  // Group slots by date string
  const groupedSlots = slots.reduce((acc, slot) => {
    const dateKey = formatDate(slot.start_time);
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(slot);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(groupedSlots).map(([dateLabel, dateSlots]) => (
        <div key={dateLabel} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-2 text-sm font-semibold text-gray-800 mb-3 border-b border-gray-100 pb-2">
            <CalendarIcon className="w-4 h-4 text-sky-600" />
            <span>{dateLabel}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {dateSlots.map((slot) => {
              const isSelected = selectedSlotId === slot.id;
              return (
                <button
                  key={slot.id}
                  type="button"
                  onClick={() => onSelectSlot(slot)}
                  className={`flex flex-col items-center justify-center p-3 rounded-lg border text-sm font-medium transition-all ${
                    isSelected
                      ? 'bg-sky-50 border-sky-600 text-sky-700 shadow-sm ring-2 ring-sky-500 ring-opacity-50'
                      : 'bg-white border-gray-200 text-gray-700 hover:border-sky-300 hover:bg-sky-50/50'
                  }`}
                >
                  <div className="flex items-center space-x-1">
                    <span>{formatTime(slot.start_time)}</span>
                    {isSelected && <CheckCircle className="w-3.5 h-3.5 text-sky-600 ml-1" />}
                  </div>
                  <span className="text-xs text-gray-400 font-normal mt-0.5">
                    to {formatTime(slot.end_time)}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
