import React from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Typography,
  Box 
} from '@mui/material';

const GeneralResults = ({ allAlgorithmsData }) => {
  // Ανάκτηση του execution_time από τα δεδομένα
  const executionTimes = allAlgorithmsData?.execution_time || [];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
        Algorithm Execution Time
      </Typography>
      
      <TableContainer component={Paper} sx={{ maxWidth: 400, boxShadow: 2 }}>
        <Table size="small" aria-label="execution time table">
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Algorithm</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Time (sec)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executionTimes.length > 0 ? (
              executionTimes.map((row, index) => (
                <TableRow key={index} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell component="th" scope="row">
                    {row.algorithm}
                  </TableCell>
                  <TableCell align="right">
                    {row.time.toFixed(4)}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={2} align="center">
                  There is no time data
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default GeneralResults;