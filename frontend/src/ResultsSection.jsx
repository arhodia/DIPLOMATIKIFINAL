import React from 'react';
import { Grid, Box, Typography } from '@mui/material';
import ChartSection from './ChartSection';
import TablesSection from './TablesSection'; // Το νέο component για τους πίνακες
import MetricSection from './MetricSection'; 


const ResultsSection = ({ allAlgorithmsData }) => {
  // Ασφάλεια
  if (!allAlgorithmsData || Object.keys(allAlgorithmsData).length === 0) {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography>Δεν βρέθηκαν αποτελέσματα.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 4, color: 'text.primary', textAlign: 'center' }}>
        Dashboard Ανάλυσης
      </Typography>

      <Grid container spacing={3}>
        
        {/* ΑΡΙΣΤΕΡΗ ΣΤΗΛΗ: ΓΡΑΦΗΜΑΤΑ */}
        <Grid item xs={12}>
            <ChartSection  allAlgorithmsData={allAlgorithmsData} />
            <MetricSection allAlgorithmsData={allAlgorithmsData} />
            <TablesSection allAlgorithmsData={allAlgorithmsData} />
        </Grid>


      </Grid>
    </Box>
  );
};

export default ResultsSection;