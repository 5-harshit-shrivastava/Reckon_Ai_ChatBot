import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased to 60 seconds for large content processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types matching the backend models
export interface DashboardStats {
  total_conversations: number;
  total_conversations_change: string;
  knowledge_base_entries: number;
  knowledge_base_entries_change: string;
  total_users: number;
  total_users_change: string;
  success_rate: number;
  success_rate_change: string;
}

export interface RecentActivity {
  id: number;
  action: string;
  details: string;
  timestamp: string;
  status: string;
}

export interface TopQuery {
  query: string;
  count: number;
  category: string;
}

export interface KnowledgeBaseEntry {
  id: number;
  title: string;
  document_type: string;
  industry_type?: string;
  language: string;
  is_active: boolean;
  created_at: string;
  chunk_count: number;
}

export interface KnowledgeBaseCreate {
  title: string;
  content: string;
  document_type: string;
  industry_type?: string;
  language?: string;
}

export interface KnowledgeBaseUpdate {
  title?: string;
  content?: string;
  document_type?: string;
  industry_type?: string;
  language?: string;
  is_active?: boolean;
}

export interface SystemStatus {
  database_status: string;
  api_services_status: string;
  vector_store_status: string;
  total_documents: number;
  total_chunks: number;
  total_sessions: number;
  last_updated: string;
}

// API Service Class
export class AdminApiService {
  // Dashboard endpoints
  static async getDashboardStats(): Promise<DashboardStats> {
    try {
      const response = await api.get('/api/admin/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  static async getRecentActivities(limit = 10): Promise<RecentActivity[]> {
    try {
      const response = await api.get(`/api/admin/dashboard/recent-activities?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      throw error;
    }
  }

  static async getTopQueries(limit = 5): Promise<TopQuery[]> {
    try {
      const response = await api.get(`/api/admin/dashboard/top-queries?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching top queries:', error);
      throw error;
    }
  }

  // Knowledge Base CRUD operations
  static async getKnowledgeBaseEntries(
    skip = 0,
    limit = 100,
    search?: string,
    documentType?: string
  ): Promise<KnowledgeBaseEntry[]> {
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });

      if (search) params.append('search', search);
      if (documentType) params.append('document_type', documentType);

      const response = await api.get(`/api/admin/knowledge-base?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching knowledge base entries:', error);
      throw error;
    }
  }

  static async createKnowledgeBaseEntry(entry: KnowledgeBaseCreate): Promise<{ id: number; message: string; status: string }> {
    try {
      const response = await api.post('/api/admin/knowledge-base', entry);
      return response.data;
    } catch (error) {
      console.error('Error creating knowledge base entry:', error);
      throw error;
    }
  }

  static async updateKnowledgeBaseEntry(
    entryId: number,
    entry: KnowledgeBaseUpdate
  ): Promise<{ id: number; message: string; status: string }> {
    try {
      const response = await api.put(`/api/admin/knowledge-base/${entryId}`, entry);
      return response.data;
    } catch (error) {
      console.error('Error updating knowledge base entry:', error);
      throw error;
    }
  }

  static async deleteKnowledgeBaseEntry(entryId: number): Promise<{ id: number; message: string; status: string }> {
    try {
      const response = await api.delete(`/api/admin/knowledge-base/${entryId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting knowledge base entry:', error);
      throw error;
    }
  }

  static async getKnowledgeBaseEntry(entryId: number): Promise<any> {
    try {
      const response = await api.get(`/api/admin/knowledge-base/${entryId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching knowledge base entry:', error);
      throw error;
    }
  }

  // System status
  static async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await api.get('/api/admin/system/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching system status:', error);
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

export default AdminApiService;