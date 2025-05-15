import { analyzeEmotion, getRecommendations } from '../services/api';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('analyzeEmotion', () => {
    test('calls the correct endpoint with the right parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          emotions: { joy: 0.8, optimism: 0.6 },
          primary_emotion: 'joy',
          summary: 'You are feeling joyful'
        }
      };
      
      mockedAxios.post.mockResolvedValue(mockResponse);
      
      // Call the function
      const result = await analyzeEmotion('I am feeling happy today', 'test-session-id');
      
      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/analyze',
        { text: 'I am feeling happy today' },
        { params: { session_id: 'test-session-id' } }
      );
      
      expect(result).toEqual(mockResponse.data);
    });

    test('handles errors correctly', async () => {
      // Mock error response
      mockedAxios.post.mockRejectedValue(new Error('Network error'));
      
      // Call the function and expect it to throw
      await expect(analyzeEmotion('I am feeling happy today', 'test-session-id'))
        .rejects.toThrow('Network error');
      
      // Verify the API was called
      expect(mockedAxios.post).toHaveBeenCalled();
    });
  });

  describe('getRecommendations', () => {
    test('calls the correct endpoint with the right parameters', async () => {
      // Mock emotion data
      const emotionData = {
        emotions: { joy: 0.8, optimism: 0.6 },
        primary_emotion: 'joy',
        summary: 'You are feeling joyful'
      };
      
      // Mock response
      const mockResponse = {
        data: {
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
        }
      };
      
      mockedAxios.post.mockResolvedValue(mockResponse);
      
      // Call the function
      const result = await getRecommendations(emotionData, 'test-session-id');
      
      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/recommend',
        emotionData,
        { params: { session_id: 'test-session-id' } }
      );
      
      expect(result).toEqual(mockResponse.data);
    });

    test('handles errors correctly', async () => {
      // Mock emotion data
      const emotionData = {
        emotions: { joy: 0.8, optimism: 0.6 },
        primary_emotion: 'joy',
        summary: 'You are feeling joyful'
      };
      
      // Mock error response
      mockedAxios.post.mockRejectedValue(new Error('Network error'));
      
      // Call the function and expect it to throw
      await expect(getRecommendations(emotionData, 'test-session-id'))
        .rejects.toThrow('Network error');
      
      // Verify the API was called
      expect(mockedAxios.post).toHaveBeenCalled();
    });
  });
});