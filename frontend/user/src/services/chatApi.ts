import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout for chat responses
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for chat API matching backend schemas
export interface SendMessageRequest {
  session_id: number;
  message: string;
  user_id?: number;
  channel?: 'web' | 'mobile' | 'whatsapp';
  language?: 'en' | 'hi';
}

export interface ChatMessage {
  id: number;
  session_id: number;
  message_text: string;
  message_type: 'user' | 'assistant' | 'system';
  intent?: string;
  confidence_score?: number;
  escalated_to_human: boolean;
  response_time_ms?: number;
  created_at: string;
}

export interface SendMessageResponse {
  success: boolean;
  message: string;
  data: Record<string, any>;
  user_message: ChatMessage;
  assistant_response?: ChatMessage;
  session_info: ChatSession;
}

export interface ChatSession {
  id: number;
  user_id: number;
  session_id: string;
  channel: string;
  language: string;
  is_active: boolean;
  created_at: string;
  ended_at?: string;
  message_count?: number;
}

export interface CreateSessionRequest {
  user_id: number;
  channel?: 'web' | 'mobile' | 'whatsapp';
  language?: 'en' | 'hi';
}

// Chat API Service Class
export class ChatApiService {
  // Send a message to the chatbot
  static async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    try {
      const response = await api.post('/api/chat/messages/send', request);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  // Create a new chat session
  static async createSession(request: CreateSessionRequest): Promise<ChatSession> {
    try {
      const response = await api.post('/api/chat/sessions/', request);
      return response.data.data.session;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  // Get user's chat sessions
  static async getSessions(userId: number): Promise<ChatSession[]> {
    try {
      const response = await api.get(`/api/chat/sessions/?user_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sessions:', error);
      throw error;
    }
  }

  // Health check
  static async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  // Helper method to handle API errors
  static handleApiError(error: any): string {
    if (error.response) {
      // Server responded with error status
      return error.response.data?.detail || error.response.statusText || 'An error occurred';
    } else if (error.request) {
      // Request made but no response received
      return 'Unable to connect to server. Please check if the backend is running.';
    } else {
      // Something else happened
      return error.message || 'An unexpected error occurred';
    }
  }
}

export default ChatApiService;