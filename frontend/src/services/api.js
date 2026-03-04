import axios from 'axios';

const api = axios.create({
  baseURL: '/api' // Updated baseURL from 'http://localhost:8000' to '/api'
});

// Function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response;
    throw new Error(`Error ${status}: ${data.message || 'An error occurred'}`);
  } else if (error.request) {
    throw new Error('No response received from the server.');
  } else {
    throw new Error(`Request error: ${error.message}`);
  }
};

// Health Check
export const getHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Prompts
export const getPrompts = async (params) => {
  try {
    const response = await api.get('/prompts', { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getPrompt = async (promptId) => {
  try {
    const response = await api.get(`/prompts/${promptId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const createPrompt = async (promptData) => {
  try {
    const response = await api.post('/prompts', promptData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const updatePrompt = async (promptId, promptData) => {
  try {
    const response = await api.put(`/prompts/${promptId}`, promptData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const patchPrompt = async (promptId, promptData) => {
  try {
    const response = await api.patch(`/prompts/${promptId}`, promptData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const deletePrompt = async (promptId) => {
  try {
    await api.delete(`/prompts/${promptId}`);
  } catch (error) {
    handleApiError(error);
  }
};

// Collections
export const getCollections = async () => {
  try {
    const response = await api.get('/collections');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getCollection = async (collectionId) => {
  try {
    const response = await api.get(`/collections/${collectionId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const createCollection = async (collectionData) => {
  try {
    const response = await api.post('/collections', collectionData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const deleteCollection = async (collectionId) => {
  try {
    await api.delete(`/collections/${collectionId}`);
  } catch (error) {
    handleApiError(error);
  }
};

// Versions
export const getPromptVersions = async (promptId) => {
  try {
    const response = await api.get(`/prompts/${promptId}/versions`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getPromptVersion = async (promptId, versionNumber) => {
  try {
    const response = await api.get(`/prompts/${promptId}/versions/${versionNumber}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const revertPromptVersion = async (promptId, versionNumber) => {
  try {
    const response = await api.post(`/prompts/${promptId}/versions/${versionNumber}/revert`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export default api;