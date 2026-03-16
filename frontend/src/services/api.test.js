/**
 * Tests for API Service
 * Unit tests for classificationAPI functions
 */

import { classificationAPI, handleAPIError, formatResult } from '../services/api';

describe('classificationAPI', () => {
  // Mock fetch
  global.fetch = jest.fn();

  beforeEach(() => {
    fetch.mockClear();
  });

  describe('checkHealth', () => {
    test('should return healthy status when API responds with 200', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
      });

      const result = await classificationAPI.checkHealth();

      expect(result.ok).toBe(true);
      expect(result.status).toBe(200);
      expect(result.timestamp).toBeDefined();
    });

    test('should return unhealthy status when API responds with error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const result = await classificationAPI.checkHealth();

      expect(result.ok).toBe(false);
      expect(result.status).toBe(500);
    });

    test('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await classificationAPI.checkHealth();

      expect(result.ok).toBe(false);
      expect(result.error).toBe('Network error');
    });
  });

  describe('classifyPrimary', () => {
    test('should classify image and return result', async () => {
      const mockResult = {
        predicted_class: 'Guitarra_Acustica',
        confidence: 0.85,
        model_used: 'primary',
        processing_time_ms: 150,
        class_probabilities: {
          Bajo_Electrico: 0.05,
          Guitarra_Acustica: 0.85,
          Guitarra_Electrica: 0.08,
          Guitarra_Electroacustica: 0.02,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult,
      });

      const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
      const result = await classificationAPI.classifyPrimary(file);

      expect(result).toEqual(mockResult);
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/classify'),
        expect.objectContaining({ method: 'POST' })
      );
    });

    test('should throw error when API returns error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid image format' }),
      });

      const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });

      await expect(classificationAPI.classifyPrimary(file)).rejects.toThrow(
        'Invalid image format'
      );
    });

    test('should handle timeout', async () => {
      fetch.mockRejectedValueOnce(new Error('Timeout'));

      const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });

      await expect(classificationAPI.classifyPrimary(file)).rejects.toThrow('Timeout');
    });
  });

  describe('classifyAlternative', () => {
    test('should classify using alternative model', async () => {
      const mockResult = {
        predicted_class: 'Guitarra_Acustica',
        confidence: 0.80,
        model_used: 'alternative',
        processing_time_ms: 175,
        class_probabilities: {
          Bajo_Electrico: 0.08,
          Guitarra_Acustica: 0.80,
          Guitarra_Electrica: 0.10,
          Guitarra_Electroacustica: 0.02,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult,
      });

      const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
      const result = await classificationAPI.classifyAlternative(file);

      expect(result.model_used).toBe('alternative');
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/classify-alternative'),
        expect.anything()
      );
    });
  });

  describe('classifyEnsemble', () => {
    test('should classify using ensemble of models', async () => {
      const mockResult = {
        predicted_class: 'Guitarra_Acustica',
        confidence: 0.825,
        model_used: 'ensemble (2 models)',
        processing_time_ms: 320,
        class_probabilities: {
          Bajo_Electrico: 0.065,
          Guitarra_Acustica: 0.825,
          Guitarra_Electrica: 0.09,
          Guitarra_Electroacustica: 0.02,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult,
      });

      const file = new File(['dummy'], 'test.jpg', { type: 'image/jpeg' });
      const result = await classificationAPI.classifyEnsemble(file);

      expect(result.model_used).toContain('ensemble');
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/classify-ensemble'),
        expect.anything()
      );
    });
  });

  describe('getModelInfo', () => {
    test('should get model information', async () => {
      const mockInfo = {
        model_name: 'best_guitar_model.keras',
        input_shape: '(None, 224, 224, 3)',
        output_shape: '(None, 4)',
        parameters: 2250000,
        class_names: [
          'Bajo_Electrico',
          'Guitarra_Acustica',
          'Guitarra_Electrica',
          'Guitarra_Electroacustica',
        ],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockInfo,
      });

      const result = await classificationAPI.getModelInfo('best_guitar_model.keras');

      expect(result).toEqual(mockInfo);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/model-info'),
        expect.anything()
      );
    });
  });
});

describe('handleAPIError', () => {
  test('should return timeout message for AbortError', () => {
    const error = new Error('Abort');
    error.name = 'AbortError';

    const message = handleAPIError(error);

    expect(message).toBe('Request timeout - please try again');
  });

  test('should return network error message for TypeError', () => {
    const error = new TypeError('Failed to fetch');

    const message = handleAPIError(error);

    expect(message).toBe('Network error - unable to reach backend server');
  });

  test('should return error message from error object', () => {
    const error = new Error('Custom error message');

    const message = handleAPIError(error);

    expect(message).toBe('Custom error message');
  });

  test('should return default message when error has no message', () => {
    const error = {};

    const message = handleAPIError(error);

    expect(message).toBe('An unexpected error occurred');
  });
});

describe('formatResult', () => {
  test('should format classification result', () => {
    const result = {
      predicted_class: 'Guitarra_Acustica',
      confidence: 0.85,
      model_used: 'primary_model',
      processing_time_ms: 150,
      class_probabilities: {
        Bajo_Electrico: 0.05,
        Guitarra_Acustica: 0.85,
        Guitarra_Electrica: 0.08,
        Guitarra_Electroacustica: 0.02,
      },
    };

    const formatted = formatResult(result);

    expect(formatted.predicted_class).toBe('Guitarra Acustica');
    expect(formatted.confidence_percentage).toBe('85.00');
    expect(formatted.processing_time_seconds).toBe('0.150');
    expect(formatted.class_probabilities_formatted).toHaveLength(4);
    expect(formatted.class_probabilities_formatted[0].name).toBe('Guitarra Acustica');
    expect(formatted.class_probabilities_formatted[0].percentage).toBe('85.0');
  });

  test('should handle missing class_probabilities', () => {
    const result = {
      predicted_class: 'Guitarra_Acustica',
      confidence: 0.85,
      model_used: 'primary_model',
      processing_time_ms: 150,
    };

    const formatted = formatResult(result);

    expect(formatted.class_probabilities_formatted).toEqual([]);
  });

  test('should format class names with underscores to spaces', () => {
    const result = {
      predicted_class: 'Guitarra_Electroacustica',
      confidence: 0.9,
      model_used: 'ensemble',
      processing_time_ms: 200,
      class_probabilities: {
        Guitarra_Electroacustica: 0.9,
      },
    };

    const formatted = formatResult(result);

    expect(formatted.predicted_class).toBe('Guitarra Electroacustica');
    expect(formatted.class_probabilities_formatted[0].name).toBe('Guitarra Electroacustica');
  });
});
