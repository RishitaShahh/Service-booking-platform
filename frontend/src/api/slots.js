import apiClient from './client';

export const slotsApi = {
  getAvailableSlots: async (params = {}) => {
    const response = await apiClient.get('/slots', { params });
    return response.data;
  },

  getProviderSlots: async () => {
    const response = await apiClient.get('/slots/provider/my-slots');
    return response.data;
  },

  createSlot: async (slotData) => {
    const response = await apiClient.post('/slots', slotData);
    return response.data;
  },

  batchCreateSlots: async (batchData) => {
    const response = await apiClient.post('/slots/batch', batchData);
    return response.data;
  },

  deleteSlot: async (id) => {
    const response = await apiClient.delete(`/slots/${id}`);
    return response.data;
  },
};
