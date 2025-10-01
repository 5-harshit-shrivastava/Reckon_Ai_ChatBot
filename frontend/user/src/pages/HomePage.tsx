import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Container,
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

  // Popular questions are now shown inside chat, not on homepage

  const handleStartChat = () => {
    // Force a new chat session by adding a unique timestamp
    navigate('/chat', { state: { newSession: Date.now() } });
  };

  return (
    <Layout
      title="Reckon AI Support"
      showConnectionStatus={false}
      showLanguageSelector={true}
    >
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 4, py: 3 }}>
          <Typography
            variant="h3"
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
            variant="body1"
            color="text.secondary"
            sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}
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
              borderRadius: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              textTransform: 'none',
            }}
          >
            Start Chat
          </Button>

        </Box>

        {/* Solutions Grid */}
        <Grid container spacing={3} sx={{ mb: 2 }}>
          {solutionCards.map((card, index) => (
            <Grid size={{xs: 12, sm: 6, md: 3}} key={index}>
              <ReckonCard
                title={card.title}
                icon={card.icon}
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  cursor: 'pointer',
                  p: 3,
                }}
                onClick={handleStartChat}
              >
                <Typography variant="caption" color="text.secondary">
                  {card.description}
                </Typography>
              </ReckonCard>
            </Grid>
          ))}
        </Grid>


      </Container>
    </Layout>
  );
};

export default HomePage;