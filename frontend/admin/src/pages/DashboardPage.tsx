import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
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
import AdminApiService, { DashboardStats, RecentActivity, TopQuery } from '../services/adminApi';

const DashboardPage: React.FC = () => {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [topQueries, setTopQueries] = useState<TopQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all dashboard data in parallel
      const [statsData, activitiesData, queriesData] = await Promise.all([
        AdminApiService.getDashboardStats(),
        AdminApiService.getRecentActivities(10),
        AdminApiService.getTopQueries(5),
      ]);

      setDashboardStats(statsData);
      setRecentActivities(activitiesData);
      setTopQueries(queriesData);
    } catch (err) {
      const errorMessage = AdminApiService.handleApiError(err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatIcon = (title: string) => {
    switch (title) {
      case 'Total Conversations':
        return <QuestionAnswer sx={{ fontSize: 32 }} />;
      case 'Active Users':
        return <People sx={{ fontSize: 32 }} />;
      case 'Knowledge Base Entries':
        return <Storage sx={{ fontSize: 32 }} />;
      case 'Success Rate':
        return <TrendingUp sx={{ fontSize: 32 }} />;
      default:
        return <TrendingUp sx={{ fontSize: 32 }} />;
    }
  };

  const getStatColor = (title: string) => {
    switch (title) {
      case 'Total Conversations':
        return colors.primary.main;
      case 'Active Users':
        return colors.success.main;
      case 'Knowledge Base Entries':
        return colors.info.main;
      case 'Success Rate':
        return colors.warning.main;
      default:
        return colors.secondary.main;
    }
  };

  const stats = dashboardStats ? [
    {
      title: 'Total Conversations',
      value: dashboardStats.total_conversations.toString(),
      change: dashboardStats.total_conversations_change,
      trend: 'up',
      icon: getStatIcon('Total Conversations'),
      color: getStatColor('Total Conversations'),
    },
    {
      title: 'Active Users',
      value: dashboardStats.total_users.toString(),
      change: dashboardStats.total_users_change,
      trend: 'up',
      icon: getStatIcon('Active Users'),
      color: getStatColor('Active Users'),
    },
    {
      title: 'Knowledge Base Entries',
      value: dashboardStats.knowledge_base_entries.toString(),
      change: dashboardStats.knowledge_base_entries_change,
      trend: 'up',
      icon: getStatIcon('Knowledge Base Entries'),
      color: getStatColor('Knowledge Base Entries'),
    },
    {
      title: 'Success Rate',
      value: `${dashboardStats.success_rate}%`,
      change: dashboardStats.success_rate_change,
      trend: 'up',
      icon: getStatIcon('Success Rate'),
      color: getStatColor('Success Rate'),
    },
  ] : [];

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

  if (loading) {
    return (
      <AdminLayout title="Dashboard Overview">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress size={60} />
        </Box>
      </AdminLayout>
    );
  }

  if (error) {
    return (
      <AdminLayout title="Dashboard Overview">
        <Alert
          severity="error"
          action={
            <button onClick={loadDashboardData}>
              Retry
            </button>
          }
        >
          {error}
        </Alert>
      </AdminLayout>
    );
  }

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
                  <Typography variant="caption" sx={{ color: stat.color, fontWeight: 600 }}>
                    {stat.change} from last week
                  </Typography>
                </Box>
                <Box sx={{ color: stat.color, opacity: 0.8 }}>
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
            {recentActivities.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Action</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Details</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentActivities.map((activity) => (
                      <TableRow key={activity.id} hover>
                        <TableCell>
                          {getStatusIcon(activity.status)}
                        </TableCell>
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
                          <Typography variant="body2" color="text.secondary">
                            {activity.timestamp}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No recent activities found. Start by adding some data to the knowledge base.
              </Typography>
            )}
          </ReckonCard>
        </Grid>

        {/* Top Queries */}
        <Grid size={{xs: 12, md: 4}}>
          <ReckonCard title="Top Queries Today" hover={false}>
            {topQueries.length > 0 ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {topQueries.map((query, index) => (
                  <Box
                    key={index}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: colors.background.secondary,
                      border: `1px solid ${colors.divider}`,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="body2" sx={{ flex: 1, fontWeight: 500 }}>
                        {query.query}
                      </Typography>
                      <Chip
                        label={query.count}
                        size="small"
                        sx={{ bgcolor: `${getCategoryColor(query.category)}20`, color: getCategoryColor(query.category) }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: getCategoryColor(query.category), fontWeight: 600 }}>
                      {query.category}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No queries found yet. Users haven't started asking questions.
              </Typography>
            )}
          </ReckonCard>
        </Grid>
      </Grid>
    </AdminLayout>
  );
};

export default DashboardPage;