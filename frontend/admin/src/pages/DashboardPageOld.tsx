import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  People,
  QuestionAnswer,
  Storage,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';
import { AdminLayout } from '../components/AdminLayout';
import { ReckonCard, colors } from '../shared';

const DashboardPage: React.FC = () => {
  const stats = [
    {
      title: 'Total Conversations',
      value: '2,847',
      change: '+12.5%',
      trend: 'up',
      icon: <QuestionAnswer sx={{ fontSize: 32 }} />,
      color: colors.primary.main,
    },
    {
      title: 'Active Users',
      value: '1,234',
      change: '+8.2%',
      trend: 'up',
      icon: <People sx={{ fontSize: 32 }} />,
      color: colors.success.main,
    },
    {
      title: 'Knowledge Base Entries',
      value: '15,678',
      change: '+23.1%',
      trend: 'up',
      icon: <Storage sx={{ fontSize: 32 }} />,
      color: colors.info.main,
    },
    {
      title: 'Success Rate',
      value: '94.2%',
      change: '+2.1%',
      trend: 'up',
      icon: <TrendingUp sx={{ fontSize: 32 }} />,
      color: colors.warning.main,
    },
  ];

  const recentActivities = [
    {
      id: 1,
      action: 'Knowledge Base Updated',
      details: 'Added 15 new GST compliance articles',
      timestamp: '2 hours ago',
      status: 'success',
    },
    {
      id: 2,
      action: 'User Query Processed',
      details: 'Processed 234 queries in the last hour',
      timestamp: '1 hour ago',
      status: 'success',
    },
    {
      id: 3,
      action: 'System Alert',
      details: 'High query volume detected',
      timestamp: '30 minutes ago',
      status: 'warning',
    },
    {
      id: 4,
      action: 'Data Sync',
      details: 'Synchronized with ERP systems',
      timestamp: '15 minutes ago',
      status: 'success',
    },
  ];

  const topQueries = [
    { query: 'GST return filing process', count: 127, category: 'GST' },
    { query: 'Inventory management setup', count: 98, category: 'Inventory' },
    { query: 'Multi-branch synchronization', count: 87, category: 'ERP' },
    { query: 'Payment gateway integration', count: 76, category: 'Billing' },
    { query: 'Report generation guide', count: 65, category: 'Reports' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle sx={{ color: colors.success.main, fontSize: 20 }} />;
      case 'warning':
        return <Warning sx={{ color: colors.warning.main, fontSize: 20 }} />;
      case 'error':
        return <Error sx={{ color: colors.error.main, fontSize: 20 }} />;
      default:
        return <CheckCircle sx={{ color: colors.success.main, fontSize: 20 }} />;
    }
  };

  const getCategoryColor = (category: string) => {
    const colorMap: { [key: string]: string } = {
      GST: colors.primary.main,
      Inventory: colors.success.main,
      ERP: colors.info.main,
      Billing: colors.warning.main,
      Reports: colors.secondary.main,
    };
    return colorMap[category] || colors.secondary.main;
  };

  return (
    <AdminLayout title="Dashboard Overview">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
          Welcome back, Admin
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your Reckon AI Support system today.
        </Typography>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid size={{xs: 12, sm: 6, md: 3}} key={index}>
            <ReckonCard hover={false}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {stat.title}
                  </Typography>
                  <Chip
                    label={stat.change}
                    size="small"
                    sx={{
                      bgcolor: `${colors.success.main}20`,
                      color: colors.success.main,
                      fontWeight: 600,
                    }}
                  />
                </Box>
                <Box sx={{ color: stat.color }}>
                  {stat.icon}
                </Box>
              </Box>
            </ReckonCard>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activities */}
        <Grid size={{xs: 12, md: 8}}>
          <ReckonCard title="Recent Activities" hover={false}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Action</TableCell>
                    <TableCell>Details</TableCell>
                    <TableCell>Time</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentActivities.map((activity) => (
                    <TableRow key={activity.id} hover>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {activity.action}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {activity.details}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {activity.timestamp}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {getStatusIcon(activity.status)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </ReckonCard>
        </Grid>

        {/* Top Queries */}
        <Grid size={{xs: 12, md: 4}}>
          <ReckonCard title="Top Queries Today" hover={false}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {topQueries.map((query, index) => (
                <Box key={index}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body2" sx={{ flex: 1, pr: 1 }}>
                      {query.query}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                      {query.count}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Chip
                      label={query.category}
                      size="small"
                      sx={{
                        bgcolor: `${getCategoryColor(query.category)}20`,
                        color: getCategoryColor(query.category),
                        fontSize: '0.7rem',
                      }}
                    />
                    <LinearProgress
                      variant="determinate"
                      value={(query.count / 127) * 100}
                      sx={{
                        flex: 1,
                        ml: 2,
                        height: 4,
                        borderRadius: 2,
                        '& .MuiLinearProgress-bar': {
                          bgcolor: getCategoryColor(query.category),
                        },
                      }}
                    />
                  </Box>
                </Box>
              ))}
            </Box>
          </ReckonCard>
        </Grid>
      </Grid>
    </AdminLayout>
  );
};

export default DashboardPage;