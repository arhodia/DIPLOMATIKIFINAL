import { Grid, Box, Typography } from '@mui/material';
import TablesSection from './TablesSection'; // Το νέο component για τους πίνακες
import MetricSection from './MetricSection'; 
import ScatterSection from './ScatterSection';
import GeneralResults from './GeneralResults';
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
        
        <Grid>
          <></>
            <GeneralResults allAlgorithmsData={allAlgorithmsData} />
            <MetricSection allAlgorithmsData={allAlgorithmsData} />
            <TablesSection allAlgorithmsData={allAlgorithmsData} />
            <ScatterSection allAlgorithmsData={allAlgorithmsData}/>
        </Grid>


      </Grid>
    </Box>
  );
};

export default ResultsSection;