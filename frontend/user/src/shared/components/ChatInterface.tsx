import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  Avatar,
  Chip,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { colors } from '../theme';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'action';
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
  placeholder?: string;
  suggestions?: string[];
  showContactOptions?: boolean;
  onContactAction?: (action: 'call' | 'email' | 'demo') => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isTyping = false,
  placeholder = "Ask about billing, GST, inventory...",
  suggestions = [],
  showContactOptions = false,
  onContactAction,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    onSendMessage(suggestion);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          minHeight: 0,
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              alignItems: 'flex-start',
              gap: 1,
            }}
          >
            {message.sender === 'assistant' && (
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: colors.primary.main,
                  fontSize: '0.875rem',
                }}
              >
                AI
              </Avatar>
            )}
            <Box
              sx={{
                maxWidth: '70%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: message.sender === 'user' ? colors.primary.main : colors.background.paper,
                  color: message.sender === 'user' ? 'white' : colors.text.primary,
                  border: message.sender === 'assistant' ? `1px solid ${colors.divider}` : 'none',
                  borderBottomRightRadius: message.sender === 'user' ? 4 : 16,
                  borderBottomLeftRadius: message.sender === 'assistant' ? 4 : 16,
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              </Paper>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 0.5, px: 1 }}
              >
                {formatTime(message.timestamp)}
              </Typography>
            </Box>
          </Box>
        ))}

        {isTyping && (
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: colors.primary.main,
                fontSize: '0.875rem',
              }}
            >
              AI
            </Avatar>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: colors.background.paper,
                border: `1px solid ${colors.divider}`,
                borderBottomLeftRadius: 4,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  AI is typing...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Box sx={{ p: 2, pt: 0 }}>
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1,
              maxHeight: { xs: 120, sm: 'none' },
              overflowY: { xs: 'auto', sm: 'visible' },
            }}
          >
            {suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                variant="outlined"
                onClick={() => handleSuggestionClick(suggestion)}
                sx={{
                  borderColor: colors.primary.main,
                  color: colors.primary.main,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  height: { xs: 'auto', sm: 32 },
                  '&:hover': {
                    bgcolor: colors.primary.main,
                    color: 'white',
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Contact Options */}
      {showContactOptions && (
        <Box sx={{ p: 2, pt: 0 }}>
          <Box
            sx={{
              display: 'flex',
              gap: { xs: 1, sm: 2 },
              flexWrap: 'wrap',
              flexDirection: { xs: 'column', sm: 'row' },
            }}
          >
            <Button
              variant="outlined"
              startIcon={<PhoneIcon />}
              onClick={() => onContactAction?.('call')}
              size="small"
              sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
            >
              <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
                Call: +91-522-XXXXXX
              </Box>
              <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>
                Call
              </Box>
            </Button>
            <Button
              variant="outlined"
              startIcon={<EmailIcon />}
              onClick={() => onContactAction?.('email')}
              size="small"
              sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
            >
              <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
                Email: support@reckonsales.in
              </Box>
              <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>
                Email
              </Box>
            </Button>
            <Button
              variant="contained"
              startIcon={<CalendarIcon />}
              onClick={() => onContactAction?.('demo')}
              size="small"
              sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
            >
              Book a Demo
            </Button>
          </Box>
        </Box>
      )}

      {/* Input Area */}
      <Box sx={{ p: 2, borderTop: `1px solid ${colors.divider}` }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            variant="outlined"
            placeholder={placeholder}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!inputValue.trim()}
            sx={{
              bgcolor: colors.primary.main,
              color: 'white',
              '&:hover': {
                bgcolor: colors.primary.dark,
              },
              '&:disabled': {
                bgcolor: colors.secondary.light,
              },
            }}
          >
            <SendIcon />
          </IconButton>
          <IconButton
            color="inherit"
            sx={{ color: colors.text.secondary }}
          >
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};