import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Container,
  Chip,
} from '@mui/material';
import {
  PhoneAndroid as MobileIcon,
  Cloud as CloudIcon,
  DesktopMac as DesktopIcon,
  Receipt as ReceiptIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Layout, ReckonCard, colors } from '../shared';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const solutionCards = [
    {
      title: 'Mobile Solutions',
      icon: <MobileIcon sx={{ fontSize: 32 }} />,
      description: 'Access Reckon on the go with our mobile-optimized platform',
    },
    {
      title: 'Cloud Solutions',
      icon: <CloudIcon sx={{ fontSize: 32 }} />,
      description: 'Secure cloud-based GST and inventory management',
    },
    {
      title: 'Desktop Solutions',
      icon: <DesktopIcon sx={{ fontSize: 32 }} />,
      description: 'Full-featured desktop application for comprehensive business management',
    },
    {
      title: 'GST Returns Help',
      icon: <ReceiptIcon sx={{ fontSize: 32 }} />,
      description: 'Expert assistance with GST compliance and return filing',
    },
  ];

  const popularQuestions = [
    'What are the advantages of ERP?',
    'How to reconcile ledger entries?',
    'Setup pharmacy billing system',
    'Auto parts inventory management',
    'GST compliance for retailers',
    'Multi-branch synchronization',
  ];

  const handleQuestionClick = (question: string) => {
    navigate('/chat', { state: { initialMessage: question } });
  };

  const handleStartChat = () => {
    navigate('/chat');
  };

  return (
    <Layout
      title="Reckon AI Support"
      showConnectionStatus={true}
      connectionStatus="connected"
      showLanguageSelector={true}
      currentUser={{ name: "Profile" }}
    >
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 6, py: 4 }}>
          <Typography
            variant="h2"
            component="h1"
            sx={{
              mb: 2,
              fontWeight: 700,
              background: `linear-gradient(45deg, ${colors.primary.main}, ${colors.primary.dark})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            How can I help you today?
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}
          >
            Get instant support for billing, GST compliance, inventory, and more
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<ChatIcon />}
            onClick={handleStartChat}
            sx={{
              py: 1.5,
              px: 4,
              borderRadius: 3,
              fontSize: '1.1rem',
              fontWeight: 600,
              textTransform: 'none',
            }}
          >
            Start Chat
          </Button>
        </Box>

        {/* Solutions Grid */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {solutionCards.map((card, index) => (
            <Grid size={{xs: 12, sm: 6, md: 3}} key={index}>
              <ReckonCard
                title={card.title}
                icon={card.icon}
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => handleQuestionClick(card.title)}
              >
                <Typography variant="body2" color="text.secondary">
                  {card.description}
                </Typography>
              </ReckonCard>
            </Grid>
          ))}
        </Grid>

        {/* Popular Questions */}
        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" component="h2" sx={{ mb: 3, fontWeight: 600 }}>
            Popular Questions
          </Typography>
          <Grid container spacing={2}>
            {popularQuestions.map((question, index) => (
              <Grid size={{xs: 12, sm: 6, md: 4}} key={index}>
                <Chip
                  label={question}
                  variant="outlined"
                  onClick={() => handleQuestionClick(question)}
                  sx={{
                    width: '100%',
                    height: 'auto',
                    p: 2,
                    borderRadius: 2,
                    borderColor: colors.border,
                    fontSize: '0.875rem',
                    textAlign: 'left',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      borderColor: colors.primary.main,
                      bgcolor: colors.background.secondary,
                      transform: 'translateY(-1px)',
                    },
                    transition: 'all 0.2s ease-in-out',
                  }}
                />
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Welcome Message */}
        <ReckonCard
          sx={{
            bgcolor: colors.background.secondary,
            border: `1px solid ${colors.primary.light}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                bgcolor: colors.primary.main,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 600,
                fontSize: '1.1rem',
              }}
            >
              AI
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Namaste! Welcome to Reckon Support. I can help you with billing, GST compliance,
                inventory management, and more. How can I assist you today?
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<ChatIcon />}
                  onClick={handleStartChat}
                >
                  Start Conversation
                </Button>
              </Box>
            </Box>
          </Box>
        </ReckonCard>
      </Container>
    </Layout>
  );
};

export default HomePage;