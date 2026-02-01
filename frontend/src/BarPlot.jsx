import * as React from 'react';
import { BarChart } from '@mui/x-charts/BarChart';
import { Stack, Typography, createTheme, ThemeProvider, CssBaseline } from '@mui/material';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const AlgorithmExecutionChart = ({ allAlgorithmsData }) => {
  // 1. Προετοιμασία Δεδομένων
  const rawData = allAlgorithmsData?.Classification_Results?.execution_time || [];
  
  // Τα ονόματα των αλγορίθμων (π.χ. ["KMeans", "BisectingKMeans"])
  const labels = rawData.map((item) => item[0] || 'Unknown');
  // Οι τιμές χρόνου (π.χ. [0.911, 7.316])
  const values = rawData.map((item) => item[1] ?? 0);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Stack spacing={2} sx={{ p: 4, alignItems: 'center', width: '100%', minHeight: 500 }}>
        
        <Typography variant="h6">
          Algorithm Execution Time Comparison
        </Typography>

        {/* 2. Υλοποίηση BarChart */}
        <BarChart
          // Ο άξονας Χ παίρνει τα labels (KMeans, κλπ)
          xAxis={[{ 
            scaleType: 'band', 
            data: labels,
            label: 'Algorithms' 
          }]}
          // Τα δεδομένα (χρόνος) μπαίνουν στο series
          series={[{ 
            data: values, 
            label: 'Time (s)',
            color: '#1976d2' // Μπορείς να αλλάξεις το χρώμα
          }]}
          width={600}
          height={400}
        />
        
      </Stack>
    </ThemeProvider>
  );
};

export default AlgorithmExecutionChart;