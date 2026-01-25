import React, { useState } from 'react';
import { Box, Container, CircularProgress, Alert, ThemeProvider, CssBaseline } from '@mui/material'; 
import DashboardHeader from './DashboardHeader';
import ResultsSection from './ResultsSection'; // Πλέον αυτό είναι ο Container
import { darkTheme } from './theme'; 

const FacultyDashboard = () => {
  const [filters, setFilters] = useState({
    industry: '',
    algorithms: [],
    radioOption: '',
    name:'',
    neighbor:''
  });

  const [allData, setAllData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setAllData(null);

    try {
      const response = await fetch('http://localhost:5001/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      
      // --- FIX STARTS HERE ---
    // Check if the API returned the "matches" structure seen in your screenshot
    if (data.matches) {
        // We wrap it to match the structure expected by ChartsSection/TablesSection
        setAllData({
            "Classification Results": { // You can use dynamic name based on filters if needed
                hyperparameters_results:data.hyperparameters,  
                matching_results: data.matches,
                execution_time:data.execution_time,
                lsh_brp:data.lsh_brp,
                lsh_minihash:data.lsh_minihash

            }
        });
    } 
    // Fallback if the API returns the old/expected dictionary format
    else if (Object.keys(data).length > 0) {
        setAllData(data); 
    } else {
        setAllData(null); 
    }
    // --- FIX ENDS HERE ---

  } catch (err) {
      setError('Υπήρξε πρόβλημα κατά τη λήψη δεδομένων.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (industry, value) => {
    setFilters(prev => ({ ...prev, [industry]: value }));
  };

  return (
  <ThemeProvider theme={darkTheme}>
    <CssBaseline />

    {/* Wrapper που ελέγχει το πλάτος της σελίδας */}
    <Box
      sx={{
        width: "100%",  // Πιάνει όλο το διαθέσιμο πλάτος
        maxWidth: { xs: "90%", md: "95%", xl: "95%" }, // Βάζει όριο στο πόσο μπορεί να απλωθεί
        mx: "auto",     // Το "μαγικό" συστατικό: Μοιράζει αυτόματα τον υπόλοιπο χώρο αριστερά/δεξιά
        display: "block", // Εξασφαλίζει τη σωστή συμπεριφορά block στοιχείου
        py: 4,
      }}
    >
      <DashboardHeader
        filters={filters}
        onFilterChange={handleFilterChange}
        onSubmit={handleSearch}
      />

    <Box   
      sx={{
        width: "100%",  // Πιάνει όλο το διαθέσιμο πλάτος
        maxWidth: { xs: "90%", md: "95%", xl: "95%" }, // Βάζει όριο στο πόσο μπορεί να απλωθεί
        mx: "auto",     // Το "μαγικό" συστατικό: Μοιράζει αυτόματα τον υπόλοιπο χώρο αριστερά/δεξιά
        display: "block", // Εξασφαλίζει τη σωστή συμπεριφορά block στοιχείου
        py: 4,
      }}>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {allData && <ResultsSection allAlgorithmsData={allData} />}
      </Box>
    </Box>
  </ThemeProvider>
);
};

export default FacultyDashboard;