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

        // Start with Rico's welcome message
        const welcomeMessage = createWelcomeMessage();
        setMessages([welcomeMessage]);

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

        // Initialize with Rico's welcome message
        const welcomeMessage = createWelcomeMessage();
        setMessages([welcomeMessage]);

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

  // State to store user name for personalized responses
  const [userName, setUserName] = useState<string | null>(null);

  // Create Rico's welcome message
  const createWelcomeMessage = (): Message => {
    return {
      id: uuidv4(),
      content: "Hello! I'm Rico, your Reckon AI assistant. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date(),
      type: 'text',
      confidence: 100,
      responseTime: 0,
      status: 'delivered',
    };
  };

  const extractUserName = (message: string): string | null => {
    const lowerMessage = message.toLowerCase();
    const patterns = [
      "my name is ",
      "i am ",
      "call me ",
      "i'm "
    ];

    for (const pattern of patterns) {
      if (lowerMessage.includes(pattern)) {
        const startIndex = lowerMessage.indexOf(pattern) + pattern.length;
        const namePart = message.substring(startIndex).trim();

        // Extract first word/name
        const nameMatch = namePart.match(/^([a-zA-Z][\w\s\-']*?)(?:\s|[.!?]|$)/);
        if (nameMatch) {
          const extractedName = nameMatch[1].trim();
          // Clean up common trailing words
          const stopWords = ["and", "but", "from", "here", "there"];
          const words = extractedName.split(' ');
          if (words.length > 0 && !stopWords.includes(words[words.length - 1].toLowerCase())) {
            return extractedName.split(' ')[0]; // Take first word as name
          }
        }
      }
    }
    return null;
  };

  const detectIntent = (message: string): string => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('my name is') || lowerMessage.includes('i am') || lowerMessage.includes('call me')) {
      return 'name_introduction';
    }
    if (['hello', 'hi', 'hey', 'good morning', 'good evening'].some(word => lowerMessage.includes(word))) {
      return 'greeting';
    }
    if (['erp', 'advantage'].some(word => lowerMessage.includes(word))) {
      return 'erp_query';
    }
    if (['gst', 'tax'].some(word => lowerMessage.includes(word))) {
      return 'gst_query';
    }
    if (['inventory', 'stock'].some(word => lowerMessage.includes(word))) {
      return 'inventory_query';
    }
    if (['billing', 'invoice'].some(word => lowerMessage.includes(word))) {
      return 'billing_query';
    }
    return 'general_query';
  };

  const generateMockResponse = useCallback((userMessage: string): string => {
    const intent = detectIntent(userMessage);

    // Handle name introduction
    if (intent === 'name_introduction') {
      const extractedName = extractUserName(userMessage);
      if (extractedName) {
        setUserName(extractedName);
        return `Nice to meet you, ${extractedName}! I'm Rico, your Reckon AI assistant. How can I help you today?`;
      } else {
        return `Nice to meet you! I'm Rico, your Reckon AI assistant. How can I help you today?`;
      }
    }

    // Handle greetings with personalization
    if (intent === 'greeting') {
      return `Hello${userName ? ' ' + userName : ''}! I'm Rico, your Reckon AI assistant. How can I help you today?`;
    }

    // Handle other intents
    if (intent === 'erp_query') {
      return `Great question about ERP advantages! Reckon ERP offers:\n\n• Integrated billing and inventory management\n• Real-time GST compliance\n• Multi-location support\n• Automated financial reporting\n• Cloud-based accessibility\n\nWould you like me to explain any specific feature in detail?`;
    }

    if (intent === 'gst_query') {
      return `For GST compliance, Reckon helps with:\n\n• Automatic GST calculation\n• GSTR-1, GSTR-3B filing\n• Input tax credit management\n• E-way bill generation\n• Compliance reports\n\nDo you need help with a specific GST return or compliance issue?`;
    }

    if (intent === 'inventory_query') {
      return `Reckon's inventory management includes:\n\n• Real-time stock tracking\n• Low stock alerts\n• Batch and serial number tracking\n• Multi-warehouse management\n• Purchase and sales integration\n\nWhat specific inventory challenge are you facing?`;
    }

    if (intent === 'billing_query') {
      return `Our billing system offers:\n\n• Professional invoice templates\n• Automatic tax calculations\n• Payment tracking\n• Recurring billing setup\n• Integration with payment gateways\n\nHow can I help with your billing requirements?`;
    }

    return `Thank you for your question about "${userMessage}". I'm here to help with all Reckon-related queries. Could you provide more specific details so I can give you the most relevant assistance?\n\nI can help with:\n• Billing and invoicing\n• GST compliance\n• Inventory management\n• Multi-branch operations\n• Technical support`;
  }, [userName]);

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
  }, [sessionId, generateMockResponse]);

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