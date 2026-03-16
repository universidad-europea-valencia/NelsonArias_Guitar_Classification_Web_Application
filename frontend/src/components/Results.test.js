/**
 * Tests for Results Component
 * Unit tests for result display and formatting
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Results from '../components/Results';

describe('Results Component', () => {
  const mockResult = {
    predicted_class: 'Guitarra_Acustica',
    confidence: 0.85,
    model_used: 'best_guitar_model',
    processing_time_ms: 150.5,
    class_probabilities: {
      Bajo_Electrico: 0.05,
      Guitarra_Acustica: 0.85,
      Guitarra_Electrica: 0.08,
      Guitarra_Electroacustica: 0.02,
    },
  };

  test('should not render when result is null', () => {
    const { container } = render(<Results result={null} />);
    expect(container.firstChild).toBeNull();
  });

  test('should render results card when result is provided', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText(/Classification Result/i)).toBeInTheDocument();
  });

  test('should display guitar type with formatted name', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText(/Guitarra Acustica/)).toBeInTheDocument();
  });

  test('should display confidence percentage', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText('85.00%')).toBeInTheDocument();
  });

  test('should display all class probabilities', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText(/Bajo Electrico/)).toBeInTheDocument();
    expect(screen.getByText(/Guitarra Electrica/)).toBeInTheDocument();
    expect(screen.getByText(/Guitarra Electroacustica/)).toBeInTheDocument();
  });

  test('should display model used', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText('best_guitar_model')).toBeInTheDocument();
  });

  test('should display processing time', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText('150.50ms')).toBeInTheDocument();
  });

  test('should have toggle details button', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText(/Show Details|Hide Details/)).toBeInTheDocument();
  });

  test('should display confidence level badge', () => {
    render(<Results result={mockResult} />);
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  test('should render results with animation', () => {
    const { container } = render(<Results result={mockResult} />);
    const resultsCard = container.querySelector('.results-card');
    expect(resultsCard).toHaveClass('results-card');
  });

  test('should format class names by replacing underscores', () => {
    render(<Results result={mockResult} />);
    const guitarName = screen.getByText(/Guitarra Acustica/);
    expect(guitarName.textContent).not.toContain('_');
  });

  test('should display confidence level as "Very High" for confidence >= 0.9', () => {
    const highConfidenceResult = { ...mockResult, confidence: 0.95 };
    render(<Results result={highConfidenceResult} />);
    expect(screen.getByText('Very High')).toBeInTheDocument();
  });

  test('should display confidence level as "Moderate" for confidence 0.5-0.7', () => {
    const moderateResult = { ...mockResult, confidence: 0.6 };
    render(<Results result={moderateResult} />);
    expect(screen.getByText('Moderate')).toBeInTheDocument();
  });

  test('should display class probabilities in order of confidence', () => {
    render(<Results result={mockResult} />);
    const percentages = screen.getAllByText(/%/);
    // First percentage should be the highest (85.0%)
    expect(percentages[0].textContent).toBe('85.0%');
  });

  test('should handle result with missing class_probabilities', () => {
    const resultWithoutProbs = {
      ...mockResult,
      class_probabilities: undefined,
    };
    render(<Results result={resultWithoutProbs} />);
    expect(screen.getByText(/Classification Result/i)).toBeInTheDocument();
  });
});
