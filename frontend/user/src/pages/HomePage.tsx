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

  const handleQuestionClick = (question: string) => {
    // Force a new chat session with the question and a unique timestamp
    navigate('/chat', { state: { initialMessage: question, newSession: Date.now() } });
  };

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

          {/* Animated Popular Questions */}
          <Box sx={{ mt: 4, mb: 2 }}>
            <Typography variant="h6" component="h2" sx={{ mb: 1.5, fontWeight: 600, textAlign: 'center' }}>
              Popular Questions
            </Typography>

            {/* Scrolling container with blur edges */}
            <Box
              sx={{
                position: 'relative',
                overflow: 'hidden',
                '&::before, &::after': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  bottom: 0,
                  width: 100,
                  zIndex: 2,
                  pointerEvents: 'none',
                },
                '&::before': {
                  left: 0,
                  background: `linear-gradient(to right, ${colors.background.default}, transparent)`,
                },
                '&::after': {
                  right: 0,
                  background: `linear-gradient(to left, ${colors.background.default}, transparent)`,
                }
              }}
            >
              {/* Row 1 */}
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  mb: 1.5,
                  animation: 'scroll-left 40s linear infinite',
                  '@keyframes scroll-left': {
                    '0%': { transform: 'translateX(0%)' },
                    '100%': { transform: 'translateX(-50%)' }
                  }
                }}
              >
                {[...popularQuestions.slice(0, 20), ...popularQuestions.slice(0, 20)].map((question, index) => (
                  <Chip
                    key={`row1-${index}`}
                    label={question}
                    variant="outlined"
                    onClick={() => handleQuestionClick(question)}
                    sx={{
                      whiteSpace: 'nowrap',
                      borderRadius: 3,
                      px: 2,
                      py: 0.5,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      border: 'none',
                      bgcolor: colors.background.paper,
                      color: colors.text.primary,
                      '&:hover': {
                        bgcolor: colors.primary.main,
                        color: 'white',
                        transform: 'translateY(-1px)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  />
                ))}
              </Box>

              {/* Row 2 */}
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  mb: 1.5,
                  animation: 'scroll-left 45s linear infinite',
                }}
              >
                {[...popularQuestions.slice(20, 40), ...popularQuestions.slice(20, 40)].map((question, index) => (
                  <Chip
                    key={`row2-${index}`}
                    label={question}
                    variant="outlined"
                    onClick={() => handleQuestionClick(question)}
                    sx={{
                      whiteSpace: 'nowrap',
                      borderRadius: 3,
                      px: 2,
                      py: 0.5,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      border: 'none',
                      bgcolor: colors.background.paper,
                      color: colors.text.primary,
                      '&:hover': {
                        bgcolor: colors.primary.main,
                        color: 'white',
                        transform: 'translateY(-1px)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  />
                ))}
              </Box>

              {/* Row 3 */}
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  mb: 0,
                  animation: 'scroll-left 50s linear infinite',
                }}
              >
                {[...popularQuestions.slice(40), ...popularQuestions.slice(40)].map((question, index) => (
                  <Chip
                    key={`row3-${index}`}
                    label={question}
                    variant="outlined"
                    onClick={() => handleQuestionClick(question)}
                    sx={{
                      whiteSpace: 'nowrap',
                      borderRadius: 3,
                      px: 2,
                      py: 0.5,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      border: 'none',
                      bgcolor: colors.background.paper,
                      color: colors.text.primary,
                      '&:hover': {
                        bgcolor: colors.primary.main,
                        color: 'white',
                        transform: 'translateY(-1px)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Box>
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
                onClick={() => handleQuestionClick(card.title)}
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