import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EmotionAnalysis from '../pages/EmotionAnalysis';
import { analyzeEmotion, getRecommendations } from '../services/api';
import { AppProvider } from '../context/AppContext';

// Mock the API services
jest.mock('../services/api', () => ({
  analyzeEmotion: jest.fn(),
  getRecommendations: jest.fn()
}));

// Mock the context
jest.mock('../context/AppContext', () => ({
  AppProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useApp: () => ({ sessionId: 'test-session-id' })
}));

describe('EmotionAnalysis Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the component correctly', () => {
    render(<EmotionAnalysis />);
    
    expect(screen.getByText(/Women's Emotional Wellness Journey/i)).toBeInTheDocument();
    expect(screen.getByText(/Express Yourself in Our Women's Safe Space/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Analyze My Feelings/i })).toBeInTheDocument();
  });

  test('button is disabled when text area is empty', () => {
    render(<EmotionAnalysis />);
    
    const button = screen.getByRole('button', { name: /Analyze My Feelings/i });
    expect(button).toBeDisabled();
  });

  test('button is enabled when text area has content', () => {
    render(<EmotionAnalysis />);
    
    const textArea = screen.getByPlaceholderText(/How are you feeling today/i);
    fireEvent.change(textArea, { target: { value: 'I am feeling happy today' } });
    
    const button = screen.getByRole('button', { name: /Analyze My Feelings/i });
    expect(button).toBeEnabled();
  });

  test('analyzes emotions when button is clicked', async () => {
    // Mock API responses
    const mockEmotionResponse = {
      emotions: { joy: 0.8, optimism: 0.6 },
      primary_emotion: 'joy',
      summary: 'You are feeling joyful'
    };
    
    const mockRecommendationResponse = {
      activities: [
        {
          id: 'activity1',
          title: 'Mindful Breathing',
          description: 'A breathing technique',
          duration: '5 minutes',
          difficulty: 'beginner',
          benefits: ['Reduces stress'],
          steps: ['Step 1', 'Step 2'],
          emotional_context: 'This helps with joy'
        }
      ],
      explanation: 'These activities will help with joy'
    };
    
    (analyzeEmotion as jest.Mock).mockResolvedValue(mockEmotionResponse);
    (getRecommendations as jest.Mock).mockResolvedValue(mockRecommendationResponse);
    
    render(<EmotionAnalysis />);
    
    const textArea = screen.getByPlaceholderText(/How are you feeling today/i);
    fireEvent.change(textArea, { target: { value: 'I am feeling happy today' } });
    
    const button = screen.getByRole('button', { name: /Analyze My Feelings/i });
    fireEvent.click(button);
    
    // Verify loading state
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText(/Your Feminine Emotional Wisdom/i)).toBeInTheDocument();
      expect(screen.getByText(/JOY/i)).toBeInTheDocument();
      expect(screen.getByText(/Women's Wellness Recommendations/i)).toBeInTheDocument();
      expect(screen.getByText(/Mindful Breathing/i)).toBeInTheDocument();
    });
    
    // Verify API calls
    expect(analyzeEmotion).toHaveBeenCalledWith('I am feeling happy today', 'test-session-id');
    expect(getRecommendations).toHaveBeenCalledWith(mockEmotionResponse, 'test-session-id');
  });

  test('handles API errors gracefully', async () => {
    (analyzeEmotion as jest.Mock).mockRejectedValue(new Error('API error'));
    
    render(<EmotionAnalysis />);
    
    const textArea = screen.getByPlaceholderText(/How are you feeling today/i);
    fireEvent.change(textArea, { target: { value: 'I am feeling happy today' } });
    
    const button = screen.getByRole('button', { name: /Analyze My Feelings/i });
    fireEvent.click(button);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to analyze emotions/i)).toBeInTheDocument();
    });
  });
});