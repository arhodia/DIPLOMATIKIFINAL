import React, { useState } from "react";
import { 
  createTheme, ThemeProvider, CssBaseline, 
  Select, MenuItem, InputLabel, FormControl, Button, Box, Typography, Alert, 
  CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, 
  TableRow, Paper, Chip, OutlinedInput, Grid, IconButton, TextField
} from "@mui/material";
import { 
  RadioGroup, FormControlLabel, Radio 
} from '@mui/material';
// Icons
import ShareIcon from '@mui/icons-material/Share';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DownloadIcon from '@mui/icons-material/Download';
// Charts (Recharts)
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  LineChart, Line
} from 'recharts';


// --- THEME SETUP (DARK MODE) ---
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#121212', // Πολύ σκούρο φόντο
      paper: '#1e1e1e',   // Λίγο πιο ανοιχτό για τα cards
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
    primary: {
      main: '#90caf9',
    },
    success: {
      main: '#2e7d32', // Πράσινο κουμπί
    }
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h4: { fontWeight: 600 },
    h6: { fontWeight: 500 },
  },
  components: {
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #333',
        },
        head: {
          backgroundColor: '#2c2c2c',
          color: '#fff',
          fontWeight: 'bold',
        }
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          '& fieldset': { borderColor: '#555' }, // Γκρι borders
          '&:hover fieldset': { borderColor: '#888' },
        }
      }
    }
  }
});

// --- DUMMY DATA FOR CHARTS (Για να φαίνεται όπως η εικόνα) ---
const barData = [
  { name: '0-300', HL: 80, ML: 50, LL: 20 },
  { name: '300-600', HL: 95, ML: 40, LL: 10 },
  { name: '600-900', HL: 120, ML: 70, LL: 40 },
  { name: '900-1200', HL: 60, ML: 55, LL: 15 },
  { name: '>1200', HL: 90, ML: 45, LL: 50 },
];

const lineData = [
  { name: 'Jan', Sold: 120, Profit: 100 },
  { name: 'Feb', Sold: 132, Profit: 110 },
  { name: 'Mar', Sold: 101, Profit: 130 },
  { name: 'Apr', Sold: 134, Profit: 100 },
  { name: 'May', Sold: 90,  Profit: 120 },
  { name: 'Jun', Sold: 130, Profit: 140 },
  { name: 'Jul', Sold: 150, Profit: 150 },
  { name: 'Aug', Sold: 120, Profit: 100 },
  { name: 'Sep', Sold: 130, Profit: 120 },
  { name: 'Oct', Sold: 140, Profit: 150 },
  { name: 'Nov', Sold: 140, Profit: 145 },
];

const STATIC_OPTIONS = [
 'business products   services',
 'consumer products   services',
 'it management',
 'real estate',
 'financial services',
 'engineering',
 'security',
 'logistics   transportation', 
 'insurance',
 'telecommunications',
 'manufacturing', 
 'travel   hospitality', 
 'software', 
 'construction',
 'environmental services', 
 'health', 
 'education', 
 'advertising   marketing', 
 'human resources', 
 'food   beverage', 
 'government services',
 'media', 
 'energy',
 'retail',
 'it system development', 
 'it services', 
 'computer hardware'
];

const ALGORITHMS = ["LSH", "KMEANS", "BISECTING_KMEANS"];


