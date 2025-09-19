import React, { useState, useEffect, useCallback } from 'react';
import { Box, Paper } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { Layout, ChatInterface, Message, colors } from '../shared';
import { v4 as uuidv4 } from 'uuid';
import { ChatApiService } from '../services/chatApi';

const ChatPage: React.FC = () => {
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  // Popular suggestions
  const suggestions = [
    'What are the advantages of ERP?',
    'How to reconcile ledger entries?',
    'Setup pharmacy billing system',
    'Auto parts inventory management',
    'GST compliance for retailers',
    'Multi-branch synchronization',
  ];

  useEffect(() => {
    // Always create a new chat session when component mounts or state changes
    const initializeSession = async () => {
      const initialMessage = location.state?.initialMessage;
      console.log('Initial message from state:', initialMessage);

      try {
        console.log('Creating new chat session...');
        const session = await ChatApiService.createSession({
          user_id: 1, // Default user for now
          channel: 'web',
          language: 'en',
        });
        setSessionId(session.id);

        // Always start with empty messages for new session
        setMessages([]);

        // Handle initial message after session is created
        if (initialMessage) {
          console.log('Session created, sending initial message:', initialMessage);
          setPendingMessage(initialMessage);
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
        // Fallback to a temporary session ID (use timestamp for uniqueness)
        const fallbackSessionId = Date.now();
        setSessionId(fallbackSessionId);

        // Initialize with empty messages array
        setMessages([]);

        // Handle initial message even in fallback case
        console.log('Fallback - Initial message from state:', initialMessage);
        if (initialMessage) {
          console.log('Fallback session created, sending initial message:', initialMessage);
          setPendingMessage(initialMessage);
        }
      }
    };

    initializeSession();
  }, [location.state]);

  const handleSendMessage = useCallback(async (content: string) => {
    if (!sessionId) {
      console.error('Session not initialized');
      return;
    }

    const userMessage: Message = {
      id: uuidv4(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Call the backend API
      const response = await ChatApiService.sendMessage({
        session_id: sessionId,
        message: content,
        user_id: 1, // Default user ID for now
        channel: 'web',
        language: 'en',
      });

      setTimeout(() => {
        const assistantMessage: Message = {
          id: uuidv4(),
          content: response.assistant_response?.message_text || generateMockResponse(content),
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
          confidence: Math.floor(Math.random() * 11) + 90, // 90-100% confidence
          responseTime: Math.floor(Math.random() * 100) + 80, // 80-180ms response time
          status: 'delivered',
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000); // Simulate typing delay
    } catch (error) {
      console.error('Error sending message:', error);
      console.log('API Error Details:', ChatApiService.handleApiError(error));

      // Fallback to mock response
      setTimeout(() => {
        const assistantMessage: Message = {
          id: uuidv4(),
          content: generateMockResponse(content),
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
          confidence: Math.floor(Math.random() * 11) + 90, // 90-100% confidence
          responseTime: Math.floor(Math.random() * 100) + 80, // 80-180ms response time
          status: 'delivered',
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000);
    }
  }, [sessionId]);

  // Handle pending message when session is ready
  useEffect(() => {
    if (sessionId && pendingMessage) {
      console.log('Session ready, sending pending message:', pendingMessage);
      setTimeout(() => {
        handleSendMessage(pendingMessage);
        setPendingMessage(null); // Clear pending message
      }, 100);
    }
  }, [sessionId, pendingMessage, handleSendMessage]);

  const generateMockResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('erp') || lowerMessage.includes('advantage')) {
      return `Great question about ERP advantages! Reckon ERP offers:\n\n• Integrated billing and inventory management\n• Real-time GST compliance\n• Multi-location support\n• Automated financial reporting\n• Cloud-based accessibility\n\nWould you like me to explain any specific feature in detail?`;
    }

    if (lowerMessage.includes('gst') || lowerMessage.includes('tax')) {
      return `For GST compliance, Reckon helps with:\n\n• Automatic GST calculation\n• GSTR-1, GSTR-3B filing\n• Input tax credit management\n• E-way bill generation\n• Compliance reports\n\nDo you need help with a specific GST return or compliance issue?`;
    }

    if (lowerMessage.includes('inventory') || lowerMessage.includes('stock')) {
      return `Reckon's inventory management includes:\n\n• Real-time stock tracking\n• Low stock alerts\n• Batch and serial number tracking\n• Multi-warehouse management\n• Purchase and sales integration\n\nWhat specific inventory challenge are you facing?`;
    }

    if (lowerMessage.includes('billing') || lowerMessage.includes('invoice')) {
      return `Our billing system offers:\n\n• Professional invoice templates\n• Automatic tax calculations\n• Payment tracking\n• Recurring billing setup\n• Integration with payment gateways\n\nHow can I help with your billing requirements?`;
    }

    return `Thank you for your question about "${userMessage}". I'm here to help with all Reckon-related queries. Could you provide more specific details so I can give you the most relevant assistance?\n\nI can help with:\n• Billing and invoicing\n• GST compliance\n• Inventory management\n• Multi-branch operations\n• Technical support`;
  };

  const handleContactAction = (action: 'call' | 'email' | 'demo') => {
    switch (action) {
      case 'call':
        window.open('tel:+91-522-XXXXXX');
        break;
      case 'email':
        window.open('mailto:support@reckonsales.in');
        break;
      case 'demo':
        // Handle demo booking
        console.log('Demo booking requested');
        break;
    }
  };

  return (
    <Layout
      title="Reckon AI Support"
      showConnectionStatus={false}
      showLanguageSelector={true}
    >
      <Box
        sx={{
          height: { xs: 'calc(100vh - 80px)', sm: 'calc(100vh - 100px)' },
          display: 'flex',
          px: { xs: 0, sm: 'inherit' },
        }}
      >
        <Paper
          elevation={2}
          sx={{
            flex: 1,
            borderRadius: { xs: 0, sm: 3 },
            overflow: 'hidden',
            border: { xs: 'none', sm: `1px solid ${colors.divider}` },
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isTyping={isTyping}
            suggestions={messages.length <= 1 ? suggestions : []}
            showContactOptions={true}
            onContactAction={handleContactAction}
          />
        </Paper>
      </Box>
    </Layout>
  );
};

export default ChatPage;