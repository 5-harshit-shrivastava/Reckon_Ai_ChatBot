import React, { useState, useEffect, useCallback, useRef } from 'react';
// CACHE BUST - FORCE REDEPLOY v0.1.2 - 2025-10-30
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
  // Flow state: choose -> existing input -> new customer suggestions/chat
  const [flowStage, setFlowStage] = useState<'choose' | 'existing' | 'chat'>('choose');
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);

  // Popular suggestions shown inside chat for new customers (full list)
  const popularSuggestions = [
    'What are the advantages of ERP?',
    'How to reconcile ledger entries?',
    'Setup pharmacy billing system',
    'Auto parts inventory management',
    'GST compliance for retailers',
    'Multi-branch synchronization',
    'How to file GST returns?',
    'Inventory tracking best practices',
    'Setting up barcode scanning',
    'Managing supplier payments',
    'Creating purchase orders',
    'Generating sales reports',
    'Setting up tax rates',
    'Managing customer accounts',
    'Backup and restore data',
    'User permissions setup',
    'Integration with banks',
    'Managing multiple locations',
    'Discount and pricing rules',
    'Setting up payment terms',
    'Handling returns and refunds',
    'Managing stock transfers',
    'Setting up automated alerts',
    'Customizing invoice templates',
    'Managing employee access',
    'Setting up recurring billing',
    'Handling damaged goods',
    'Managing vendor catalogs',
    'Setting up approval workflows',
    'Tracking expenses',
    'Managing cash flow',
    'Setting up credit limits',
    'Handling foreign currency',
    'Managing seasonal inventory',
    'Setting up loyalty programs',
    'Batch processing invoices',
    'Managing service contracts',
    'Setting up manufacturing',
    'Handling warranty claims',
    'Managing project billing',
    'Setting up commission tracking',
    'Handling subscription billing',
    'Managing digital receipts',
    'Setting up mobile access',
    'Handling partial payments',
    'Managing supplier discounts',
    'Setting up automatic backups',
    'Handling tax exemptions',
    'Managing product bundles',
    'Setting up price lists',
    'Handling split billing',
    'Managing delivery tracking',
    'Setting up quality control',
    'Handling emergency procedures',
    'Managing audit trails',
    'Setting up performance metrics',
    'Handling system updates',
    'Managing data migration',
    'Setting up integration APIs',
    'Handling compliance reporting'
  ];

  const initializedRef = useRef(false);
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    // Show welcome message immediately
    const welcomeMessage = createWelcomeMessage();
    setMessages([welcomeMessage]);
    setFlowStage('choose');

    // Create session in background
    const initializeSession = async () => {
      const initialMessage = location.state?.initialMessage;
      try {
        const session = await ChatApiService.createSession({
          user_id: 1,
          channel: 'web',
          language: 'en',
        });
        setSessionId(session.id);

        if (initialMessage) {
          setPendingMessage(initialMessage);
        }
      } catch (error) {
        console.log('Using fallback session ID');
        const fallbackSessionId = Date.now();
        setSessionId(fallbackSessionId);

        if (initialMessage) {
          setPendingMessage(initialMessage);
        }
      }
    };

    initializeSession();
  }, [location.state?.initialMessage]);

  // Create welcome + choice message combined (updated)
  const createWelcomeMessage = (): Message => {
    return {
      id: uuidv4(),
      content: "Hello! I'm Rico, your Reckon AI assistant.\nAre you an existing customer or a new customer? Please choose below.",
      sender: 'assistant',
      timestamp: new Date(),
      type: 'text',
      confidence: 100,
      responseTime: 0,
      status: 'delivered',
    };
  };

  // Simple validators
  const isValidLicense = (value: string) => /^[0-9]{5,}$/.test(value.trim());
  const isValidMobile = (value: string) => /^[0-9]{10}$/.test(value.trim());

  const handleSendMessage = useCallback(async (content: string) => {
    if (!sessionId) {
      console.error('Session not initialized');
      return;
    }

    // Intercept flow for customer selection and validation before hitting API
    if (flowStage === 'choose') {
      const normalized = content.toLowerCase();
      const isExisting = normalized.includes('existing');
      const isNew = normalized.includes('new');

      if (isExisting || (!isNew && content.trim().toLowerCase() === 'existing customer')) {
        // Push user message then assistant prompt for input
        const userMsg: Message = { id: uuidv4(), content, sender: 'user', timestamp: new Date(), type: 'text' };
        const prompt: Message = {
          id: uuidv4(),
          content: 'Please enter your License Number or your 10-digit Registered Mobile Number.',
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
        };
        setMessages(prev => [...prev, userMsg, prompt]);
        setSelectedChoice('Existing Customer');
        setFlowStage('existing');
        return;
      }

      if (isNew || (!isExisting && content.trim().toLowerCase() === 'new customer')) {
        const userMsg: Message = { id: uuidv4(), content, sender: 'user', timestamp: new Date(), type: 'text' };
        const msg: Message = {
          id: uuidv4(),
          content: 'Great! Here are some popular questions to get you started.',
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
        };
        setMessages(prev => [...prev, userMsg, msg]);
        setSelectedChoice('New Customer');
        setFlowStage('chat');
        return;
      }
      // If neither, allow normal processing
    }

    if (flowStage === 'existing') {
      const trimmed = content.trim();
      const valid = isValidLicense(trimmed) || isValidMobile(trimmed);
      const userMsg: Message = { id: uuidv4(), content, sender: 'user', timestamp: new Date(), type: 'text' };
      setMessages(prev => [...prev, userMsg]);
      setIsTyping(true);

      // Hardcoded success/failure for now
      setTimeout(() => {
        const assistantMessage: Message = {
          id: uuidv4(),
          content: valid
            ? 'Thanks! Your details were verified successfully. Here are some suggestions based on your business type.'
            : 'That did not look right. You can re-enter correct details, or continue as a new customer.',
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
          status: 'delivered',
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
        if (valid) {
          const suggestionsMsg: Message = {
            id: uuidv4(),
            content: 'Suggested topics: Billing setup, GST returns, Inventory optimization. Choose one or ask your question.',
            sender: 'assistant',
            timestamp: new Date(),
            type: 'text',
          };
          setMessages(prev => [...prev, suggestionsMsg]);
          setFlowStage('chat');
        } else {
          const nextMsg: Message = {
            id: uuidv4(),
            content: 'Would you like to try again or proceed as a new customer?',
            sender: 'assistant',
            timestamp: new Date(),
            type: 'text',
          };
          setMessages(prev => [...prev, nextMsg]);
          setFlowStage('choose');
          setSelectedChoice(null);
        }
      }, 600);
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
        // Use the real API response, log for debugging
        console.log('API Response:', response);
        const apiResponse = response.assistant_response?.message_text || response.response;
        
        const assistantMessage: Message = {
          id: uuidv4(),
          content: apiResponse || `API Error: No response received. Response: ${JSON.stringify(response)}`,
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
          confidence: response.confidence ? Math.round(response.confidence * 100) : 90,
          responseTime: response.processing_time_ms || 100,
          status: 'delivered',
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000); // Simulate typing delay
    } catch (error) {
      console.error('Error sending message:', error);
      console.log('API Error Details:', ChatApiService.handleApiError(error));

      // Show the actual error instead of fallback
      setTimeout(() => {
        const assistantMessage: Message = {
          id: uuidv4(),
          content: `API Error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check console for details.`,
          sender: 'assistant',
          timestamp: new Date(),
          type: 'text',
          confidence: 0, // Low confidence for error
          responseTime: 0,
          status: 'failed',
        };

        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000 + Math.random() * 1000);
    }
  }, [sessionId, flowStage]);

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
            suggestions={
              flowStage === 'choose' && messages.length > 0
                ? ['Existing Customer', 'New Customer']
                : flowStage === 'chat'
                ? popularSuggestions
                : []
            }
            suggestionsMarquee={flowStage === 'chat'}
            selectedSuggestion={selectedChoice || undefined}
            showContactOptions={true}
            onContactAction={handleContactAction}
          />
        </Paper>
      </Box>
    </Layout>
  );
};

export default ChatPage;