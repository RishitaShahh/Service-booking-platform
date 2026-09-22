import apiClient from './client';

export const providersApi = {
  getDashboardSummary: async () => {
    const response = await apiClient.get('/providers/dashboard');
    return response.data;
  },

  getProviderBookings: async (params = {}) => {
    const response = await apiClient.get('/providers/bookings', { params });
    return response.data;
  },

  updateBookingStatus: async (id, status) => {
    const response = await apiClient.patch(`/providers/bookings/${id}/status`, { status });
    return response.data;
  },
};
