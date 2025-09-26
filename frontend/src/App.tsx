import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Analytics as AnalyticsIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import axios from 'axios';
import { Bar, Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

interface QueryResult {
  question: string;
  sql_query: string;
  results: {
    success: boolean;
    data: any[];
    columns: string[];
    row_count: number;
    error?: string;
  };
  insights: string;
  timestamp: string;
}

interface SchemaInfo {
  [table: string]: {
    columns: { name: string; type: string; nullable: boolean }[];
    sample_data: any[];
  };
}

const App: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [schema, setSchema] = useState<SchemaInfo | null>(null);

  useEffect(() => {
    fetchSchema();
  }, []);

  const fetchSchema = async () => {
    try {
      const response = await axios.get(`${API_BASE}/schema`);
      setSchema(response.data);
    } catch (err) {
      console.error('Failed to fetch schema:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE}/ask`, { question });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const generateChartData = (data: any[], columns: string[]) => {
    if (!data.length) return null;

    // Find numeric and categorical columns
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number')
    );
    const categoricalColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'string')
    );

    if (numericColumns.length === 0) return null;

    // Simple bar chart for first numeric column by first categorical column
    if (categoricalColumns.length > 0 && numericColumns.length > 0) {
      const categoryCol = categoricalColumns[0];
      const numericCol = numericColumns[0];
      
      const aggregated: { [key: string]: number } = {};
      data.forEach(row => {
        const category = row[categoryCol]?.toString() || 'Unknown';
        const value = parseFloat(row[numericCol]) || 0;
        aggregated[category] = (aggregated[category] || 0) + value;
      });

      return {
        type: 'bar',
        data: {
          labels: Object.keys(aggregated),
          datasets: [{
            label: numericCol,
            data: Object.values(aggregated),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: `${numericCol} by ${categoryCol}`
            }
          }
        }
      };
    }

    return null;
  };

  const sampleQuestions = [
    "What are our top-selling products by revenue?",
    "Show me monthly revenue trends",
    "Which customer segment generates the most profit?",
    "What's the average order value by region?",
    "Identify customers who haven't ordered in the last 90 days",
    "What's our gross margin by product category?"
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" color="primary">
        <AnalyticsIcon sx={{ fontSize: 48, mr: 2 }} />
        SQL Conversational Interface
      </Typography>
      
      <Typography variant="h6" color="textSecondary" align="center" sx={{ mb: 4 }}>
        Ask complex business questions and get intelligent answers with visualizations
      </Typography>

      {/* Sample Questions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Try these sample questions:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {sampleQuestions.map((q, index) => (
              <Chip
                key={index}
                label={q}
                onClick={() => setQuestion(q)}
                variant="outlined"
                clickable
                size="small"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Question Input */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            label="Ask a business question..."
            placeholder="e.g., What are our top performing products this quarter?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading || !question.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
          >
            {loading ? 'Analyzing...' : 'Ask Question'}
          </Button>
        </form>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {result && (
        <Box sx={{ mb: 4 }}>
          {/* Insights */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                📊 Analysis Results
              </Typography>
              <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                {result.insights}
              </Typography>
            </CardContent>
          </Card>

          {/* Data Visualization */}
          {result.results.success && result.results.data.length > 0 && (
            <>
              {(() => {
                const chartData = generateChartData(result.results.data, result.results.columns);
                return chartData ? (
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        📈 Visualization
                      </Typography>
                      <Box sx={{ height: 400 }}>
                        <Bar data={chartData.data} options={chartData.options} />
                      </Box>
                    </CardContent>
                  </Card>
                ) : null;
              })()}

              {/* Data Table */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    📋 Data Table ({result.results.row_count} rows)
                  </Typography>
                  <TableContainer sx={{ maxHeight: 400 }}>
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          {result.results.columns.map((col) => (
                            <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                              {col}
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.results.data.slice(0, 50).map((row, index) => (
                          <TableRow key={index}>
                            {result.results.columns.map((col) => (
                              <TableCell key={col}>
                                {row[col]?.toString() || 'N/A'}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  {result.results.row_count > 50 && (
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      Showing first 50 rows of {result.results.row_count} total rows
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </>
          )}

          {/* Technical Details */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🔧 Technical Details</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="subtitle2" gutterBottom>
                Generated SQL Query:
              </Typography>
              <Paper sx={{ p: 2, bgcolor: 'grey.100', mb: 2 }}>
                <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace' }}>
                  {result.sql_query}
                </Typography>
              </Paper>
              <Typography variant="caption" color="textSecondary">
                Query executed at: {new Date(result.timestamp).toLocaleString()}
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      )}

      {/* Database Schema */}
      {schema && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              <StorageIcon sx={{ mr: 1 }} />
              Database Schema
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              {Object.entries(schema).map(([tableName, tableInfo]) => (
                <Card key={tableName} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {tableName}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Columns: {tableInfo.columns.length}
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {tableInfo.columns.map((col) => (
                        <Chip
                          key={col.name}
                          label={`${col.name} (${col.type})`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
    </Container>
  );
};

export default App;