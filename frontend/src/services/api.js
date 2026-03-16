/**
 * API Service for Guitar Classification Platform
 * Handles all communication with the backend API
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

/**
 * Helper function to make API requests with timeout
 */
const fetchWithTimeout = async (url, options = {}, timeout = API_TIMEOUT) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

/**
 * Classification API Service
 */
export const classificationAPI = {
  /**
   * Check API health status
   */
  checkHealth: async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/health`);
      return {
        ok: response.ok,
        status: response.status,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        ok: false,
        status: null,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  },

  /**
   * Classify image using primary model
   * @param {File} file - Image file to classify
   * @returns {Promise} Classification result
   */
  classifyPrimary: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/classify`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to classify image`);
    }

    return response.json();
  },

  /**
   * Classify image using alternative model
   * @param {File} file - Image file to classify
   * @returns {Promise} Classification result
   */
  classifyAlternative: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/classify-alternative`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to classify image`);
    }

    return response.json();
  },

  /**
   * Classify image using ensemble of models
   * @param {File} file - Image file to classify
   * @returns {Promise} Classification result
   */
  classifyEnsemble: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/classify-ensemble`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to classify image`);
    }

    return response.json();
  },

  /**
   * Get model information
   * @param {string} modelName - Name of the model
   * @returns {Promise} Model information
   */
  getModelInfo: async (modelName) => {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/model-info?model_name=${encodeURIComponent(modelName)}`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to get model info`);
    }

    return response.json();
  },
};

/**
 * Error handler utility
 */
export const handleAPIError = (error) => {
  if (error.name === 'AbortError') {
    return 'Request timeout - please try again';
  }
  if (error instanceof TypeError) {
    return 'Network error - unable to reach backend server';
  }
  return error.message || 'An unexpected error occurred';
};

/**
 * Result formatter utility
 */
export const formatResult = (result) => {
  return {
    ...result,
    predicted_class: result.predicted_class.replace(/_/g, ' '),
    confidence_percentage: (result.confidence * 100).toFixed(2),
    processing_time_seconds: (result.processing_time_ms / 1000).toFixed(3),
    class_probabilities_formatted: Object.entries(result.class_probabilities || {}).map(
      ([className, probability]) => ({
        name: className.replace(/_/g, ' '),
        value: probability,
        percentage: (probability * 100).toFixed(1),
      })
    ),
  };
};

export default classificationAPI;