export default function FacultyDashboard() {
  const [selectedOption, setSelectedOption] = useState('engineering'); // Default για να μοιάζει με το screenshot
  const [fileType, setFileType] = useState('researcher');
  const [loading, setLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState({ type: '', text: '' });
  
  // Dummy results για να γεμίσουν οι πίνακες αν δεν τρέξει API
  const [results, setResults] = useState([
    { name: 'India', code: 'IN', pop: '1,234,171,354', size: '3,287,263', density: '462.82' },
    { name: 'China', code: 'CN', pop: '1,402,111,222', size: '9,596,961', density: '146.24' },
    { name: 'Italy', code: 'IT', pop: '60,461,826', size: '301,340', density: '200.77' },
    { name: 'United States', code: 'US', pop: '327,167,434', size: '9,833,520', density: '35.27' },
    { name: 'Canada', code: 'CA', pop: '37,602,103', size: '9,984,670', density: '3.77' },
  ]);
  
  const [algorithms, setAlgorithms] = useState(['LSH', 'KMEANS']); 

  const handleAlgorithmChange = (event) => {
    const { target: { value } } = event;
    setAlgorithms(typeof value === 'string' ? value.split(',') : value);
  };

  const handleRun = async () => {
    setLoading(true);
    // Προσομοίωση API call
    setTimeout(() => {
        setLoading(false);
        alert("Run Complete (Simulation)");
    }, 1500);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline /> {/* Αυτό κάνει όλη τη σελίδα μαύρη */}
      
      <Box sx={{ p: 3, maxWidth: '1600px', margin: '0 auto' }}>
        
        {/* --- HEADER SECTION --- */}
        <Paper elevation={3} sx={{ p: 2, mb: 3, borderRadius: 2, position: 'relative' }}>
          
          {/* Top Row: Title & Action Icons */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }} /> {/* Spacer left */}
            <Typography variant="h5" sx={{ flex: 1, textAlign: 'center', color: '#eee' }}>
              Faculty Dataset
            </Typography>
            <Box sx={{ flex: 1, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                <IconButton sx={{ bgcolor: '#333', color: '#fff' }}><ShareIcon /></IconButton>
                <IconButton sx={{ bgcolor: '#333', color: '#fff' }}><ContentCopyIcon /></IconButton>
                <IconButton sx={{ bgcolor: '#333', color: '#fff' }}><DownloadIcon /></IconButton>
            </Box>
          </Box>

          {/* Controls Row */}
          <Grid container spacing={2} alignItems="center">
            
            {/* Search / Select Option */}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Select Option</InputLabel>
                <Select
                  value={selectedOption}
                  label="Select Option"
                  onChange={(e) => setSelectedOption(e.target.value)}
                >
                  {STATIC_OPTIONS.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>

            {/* Radio Buttons */}
            <Grid item xs={12} md={3} sx={{ display: 'flex', justifyContent: 'center' }}>
                <RadioGroup row value={fileType} onChange={(e) => setFileType(e.target.value)}>
                    <FormControlLabel value="start-up" control={<Radio />} label="start-up" />
                    <FormControlLabel value="researcher" control={<Radio />} label="researcher" />
                </RadioGroup>
            </Grid>

            {/* Algorithms */}
            <Grid item xs={12} md={3}>
                 <FormControl size="small" fullWidth>
                    <InputLabel>Algorithms</InputLabel>
                    <Select
                        multiple
                        value={algorithms}
                        onChange={handleAlgorithmChange}
                        input={<OutlinedInput label="Algorithms" />}
                        renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                            ))}
                        </Box>
                        )}
                    >
                        {ALGORITHMS.map((algo) => (
                        <MenuItem key={algo} value={algo}>{algo}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            {/* RUN Button */}
            <Grid item xs={12} md={2} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                    variant="contained" 
                    color="success" 
                    fullWidth
                    onClick={handleRun}
                    disabled={loading}
                    sx={{ height: 40, fontWeight: 'bold' }}
                >
                    {loading ? <CircularProgress size={24} color="inherit"/> : "RUN"}
                </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* --- MAIN GRID LAYOUT (2x2) --- */}
        {/* --- MAIN GRID LAYOUT (2 Columns: Left=Charts, Right=Tables) --- */}
        <Grid container spacing={50}>
            
            {/* --- LEFT COLUMN: CHARTS --- */}
            <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    
                    {/* 1. Bar Chart (Top Left) */}
                    <Paper sx={{ p: 2, height: 350, display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="subtitle1" gutterBottom>Average Rates</Typography>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={barData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="name" stroke="#fff" />
                                <YAxis stroke="#fff" />
                                <RechartsTooltip contentStyle={{ backgroundColor: '#333' }} />
                                <Legend />
                                <Bar dataKey="HL" stackId="a" fill="#42a5f5" />
                                <Bar dataKey="ML" stackId="a" fill="#ff7043" />
                                <Bar dataKey="LL" stackId="a" fill="#bdbdbd" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Paper>

                    {/* 2. Line Chart (Bottom Left) */}
                    <Paper sx={{ p: 2, height: 350, display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="h6" align="center" gutterBottom>Units Sold VS Profit</Typography>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={lineData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="name" stroke="#fff" />
                                <YAxis stroke="#fff" />
                                <RechartsTooltip contentStyle={{ backgroundColor: '#333' }} />
                                <Legend />
                                <Line type="monotone" dataKey="Sold" stroke="#90caf9" strokeWidth={2} dot={{r:4}} />
                                <Line type="monotone" dataKey="Profit" stroke="#66bb6a" strokeWidth={2} dot={{r:4}} />
                            </LineChart>
                        </ResponsiveContainer>
                    </Paper>

                </Box>
            </Grid>

            {/* --- RIGHT COLUMN: TABLES --- */}
            <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    
                    {/* 3. Table 1 (Top Right) */}
                    <Paper sx={{ height: 350, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                        <TableContainer sx={{ flex: 1 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Code</TableCell>
                                        <TableCell align="right">Population</TableCell>
                                        <TableCell align="right">Size (km²)</TableCell>
                                        <TableCell align="right">Density</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {results.map((row, idx) => (
                                        <TableRow key={idx} hover sx={{ '&:nth-of-type(odd)': { backgroundColor: '#252525' } }}>
                                            <TableCell>{row.name}</TableCell>
                                            <TableCell>{row.code}</TableCell>
                                            <TableCell align="right">{row.pop}</TableCell>
                                            <TableCell align="right">{row.size}</TableCell>
                                            <TableCell align="right">{row.density}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>

                    {/* 4. Table 2 (Bottom Right - Duplicate) */}
                    <Paper sx={{ height: 350, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                        <TableContainer sx={{ flex: 1 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Code</TableCell>
                                        <TableCell align="right">Population</TableCell>
                                        <TableCell align="right">Size (km²)</TableCell>
                                        <TableCell align="right">Density</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {results.map((row, idx) => (
                                        <TableRow key={idx} hover sx={{ '&:nth-of-type(odd)': { backgroundColor: '#252525' } }}>
                                            <TableCell>{row.name}</TableCell>
                                            <TableCell>{row.code}</TableCell>
                                            <TableCell align="right">{row.pop}</TableCell>
                                            <TableCell align="right">{row.size}</TableCell>
                                            <TableCell align="right">{row.density}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>

                </Box>
            </Grid>

        </Grid>
      </Box>
    </ThemeProvider>
  );
}