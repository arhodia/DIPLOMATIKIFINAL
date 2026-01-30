import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import Grid from '@mui/material/Grid'; // Προτείνεται η χρήση του Grid2 στην τελευταία έκδοση MUI
import { styled } from '@mui/material/styles';

// Εισαγωγή των components σου
import GeneralResults from './GeneralResults';
import MetricSection from './MetricSection';
import TablesSection from './TablesSection';
import ScatterSection from './ScatterSection';
import TableClustering from './TableClustering';



const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: 'center',
  color: (theme.vars ?? theme).palette.text.secondary,
  ...theme.applyStyles('dark', {
    backgroundColor: '#1A2027',
  }),
}));
const ResultsSection = ({ allAlgorithmsData }) => {
  if (!allAlgorithmsData || Object.keys(allAlgorithmsData).length === 0) {
    return (
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Δεν βρέθηκαν αποτελέσματα.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" sx={{ mb: 4, textAlign: 'center', fontWeight: 'bold' }}>
        Dashboard Ανάλυσης
      </Typography>

      <Box sx={{ flexGrow: 1 }}>
     
          <Grid container spacing={2} columns={16}> 
            <Grid size={8}>
              <Item><GeneralResults allAlgorithmsData={allAlgorithmsData} /></Item>
            </Grid>
            <Grid size={8}>
              <Item>size=8</Item>
            </Grid>
          </Grid>

          <Grid container spacing={2} columns={16} sx={{ mt: 2 }}> {/* Πρόσθεσα mt: 2 για λίγο κενό μεταξύ των containers */}
            <Grid size={16}>
              <Grid container spacing={2} columns={16} sx={{ mt: 2 }}>
                {/* Πρώτη στήλη: 50% του πλάτους */}
               <Grid size={8}>
                  <Item>
                    {/* Εσωτερικό Grid για να δημιουργήσουμε τις 2 "γραμμές" */}
                    <Grid container direction="column" spacing={2}>
                      
                      {/* 1η Γραμμή: MetricSection */}
                      <Grid size={12}> 
                        <MetricSection allAlgorithmsData={allAlgorithmsData} dataType="matching_recommended" />
                      </Grid>

                      {/* 2η Γραμμή: Typography & TablesSection */}
                     <Grid size={12}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Results (K-Means/Bisecting)
                      </Typography>

                        {/* Κεντρικό Container για το 50-50 split */}
                        <Grid container spacing={2}>
                          
                          {/* Αριστερή Στήλη (50%) */}
                          <Grid size={6}>
                            <Grid container spacing={2} direction="column">
                              {/* 1η Γραμμή Αριστερά: KMeans Scatter */}
                              <Grid>
                                <Item>
                                  <ScatterSection 
                                    allAlgorithmsData={allAlgorithmsData} 
                                    algorithmType="KMeans" 
                                  />
                                </Item>
                              </Grid>
                              
                              {/* 2η Γραμμή Αριστερά: Tables Section */}
                              <Grid size={12}>
                                <Grid >
                                  <Item>
                                    <TableClustering 
                                      allAlgorithmsData={allAlgorithmsData} 
                                      algorithm="KMeans" 
                                      resultType="matching_results" 
                                    />
                                  </Item>
                                </Grid>

                                <Grid >
                                  <Item>
                                    <TableClustering 
                                      allAlgorithmsData={allAlgorithmsData} 
                                      algorithm="KMeans" 
                                      resultType="recommended_results"
                                    />
                                  </Item>
                                </Grid>
                              </Grid>

                            </Grid>
                          </Grid>

                          {/* Δεξιά Στήλη (50%) */}
                          <Grid size={6}>
                            <Grid container spacing={2} direction="column">
                              {/* 1η Γραμμή Δεξιά: BisectingKMeans Scatter */}
                              <Grid>
                                <Item>
                                  <ScatterSection 
                                    allAlgorithmsData={allAlgorithmsData} 
                                    algorithmType="BisectingKMeans" 
                                  />
                                </Item>
                              </Grid>
                              
                              {/* 2η Γραμμή Αριστερά: Tables Section */}
                               <Grid size={12}>
                                <Grid >
                                  <Item>
                                    <TableClustering 
                                      allAlgorithmsData={allAlgorithmsData} 
                                      algorithm="BisectingKMeans" 
                                      resultType="matching_results" 
                                    />
                                  </Item>
                                </Grid>

                                <Grid >
                                  <Item>
                                    <TableClustering 
                                      allAlgorithmsData={allAlgorithmsData} 
                                      algorithm="BisectingKMeans" 
                                      resultType="recommended_results"
                                    />
                                  </Item>
                                </Grid>
                              </Grid>
                            
                              {/* Υπόλοιπο περιεχόμενο δεξιάς στήλης αν υπάρχει */}
                            </Grid>
                          </Grid>

                        </Grid>
                    </Grid>

                    </Grid>
                  </Item>
                </Grid>

                {/* Δεύτερη στήλη: 25% του πλάτους */}
                <Grid size={4}>
                <Item sx={{ height: '100%', overflow: 'hidden' }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: 'secondary.main' }}>
                    LSH BRP Results
                  </Typography>
                  {/* Καλούμε το TablesSection με tableType="brp" */}
                  <TablesSection 
                    allAlgorithmsData={allAlgorithmsData} 
                    tableType="brp" 
                  />
                </Item>
                </Grid>

                {/* Τρίτη στήλη: 25% του πλάτους */}
                <Grid size={4}>
                <Item sx={{ height: '100%', overflow: 'hidden' }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: 'secondary.main' }}>
                    LSH MiniHash Results
                  </Typography>
                  {/* Καλούμε το TablesSection με tableType="minihash" */}
                  <TablesSection 
                    allAlgorithmsData={allAlgorithmsData} 
                    tableType="minihash" 
                  />
                </Item>
              </Grid>
              </Grid>
            </Grid>
          </Grid>
  
              
      </Box>
    </Box>
  );
};

export default ResultsSection;