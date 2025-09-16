import React, { useState, useEffect } from 'react';
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
    // Initialize chat session first
    const initializeSession = async () => {
      try {
        const session = await ChatApiService.createSession({
          user_id: 1, // Default user for now
          channel: 'web',
          language: 'en',
        });
        setSessionId(session.id);

        // Add welcome message
        const welcomeMessage: Message = {
          id: uuidv4(),
          content: "Namaste! Welcome to Reckon Support. I can help you with billing, GST compliance, inventory management, and more. How can I assist you today?",
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
        };
        setMessages([welcomeMessage]);

        // Handle initial message from navigation state
        const initialMessage = location.state?.initialMessage;
        if (initialMessage) {
          setTimeout(() => {
            handleSendMessage(initialMessage);
          }, 500);
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
        // Fallback to a temporary session ID
        setSessionId(Date.now());

        // Add welcome message anyway
        const welcomeMessage: Message = {
          id: uuidv4(),
          content: "Namaste! Welcome to Reckon Support. I can help you with billing, GST compliance, inventory management, and more. How can I assist you today?",
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
        };
        setMessages([welcomeMessage]);
      }
    };

    initializeSession();
  }, [location.state]);

  const handleSendMessage = async (content: string) => {
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
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000);
    }
  };

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
      showConnectionStatus={true}
      connectionStatus="connected"
      showLanguageSelector={true}
      currentUser={{ name: "Profile" }}
    >
      <Box
        sx={{
          height: { xs: 'calc(100vh - 180px)', sm: 'calc(100vh - 200px)' },
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