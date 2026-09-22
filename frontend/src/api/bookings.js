import apiClient from './client';

export const bookingsApi = {
  createBooking: async (bookingData) => {
    const response = await apiClient.post('/bookings', bookingData);
    return response.data;
  },

  getCustomerBookings: async (params = {}) => {
    const response = await apiClient.get('/bookings/my-bookings', { params });
    return response.data;
  },

  cancelBooking: async (id) => {
    const response = await apiClient.post(`/bookings/${id}/cancel`);
    return response.data;
  },
};
