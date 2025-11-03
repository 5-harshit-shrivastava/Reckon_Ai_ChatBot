import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  Avatar,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'action';
  confidence?: number;
  responseTime?: number;
  status?: 'delivered' | 'pending' | 'failed';
  image?: {
    file?: File;
    preview: string;
    suggestedQuestions?: string[];
    documentInfo?: {
      type: string;
      filename: string;
      key_information: string;
    };
  };
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
  placeholder?: string;
  suggestions?: string[];
  showContactOptions?: boolean;
  onContactAction?: (action: 'call' | 'email' | 'demo') => void;
  selectedSuggestion?: string;
  suggestionsMarquee?: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isTyping = false,
  placeholder = "Type your message...",
  suggestions = [],
  selectedSuggestion,
  suggestionsMarquee = false,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzingImage, setIsAnalyzingImage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file');
      return;
    }

    // Validate file size (5MB limit for Vercel compatibility)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    // Create preview
    const preview = URL.createObjectURL(file);
    setImagePreview(preview);
    setSelectedImage(file);
    setIsAnalyzingImage(true);

    try {
      // Upload and analyze image
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'https://bckreckon.vercel.app'}/api/chat/analyze-image`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Send clean message with extracted error text
        const errorText = result.questions && result.questions[0] ? result.questions[0] : "Error text extracted from image";
        onSendMessage(`� ${errorText}`);
        
      } else {
        console.error('Image analysis failed:', result.error);
        alert('Failed to analyze image. Please try again.');
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
      alert('Error uploading image. Please check your connection and try again.');
    } finally {
      setIsAnalyzingImage(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleImageButtonClick = () => {
    fileInputRef.current?.click();
  };

  const clearImagePreview = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setImagePreview(null);
    setSelectedImage(null);
    setIsAnalyzingImage(false);
  };

  const getTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes === 0) {
      return 'less than a minute ago';
    } else if (diffInMinutes === 1) {
      return '1 minute ago';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else {
      const hours = Math.floor(diffInMinutes / 60);
      return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          p: 3,
          pb: 0, // Remove bottom padding to avoid double spacing
          display: 'flex',
          flexDirection: 'column',
          gap: 4,
          minHeight: 0,
          bgcolor: '#ffffff',
        }}
      >
        {messages.map((message) => (
          <Box key={message.id}>
            {message.sender === 'assistant' ? (
              // Assistant Message
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Avatar
                  sx={{
                    width: 44,
                    height: 44,
                    bgcolor: '#f8f9fa',
                    color: '#3c4043',
                    border: '1px solid #dadce0',
                  }}
                >
                  <BotIcon sx={{ fontSize: 22 }} />
                </Avatar>
                <Box sx={{ flex: 1, maxWidth: '80%' }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2,
                      bgcolor: '#f1f3f4',
                      border: '1px solid #e8eaed',
                      borderTopLeftRadius: 4,
                      mb: 1,
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.5,
                        color: '#202124',
                        fontSize: '14px',
                      }}
                    >
                      {message.content}
                    </Typography>
                  </Paper>

                  {/* Assistant Message Status */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, px: 1 }}>
                    <Typography variant="caption" sx={{ color: '#5f6368', fontSize: '12px' }}>
                      {getTimeAgo(message.timestamp)}
                    </Typography>
                    {message.confidence && (
                      <Typography variant="caption" sx={{ color: '#137333', fontSize: '12px', fontWeight: 500 }}>
                        {message.confidence}% confidence
                      </Typography>
                    )}
                    {message.responseTime && (
                      <Typography variant="caption" sx={{ color: '#5f6368', fontSize: '12px' }}>
                        {message.responseTime}ms
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Box>
            ) : (
              // User Message
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-start', gap: 2 }}>
                <Box sx={{ maxWidth: '80%', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                  {/* Image Preview if present */}
                  {message.image && (
                    <Box sx={{ mb: 1, borderRadius: 2, overflow: 'hidden', maxWidth: '300px' }}>
                      <img 
                        src={message.image.preview} 
                        alt={message.image.documentInfo?.filename || "Uploaded document"}
                        style={{
                          width: '100%',
                          height: 'auto',
                          maxHeight: '200px',
                          objectFit: 'cover',
                          borderRadius: '8px',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                      />
                      {message.image.documentInfo && (
                        <Box sx={{ 
                          p: 1, 
                          bgcolor: 'rgba(66, 133, 244, 0.1)', 
                          borderRadius: '0 0 8px 8px',
                          border: '1px solid #e8eaed'
                        }}>
                          <Typography variant="caption" sx={{ color: '#5f6368', fontSize: '11px' }}>
                            📄 {message.image.documentInfo.type} • {message.image.documentInfo.filename}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}

                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: '#4285f4',
                      color: 'white',
                      borderTopRightRadius: 4,
                      mb: 1,
                      minWidth: 'fit-content',
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.5,
                        fontSize: '14px',
                        color: 'white',
                      }}
                    >
                      {message.content}
                    </Typography>
                  </Paper>

                  {/* Suggested Questions from Image */}
                  {message.image?.suggestedQuestions && message.image.suggestedQuestions.length > 0 && (
                    <Box sx={{ 
                      width: '100%', 
                      mt: 2, 
                      mb: 1,
                      p: 2,
                      bgcolor: '#f8f9fa',
                      borderRadius: 2,
                      border: '1px solid #e8eaed'
                    }}>
                      <Typography variant="subtitle2" sx={{ 
                        color: '#3c4043', 
                        mb: 1.5,
                        fontSize: '13px',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}>
                        � Extracted Text:
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {message.image.suggestedQuestions.map((question, index) => (
                          <Box
                            key={index}
                            sx={{
                              p: 3,
                              borderRadius: 2,
                              bgcolor: '#fff',
                              border: '2px solid #e3f2fd',
                              fontSize: '14px',
                              fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
                              color: '#1565c0',
                              whiteSpace: 'pre-line',
                              lineHeight: 1.6,
                              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                              '&:hover': {
                                boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
                                transform: 'translateY(-1px)'
                              },
                              transition: 'all 0.2s ease'
                            }}
                          >
                            <Typography variant="body2" sx={{ 
                              fontWeight: 600, 
                              color: '#d32f2f', 
                              mb: 1,
                              fontSize: '12px',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              Error Message
                            </Typography>
                            <Box sx={{ 
                              fontFamily: 'monospace',
                              fontSize: '13px',
                              bgcolor: '#f5f5f5',
                              p: 2,
                              borderRadius: 1,
                              border: '1px solid #e0e0e0'
                            }}>
                              {question}
                            </Box>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* User Message Status */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, px: 1 }}>
                    <Typography variant="caption" sx={{ color: '#5f6368', fontSize: '12px' }}>
                      {getTimeAgo(message.timestamp)}
                    </Typography>
                  </Box>
                </Box>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    bgcolor: '#4285f4',
                    color: 'white',
                  }}
                >
                  <PersonIcon sx={{ fontSize: 18 }} />
                </Avatar>
              </Box>
            )}
          </Box>
        ))}

        {isTyping && (
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Avatar
              sx={{
                width: 44,
                height: 44,
                bgcolor: '#f8f9fa',
                color: '#3c4043',
                border: '1px solid #dadce0',
              }}
            >
              <BotIcon sx={{ fontSize: 22 }} />
            </Avatar>
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                borderRadius: 2,
                bgcolor: '#f1f3f4',
                border: '1px solid #e8eaed',
                borderTopLeftRadius: 4,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={16} sx={{ color: '#4285f4' }} />
                <Typography variant="body2" sx={{ color: '#5f6368', fontSize: '14px' }}>
                  AI is typing...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />

        {/* Suggestions inside messages area */}
        {suggestions.length > 0 && !suggestionsMarquee && (
          <Box sx={{ p: 3, pt: 2, bgcolor: '#ffffff', display: 'flex', justifyContent: 'flex-end' }}>
            <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1.5,
                maxWidth: '80%',
                justifyContent: 'flex-end',
                maxHeight: { xs: 120, sm: 'none' },
                overflowY: { xs: 'auto', sm: 'visible' },
              }}
            >
              {suggestions.map((suggestion, index) => {
                const isSelected = selectedSuggestion && suggestion.toLowerCase() === selectedSuggestion.toLowerCase();
                return (
                  <Chip
                    key={index}
                    label={suggestion}
                    variant={isSelected ? 'filled' : 'outlined'}
                    onClick={() => handleSuggestionClick(suggestion)}
                    sx={{
                      borderColor: isSelected ? '#4285f4' : '#dadce0',
                      bgcolor: isSelected ? '#4285f4' : 'transparent',
                      color: isSelected ? 'white' : '#3c4043',
                      fontSize: '13px',
                      height: 'auto',
                      py: 1,
                      px: 2,
                      borderRadius: 3,
                      '&:hover': {
                        bgcolor: isSelected ? '#3367d6' : '#f8f9fa',
                        borderColor: '#4285f4',
                        color: isSelected ? 'white' : '#4285f4',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  />
                );
              })}
            </Box>
          </Box>
        )}

        {/* Marquee-style suggestions (animated rows) */}
        {suggestions.length > 0 && suggestionsMarquee && (
          <Box sx={{ p: 0, pt: 1.5, pb: 2, bgcolor: '#ffffff' }}>
            {([0, 1, 2] as const).map((rowIdx) => (
              <Box
                key={rowIdx}
                sx={{
                  position: 'relative',
                  overflow: 'hidden',
                  px: 3,
                  mb: rowIdx < 2 ? 1.25 : 0,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    gap: 1.5,
                    animation: `scroll-left-${rowIdx} ${38 + rowIdx * 5}s linear infinite`,
                    '@keyframes scroll-left-0': {
                      '0%': { transform: 'translateX(0%)' },
                      '100%': { transform: 'translateX(-50%)' },
                    },
                    '@keyframes scroll-left-1': {
                      '0%': { transform: 'translateX(0%)' },
                      '100%': { transform: 'translateX(-50%)' },
                    },
                    '@keyframes scroll-left-2': {
                      '0%': { transform: 'translateX(0%)' },
                      '100%': { transform: 'translateX(-50%)' },
                    },
                  }}
                >
                  {[
                    ...suggestions.slice(rowIdx * Math.ceil(suggestions.length / 3), (rowIdx + 1) * Math.ceil(suggestions.length / 3)),
                    ...suggestions.slice(rowIdx * Math.ceil(suggestions.length / 3), (rowIdx + 1) * Math.ceil(suggestions.length / 3)),
                  ].map((suggestion, index) => (
                    <Chip
                      key={`${rowIdx}-${index}`}
                      label={suggestion}
                      variant="outlined"
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{
                        borderColor: '#dadce0',
                        color: '#3c4043',
                        fontSize: '13px',
                        height: 'auto',
                        py: 1,
                        px: 2,
                        borderRadius: 3,
                        whiteSpace: 'nowrap',
                        bgcolor: 'white',
                        '&:hover': {
                          bgcolor: '#f8f9fa',
                          borderColor: '#4285f4',
                          color: '#4285f4',
                        },
                        transition: 'all 0.2s ease',
                      }}
                    />
                  ))}
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Box>

      {/* Input Area - Fixed at bottom */}
      <Box
        sx={{
          position: 'sticky',
          bottom: 0,
          p: 3,
          borderTop: '1px solid #e8eaed',
          bgcolor: 'white',
          zIndex: 10,
        }}
      >
        {/* Image Preview Area */}
        {imagePreview && (
          <Box sx={{ 
            mb: 2, 
            p: 2, 
            bgcolor: '#f8f9fa', 
            borderRadius: 2, 
            border: '1px solid #e8eaed',
            position: 'relative'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <img 
                src={imagePreview} 
                alt="Preview" 
                style={{
                  width: '60px',
                  height: '60px',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  border: '1px solid #dadce0'
                }}
              />
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" sx={{ color: '#3c4043', fontWeight: 500 }}>
                  {selectedImage?.name}
                </Typography>
                <Typography variant="caption" sx={{ color: '#5f6368' }}>
                  {selectedImage && `${(selectedImage.size / 1024 / 1024).toFixed(2)} MB`}
                </Typography>
                {isAnalyzingImage && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="caption" sx={{ color: '#4285f4' }}>
                      Analyzing document...
                    </Typography>
                  </Box>
                )}
              </Box>
              <IconButton 
                onClick={clearImagePreview}
                sx={{ color: '#5f6368', p: 0.5 }}
                disabled={isAnalyzingImage}
              >
                ✕
              </IconButton>
            </Box>
          </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            variant="outlined"
            placeholder={isAnalyzingImage ? "Analyzing image..." : placeholder}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isAnalyzingImage}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                bgcolor: 'white',
                borderColor: '#dadce0',
                fontSize: '14px',
                '&:hover': {
                  borderColor: '#4285f4',
                },
                '&.Mui-focused': {
                  borderColor: '#4285f4',
                },
              },
              '& .MuiInputBase-input': {
                py: 1.5,
              },
            }}
          />
          
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }}
          />
          
          {/* Image Upload Button */}
          <IconButton
            onClick={handleImageButtonClick}
            disabled={isAnalyzingImage}
            sx={{
              color: '#5f6368',
              '&:hover': {
                bgcolor: '#f8f9fa',
                color: '#4285f4',
              },
              p: 1.5,
            }}
            title="Upload image document"
          >
            📸
          </IconButton>
          
          <IconButton
            onClick={handleSend}
            disabled={!inputValue.trim() || isAnalyzingImage}
            sx={{
              bgcolor: inputValue.trim() && !isAnalyzingImage ? '#4285f4' : '#f1f3f4',
              color: inputValue.trim() && !isAnalyzingImage ? 'white' : '#9aa0a6',
              '&:hover': {
                bgcolor: inputValue.trim() && !isAnalyzingImage ? '#3367d6' : '#f1f3f4',
              },
              '&:disabled': {
                bgcolor: '#f1f3f4',
                color: '#9aa0a6',
              },
              p: 1.5,
              borderRadius: 2,
            }}
          >
            <SendIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Box>

        {/* Input Helper Text */}
        <Typography
          variant="caption"
          sx={{
            color: '#9aa0a6',
            fontSize: '12px',
            mt: 1,
            display: 'block',
            textAlign: 'center',
          }}
        >
          Press Enter to send, Shift+Enter for new line • 📸 Upload business documents for instant questions
        </Typography>
      </Box>
    </Box>
  );
};