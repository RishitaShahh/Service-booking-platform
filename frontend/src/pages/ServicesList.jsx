import React, { useState, useEffect } from 'react';
import { servicesApi } from '../api/services';
import { ServiceCard } from '../components/ServiceCard';
import { Search, Wrench, Sparkles } from 'lucide-react';

export const ServicesList = () => {
  const [services, setServices] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchServices = async (searchQuery = '') => {
    try {
      setLoading(true);
      const data = await servicesApi.getServices({ search: searchQuery });
      setServices(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load available services.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchServices(search);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-sky-600 to-sky-800 rounded-2xl p-8 md:p-12 mb-10 text-white shadow-xl">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-sky-500/30 text-sky-100 px-3 py-1 rounded-full text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Professional On-Demand Services</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-4">
            Book Trusted Experts in Minutes
          </h1>
          <p className="text-sky-100 text-base md:text-lg mb-8">
            Browse our wide catalog of services, view real-time time slot availability, and book instant appointments.
          </p>

          {/* Search bar */}
          <form onSubmit={handleSearchSubmit} className="flex max-w-xl">
            <div className="relative flex-grow">
              <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search services by title or description..."
                className="w-full pl-11 pr-4 py-3 bg-white text-gray-900 placeholder-gray-500 rounded-l-xl focus:outline-none focus:ring-2 focus:ring-sky-300 text-sm"
              />
            </div>
            <button
              type="submit"
              className="bg-sky-900 hover:bg-sky-950 text-white font-medium px-6 py-3 rounded-r-xl transition-colors text-sm flex items-center"
            >
              Search
            </button>
          </form>
        </div>
      </div>

      {/* Services Grid Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
          <Wrench className="w-6 h-6 text-sky-600" />
          <span>Available Services</span>
        </h2>
        <span className="text-sm text-gray-500">
          Showing {services.length} active service{services.length !== 1 && 's'}
        </span>
      </div>

      {/* Loading state */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-white p-6 rounded-xl border border-gray-200 animate-pulse h-56 flex flex-col justify-between">
              <div>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-gray-100 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-100 rounded w-2/3"></div>
              </div>
              <div className="h-10 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg text-center">{error}</div>
      ) : services.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Wrench className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">No services found</h3>
          <p className="text-gray-500 text-sm">
            {search ? `No services matched "${search}". Try another keyword.` : 'No active services are registered in the platform yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>
      )}
    </div>
  );
};
