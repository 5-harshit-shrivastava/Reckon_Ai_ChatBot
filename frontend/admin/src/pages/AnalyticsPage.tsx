import React from 'react';
import {
  Box,
  Grid,
  Typography,
} from '@mui/material';
import { AdminLayout } from '../components/AdminLayout';
import { ReckonCard } from '../shared';

const AnalyticsPage: React.FC = () => {
  return (
    <AdminLayout title="Analytics & Reports">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
          Analytics & Reports
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor performance metrics and generate insights from your AI support system.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid size={{xs: 12}}>
          <ReckonCard title="Query Analytics" hover={false}>
            <Typography variant="body2" color="text.secondary">
              Analytics dashboard will be implemented here with charts and metrics.
            </Typography>
          </ReckonCard>
        </Grid>
      </Grid>
    </AdminLayout>
  );
};

export default AnalyticsPage;