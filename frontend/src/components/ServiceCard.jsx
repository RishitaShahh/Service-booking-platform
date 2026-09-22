import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, User, ArrowRight } from 'lucide-react';
import { formatCurrency } from '../utils/dateUtils';

export const ServiceCard = ({ service }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-lg font-bold text-gray-900 group-hover:text-sky-600 transition-colors">
            {service.name}
          </h3>
          <span className="inline-flex items-center text-lg font-extrabold text-sky-600 bg-sky-50 px-3 py-1 rounded-lg">
            {formatCurrency(service.price)}
          </span>
        </div>

        <p className="text-gray-600 text-sm line-clamp-2 mb-4">
          {service.description || 'No detailed description provided.'}
        </p>
      </div>

      <div className="border-t border-gray-100 pt-4 mt-2">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4 text-sky-500" />
            <span>{service.duration_minutes} mins</span>
          </div>

          <div className="flex items-center space-x-1">
            <User className="w-4 h-4 text-sky-500" />
            <span className="font-medium text-gray-700">{service.provider?.full_name || 'Provider'}</span>
          </div>
        </div>

        <Link
          to={`/services/${service.id}`}
          className="w-full inline-flex items-center justify-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white font-medium py-2 px-4 rounded-lg text-sm shadow-sm transition-colors"
        >
          <span>View Details & Book</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};
