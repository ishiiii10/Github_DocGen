import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import { GitHub as GitHubIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  const handleAnalyze = async () => {
    if (!repoUrl) {
      setError('Please enter a repository URL');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/api/analyze', {
        repo_url: repoUrl
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while analyzing the repository');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Repository Analyzer
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
          Analyze GitHub repositories and generate comprehensive documentation
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
          <TextField
            fullWidth
            label="GitHub Repository URL"
            variant="outlined"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository.git"
            InputProps={{
              startAdornment: <GitHubIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleAnalyze}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Analyze'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {result && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Analysis Results: {result.repository_name}
          </Typography>

          <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="Overview" />
            <Tab label="Structure" />
            <Tab label="Complexity" />
            <Tab label="Documentation" />
          </Tabs>

          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Technologies
                    </Typography>
                    {Object.entries(result.structure.languages).map(([lang, count]) => (
                      <Typography key={lang}>
                        {lang.substring(1).toUpperCase()}: {count} files
                      </Typography>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Dependencies
                    </Typography>
                    {Object.entries(result.structure.dependencies).map(([lang, deps]) => (
                      deps.length > 0 && (
                        <Box key={lang} sx={{ mb: 2 }}>
                          <Typography variant="subtitle1">{lang}</Typography>
                          {deps.map(dep => (
                            <Typography key={dep} variant="body2">
                              • {dep}
                            </Typography>
                          ))}
                        </Box>
                      )
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Project Structure
              </Typography>
              {result.structure.entry_points.map(entry => (
                <Typography key={entry} paragraph>
                  • {entry}
                </Typography>
              ))}
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Code Complexity Analysis
              </Typography>
              {Object.entries(result.structure.complexity_metrics).map(([file, metrics]) => (
                <Card key={file} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {file}
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6} md={3}>
                        <Typography variant="body2">
                          Cyclomatic Complexity: {metrics.cyclomatic_complexity}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Typography variant="body2">
                          Functions: {metrics.function_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Typography variant="body2">
                          Classes: {metrics.class_count}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <Typography variant="body2">
                          Max Nesting: {metrics.max_nesting}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}

          {activeTab === 3 && (
            <Box sx={{ '& img': { maxWidth: '100%' } }}>
              <ReactMarkdown>{result.readme_content}</ReactMarkdown>
            </Box>
          )}
        </Paper>
      )}
    </Container>
  );
}

export default App; 