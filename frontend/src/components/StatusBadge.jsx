import React from 'react';
import { CheckCircle2, Clock, XCircle, AlertCircle } from 'lucide-react';

export const StatusBadge = ({ status }) => {
  const getBadgeStyle = () => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return {
          bg: 'bg-green-100 text-green-800 border-green-200',
          icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-green-600" />,
        };
      case 'completed':
        return {
          bg: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-blue-600" />,
        };
      case 'cancelled':
        return {
          bg: 'bg-red-100 text-red-800 border-red-200',
          icon: <XCircle className="w-3.5 h-3.5 mr-1 text-red-600" />,
        };
      case 'pending':
        return {
          bg: 'bg-amber-100 text-amber-800 border-amber-200',
          icon: <Clock className="w-3.5 h-3.5 mr-1 text-amber-600" />,
        };
      default:
        return {
          bg: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: <AlertCircle className="w-3.5 h-3.5 mr-1 text-gray-600" />,
        };
    }
  };

  const style = getBadgeStyle();

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style.bg}`}>
      {style.icon}
      <span className="capitalize">{status}</span>
    </span>
  );
};
