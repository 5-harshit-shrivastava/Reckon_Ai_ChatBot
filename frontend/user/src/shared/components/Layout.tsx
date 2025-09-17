import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  IconButton,
  Container,
  Avatar,
  Menu,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Language as LanguageIcon,
  AccountCircle,
  Notifications,
} from '@mui/icons-material';
import { colors } from '../theme';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showConnectionStatus?: boolean;
  connectionStatus?: 'connected' | 'disconnected' | 'pending';
  onMenuClick?: () => void;
  showLanguageSelector?: boolean;
  showNotifications?: boolean;
  currentUser?: {
    name: string;
    avatar?: string;
  };
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  title = "Reckon AI Support",
  showConnectionStatus = false,
  connectionStatus = 'connected',
  onMenuClick,
  showLanguageSelector = true,
  showNotifications = false,
  currentUser,
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [langAnchorEl, setLangAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleLanguageMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setLangAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setLangAnchorEl(null);
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return colors.success.main;
      case 'disconnected': return colors.error.main;
      case 'pending': return colors.warning.main;
      default: return colors.secondary.main;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'ERP Connected';
      case 'disconnected': return 'ERP Disconnected';
      case 'pending': return 'ERP Connecting...';
      default: return 'ERP Status Unknown';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: colors.background.default }}>
      <AppBar
        position="static"
        elevation={0}
        sx={{
          bgcolor: colors.background.paper,
          borderBottom: `1px solid ${colors.divider}`,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {onMenuClick && (
              <IconButton
                edge="start"
                color="inherit"
                aria-label="menu"
                onClick={onMenuClick}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                component="img"
                src="/logo.png"
                alt="Reckon Logo"
                sx={{ width: 28, height: 32, objectFit: 'contain' }}
              />
              <Box>
                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                  {title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Your GST Enabled Assistant
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {showConnectionStatus && (
              <Chip
                label={getStatusText()}
                size="small"
                sx={{
                  bgcolor: `${getStatusColor()}20`,
                  color: getStatusColor(),
                  fontWeight: 500,
                  '&::before': {
                    content: '""',
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: getStatusColor(),
                    mr: 1,
                  },
                }}
              />
            )}

            {showLanguageSelector && (
              <>
                <Button
                  color="inherit"
                  startIcon={<LanguageIcon />}
                  onClick={handleLanguageMenuOpen}
                  sx={{ textTransform: 'none' }}
                >
                  English
                </Button>
                <Menu
                  anchorEl={langAnchorEl}
                  open={Boolean(langAnchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleMenuClose}>English</MenuItem>
                  <MenuItem onClick={handleMenuClose}>हिंदी</MenuItem>
                </Menu>
              </>
            )}

            {showNotifications && (
              <IconButton color="inherit">
                <Notifications />
              </IconButton>
            )}

            {currentUser && (
              <>
                <IconButton
                  edge="end"
                  aria-label="account of current user"
                  onClick={handleProfileMenuOpen}
                  color="inherit"
                >
                  {currentUser.avatar ? (
                    <Avatar src={currentUser.avatar} sx={{ width: 32, height: 32 }} />
                  ) : (
                    <AccountCircle />
                  )}
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
                  <MenuItem onClick={handleMenuClose}>Settings</MenuItem>
                  <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 3 }}>
        {children}
      </Container>
    </Box>
  );
};