import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { AdminLayout } from '../components/AdminLayout';
import { ReckonCard, colors } from '../shared';
import AdminApiService, { KnowledgeBaseEntry, KnowledgeBaseCreate, KnowledgeBaseUpdate } from '../services/adminApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const DataManagementPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'add' | 'edit'>('add');
  const [selectedItem, setSelectedItem] = useState<KnowledgeBaseEntry | null>(null);
  const [knowledgeBaseEntries, setKnowledgeBaseEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    document_type: '',
    industry_type: '',
    language: 'en'
  });

  useEffect(() => {
    loadKnowledgeBaseEntries();
  }, []);

  const loadKnowledgeBaseEntries = async () => {
    try {
      setLoading(true);
      setError(null);
      const entries = await AdminApiService.getKnowledgeBaseEntries();
      setKnowledgeBaseEntries(entries);
    } catch (err) {
      const errorMessage = AdminApiService.handleApiError(err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (type: 'add' | 'edit', item?: KnowledgeBaseEntry) => {
    setDialogType(type);
    setSelectedItem(item || null);
    if (item) {
      setFormData({
        title: item.title,
        content: '', // We'll need to fetch full content if editing
        document_type: item.document_type,
        industry_type: item.industry_type || '',
        language: item.language
      });
    } else {
      setFormData({
        title: '',
        content: '',
        document_type: '',
        industry_type: '',
        language: 'en'
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedItem(null);
    setFormData({
      title: '',
      content: '',
      document_type: '',
      industry_type: '',
      language: 'en'
    });
  };

  const handleSaveEntry = async () => {
    try {
      if (dialogType === 'add') {
        await AdminApiService.createKnowledgeBaseEntry({
          title: formData.title,
          content: formData.content,
          document_type: formData.document_type,
          industry_type: formData.industry_type || undefined,
          language: formData.language
        });
      } else if (selectedItem) {
        await AdminApiService.updateKnowledgeBaseEntry(selectedItem.id, {
          title: formData.title,
          content: formData.content,
          document_type: formData.document_type,
          industry_type: formData.industry_type || undefined,
          language: formData.language
        });
      }
      handleCloseDialog();
      loadKnowledgeBaseEntries(); // Refresh the list
    } catch (err) {
      const errorMessage = AdminApiService.handleApiError(err);
      setError(errorMessage);
    }
  };

  const handleDeleteEntry = async (entryId: number) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      try {
        await AdminApiService.deleteKnowledgeBaseEntry(entryId);
        loadKnowledgeBaseEntries(); // Refresh the list
      } catch (err) {
        const errorMessage = AdminApiService.handleApiError(err);
        setError(errorMessage);
      }
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? colors.success.main : colors.error.main;
  };

  const getStatusLabel = (isActive: boolean) => {
    return isActive ? 'active' : 'inactive';
  };

  const getCategoryColor = (documentType: string) => {
    const colorMap: { [key: string]: string } = {
      gst: colors.primary.main,
      inventory: colors.success.main,
      erp: colors.info.main,
      billing: colors.warning.main,
      reports: colors.secondary.main,
      tutorial: colors.info.main,
      documentation: colors.warning.main
    };
    return colorMap[documentType.toLowerCase()] || colors.secondary.main;
  };

  return (
    <AdminLayout title="Data Management">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
          Data Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage knowledge base entries, training data, and system content.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{xs: 12, sm: 6, md: 3}}>
          <ReckonCard hover={false}>
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
              {knowledgeBaseEntries.length.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Knowledge Base Entries
            </Typography>
          </ReckonCard>
        </Grid>
        <Grid size={{xs: 12, sm: 6, md: 3}}>
          <ReckonCard hover={false}>
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
              8,945
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Training Examples
            </Typography>
          </ReckonCard>
        </Grid>
        <Grid size={{xs: 12, sm: 6, md: 3}}>
          <ReckonCard hover={false}>
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
              94.2%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Data Quality Score
            </Typography>
          </ReckonCard>
        </Grid>
        <Grid size={{xs: 12, sm: 6, md: 3}}>
          <ReckonCard hover={false}>
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
              2.3k
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Pending Reviews
            </Typography>
          </ReckonCard>
        </Grid>
      </Grid>

      {/* Main Content */}
      <ReckonCard hover={false}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Knowledge Base" />
            <Tab label="Training Data" />
            <Tab label="Bulk Operations" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Knowledge Base Entries
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                size="small"
                onClick={loadKnowledgeBaseEntries}
                disabled={loading}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog('add')}
              >
                Add Entry
              </Button>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Document Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Chunks</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress size={24} />
                    </TableCell>
                  </TableRow>
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="error">{error}</Typography>
                    </TableCell>
                  </TableRow>
                ) : knowledgeBaseEntries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary">No entries found. Click "Add Entry" to get started.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  knowledgeBaseEntries.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {entry.title}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={entry.document_type}
                          size="small"
                          sx={{
                            bgcolor: `${getCategoryColor(entry.document_type)}20`,
                            color: getCategoryColor(entry.document_type),
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(entry.is_active)}
                          size="small"
                          sx={{
                            bgcolor: `${getStatusColor(entry.is_active)}20`,
                            color: getStatusColor(entry.is_active),
                          }}
                        />
                      </TableCell>
                      <TableCell>{new Date(entry.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>{entry.chunk_count}</TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog('edit', entry)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteEntry(entry.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Training Data
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Training data will be implemented in a future update. For now, use Knowledge Base entries.
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Bulk Operations
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{xs: 12, md: 6}}>
              <Paper sx={{ p: 3, border: `1px solid ${colors.divider}` }}>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Import Data
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Upload CSV or JSON files to bulk import knowledge base entries or training data.
                </Typography>
                <Button variant="outlined" startIcon={<UploadIcon />} fullWidth>
                  Choose Files
                </Button>
              </Paper>
            </Grid>
            <Grid size={{xs: 12, md: 6}}>
              <Paper sx={{ p: 3, border: `1px solid ${colors.divider}` }}>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Export Data
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Download your knowledge base and training data in various formats.
                </Typography>
                <Button variant="outlined" startIcon={<DownloadIcon />} fullWidth>
                  Export Data
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </ReckonCard>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogType === 'add' ? 'Add New Entry' : 'Edit Entry'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
            <FormControl fullWidth>
              <InputLabel>Document Type</InputLabel>
              <Select
                value={formData.document_type}
                onChange={(e) => setFormData({...formData, document_type: e.target.value})}
                label="Document Type"
                required
              >
                <MenuItem value="gst">GST</MenuItem>
                <MenuItem value="inventory">Inventory</MenuItem>
                <MenuItem value="erp">ERP</MenuItem>
                <MenuItem value="billing">Billing</MenuItem>
                <MenuItem value="reports">Reports</MenuItem>
                <MenuItem value="tutorial">Tutorial</MenuItem>
                <MenuItem value="documentation">Documentation</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Content"
              multiline
              rows={6}
              fullWidth
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              required
              placeholder="Enter the full content of the document here..."
            />
            <FormControl fullWidth>
              <InputLabel>Industry Type (Optional)</InputLabel>
              <Select
                value={formData.industry_type}
                onChange={(e) => setFormData({...formData, industry_type: e.target.value})}
                label="Industry Type (Optional)"
              >
                <MenuItem value="">None</MenuItem>
                <MenuItem value="manufacturing">Manufacturing</MenuItem>
                <MenuItem value="retail">Retail</MenuItem>
                <MenuItem value="services">Services</MenuItem>
                <MenuItem value="healthcare">Healthcare</MenuItem>
                <MenuItem value="education">Education</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={formData.language}
                onChange={(e) => setFormData({...formData, language: e.target.value})}
                label="Language"
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="hi">Hindi</MenuItem>
                <MenuItem value="es">Spanish</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveEntry}
            disabled={!formData.title || !formData.content || !formData.document_type}
          >
            {dialogType === 'add' ? 'Add' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </AdminLayout>
  );
};

export default DataManagementPage;