import React from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
} from '@mui/material';
import { AdminLayout } from '../components/AdminLayout';
import { ReckonCard } from '../shared';

const SettingsPage: React.FC = () => {
  return (
    <AdminLayout title="System Settings">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your AI support system settings and preferences.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid size={{xs: 12, md: 8}}>
          <ReckonCard title="General Settings" hover={false}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                label="System Name"
                defaultValue="Reckon AI Support"
                fullWidth
              />
              <TextField
                label="Admin Email"
                defaultValue="admin@reckonsales.in"
                fullWidth
              />
              <TextField
                label="Support Email"
                defaultValue="support@reckonsales.in"
                fullWidth
              />

              <Divider />

              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI Configuration
              </Typography>

              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Enable AI Responses"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-learning from Conversations"
              />
              <FormControlLabel
                control={<Switch />}
                label="Debug Mode"
              />

              <TextField
                label="Response Confidence Threshold"
                defaultValue="0.8"
                type="number"
                inputProps={{ min: 0, max: 1, step: 0.1 }}
              />

              <Box sx={{ pt: 2 }}>
                <Button variant="contained" sx={{ mr: 2 }}>
                  Save Settings
                </Button>
                <Button variant="outlined">
                  Reset to Default
                </Button>
              </Box>
            </Box>
          </ReckonCard>
        </Grid>

        <Grid size={{xs: 12, md: 4}}>
          <ReckonCard title="System Status" hover={false}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Database Status
                </Typography>
                <Typography variant="body1" color="success.main">
                  Connected
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  AI Model Status
                </Typography>
                <Typography variant="body1" color="success.main">
                  Active
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last Backup
                </Typography>
                <Typography variant="body1">
                  2 hours ago
                </Typography>
              </Box>
            </Box>
          </ReckonCard>
        </Grid>
      </Grid>
    </AdminLayout>
  );
};

export default SettingsPage;