import apiClient from './client';

export const servicesApi = {
  getServices: async (params = {}) => {
    const response = await apiClient.get('/services', { params });
    return response.data;
  },

  getServiceById: async (id) => {
    const response = await apiClient.get(`/services/${id}`);
    return response.data;
  },

  getProviderServices: async () => {
    const response = await apiClient.get('/services/provider/my-services');
    return response.data;
  },

  createService: async (serviceData) => {
    const response = await apiClient.post('/services', serviceData);
    return response.data;
  },

  updateService: async (id, serviceData) => {
    const response = await apiClient.put(`/services/${id}`, serviceData);
    return response.data;
  },

  deleteService: async (id) => {
    const response = await apiClient.delete(`/services/${id}`);
    return response.data;
  },
};
