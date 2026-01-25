import React, { useState } from 'react';
import { 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TablePagination, 
  TableRow, 
  Typography, 
  Box, 
  Divider,
  Link 
} from '@mui/material';

// Ορισμός στηλών με βάση τα κόκκινα υπογραμμισμένα πεδία στα screenshots
const columns = [
  { id: 'researcher_name', label: 'Researcher Name', minWidth: 80 },
  { id: 'university', label: 'University', minWidth: 80 },
  { id: 'age', label: 'Age', minWidth: 50 },
  { id: 'source_type', label: 'Type', minWidth: 80 },
  { id: 'company_name', label: 'Company', minWidth: 80 },
  { id: 'industry', label: 'Industry', minWidth: 120 },
  { id: 'city', label: 'City', minWidth: 80 },
  { id: 'state', label: 'State', minWidth: 60 },
  // Για τα URL και Profile, μπορούμε να τα δείξουμε ως απλό κείμενο ή Link
  { id: 'url', label: 'URL', minWidth: 100 },
  { id: 'profile', label: 'Profile', minWidth: 100 },
];

const AlgorithmTable = ({ rows, algoName }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  return (
    <Paper sx={{ width: '100%', maxWidth: '100%', margin: 'auto', overflow: 'hidden', boxShadow: 4 }}>
      <TableContainer sx={{ maxHeight: 440, overflowX: 'auto' }}> 
        <Table stickyHeader size="small" aria-label={`${algoName} table`}>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align}
                  style={{ minWidth: column.minWidth }}
                  sx={{ 
                    fontWeight: 'bold', 
                    bgcolor: '#333', 
                    color: 'white',
                    whiteSpace: 'nowrap', // Για να μην σπάει το header
                    py: 1 
                  }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((row, index) => {
                return (
                  // Χρήση του index ως key γιατί τα ID μπορεί να είναι nan
                  <TableRow hover role="checkbox" tabIndex={-1} key={index}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      
                      // Έλεγχος για "καθάρισμα" τιμών (nan, null, None)
                      let displayValue = value;
                      if (value === null || value === undefined || value === 'nan' || value === 'None') {
                        displayValue = '-';
                      }

                      return (
                        <TableCell key={column.id} align={column.align}>
                          {/* Ειδικός χειρισμός αν θέλουμε τα URL να είναι clickable */}
                          {(column.id === 'url' || column.id === 'profile') && displayValue !== '-' ? (
                             <span style={{ fontSize: '0.85rem', color: '#14575c' }}>{displayValue}</span>
                          ) : (
                             displayValue
                          )}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};

const TablesSection = ({ allAlgorithmsData }) => {
  if (!allAlgorithmsData || Object.keys(allAlgorithmsData).length === 0) {
    return null; 
  }

  const algorithmsList = Object.entries(allAlgorithmsData);

  return (
    <Box sx={{ pb: 5, width: '100%' }}>
      <Typography variant="h5" sx={{ mb: 3, textAlign: 'center', fontWeight: 'bold' }}>
        Αποτελέσματα Ταξινόμησης (Matching Results)
      </Typography>

      {algorithmsList.map(([algoName, algoContent], index) => {
        // Τραβάμε τα δεδομένα από το 'matching_results'
        const rows = algoContent.matching_results || [];
        
        if (rows.length === 0) return null;

        return (
          <Box key={algoName} sx={{ mb: 6, px: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#a4bd4a', fontWeight: 'bold' }}>
              Αλγόριθμος: {algoName}
            </Typography>

            <AlgorithmTable rows={rows} algoName={algoName} />
            
            {index < algorithmsList.length - 1 && <Divider sx={{ my: 4 }} />}
          </Box>
        );
      })}
    </Box>
  );
};

export default TablesSection;