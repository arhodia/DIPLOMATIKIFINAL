import React from 'react';
import { 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Typography, 
  Box 
} from '@mui/material';

// Ορίζουμε τις στήλες του πίνακα μετρήσεων
const columns = [
  { id: 'algorithm', label: 'Algorithm', minWidth: 150 },
  { id: 'best_k', label: 'Best K', minWidth: 80, align: 'center' },
  { id: 'best_sample_frac', label: 'Sample Frac', minWidth: 100, align: 'center' },
  { id: 'best_score', label: 'Best Score', minWidth: 100, align: 'right', format: (value) => value.toFixed(6) },
  { id: 'time', label: 'Time (sec)', minWidth: 100, align: 'right', format: (value) => value.toFixed(4) },
];

const MetricsSection = ({ allAlgorithmsData }) => {
  // Αν δεν υπάρχουν δεδομένα, δεν εμφανίζουμε τίποτα
  if (!allAlgorithmsData || Object.keys(allAlgorithmsData).length === 0) {
    return null;
  }

  // Μετατροπή των δεδομένων σε λίστα για τον πίνακα
  // Υποθέτουμε ότι το backend επιστρέφει αυτά τα πεδία (best_k, time, κλπ) μέσα στο αντικείμενο του κάθε αλγορίθμου
  const rows = Object.entries(allAlgorithmsData).map(([algoName, data]) => {
    return {
      algorithm: algoName,
      // Χρησιμοποιούμε optional chaining (?. ||) σε περίπτωση που λείπει κάποια τιμή για να μην σκάσει
      best_k: data.best_k ?? '-',
      best_sample_frac: data.best_sample_frac ?? '-',
      best_score: data.best_score ?? 0,
      time: data.time ?? 0 
    };
  });

  return (
    <Box sx={{ pb: 5, mt: 4 }}>
      <Typography variant="h5" sx={{ mb: 3, textAlign: 'center', color: '#fff' }}>
        Συγκριτικά Αποτελέσματα Αλγορίθμων
      </Typography>

      <Paper sx={{ width: '100%', overflow: 'hidden', boxShadow: 3, bgcolor: '#1e1e1e' }}>
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader aria-label="metrics table">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align}
                    style={{ minWidth: column.minWidth }}
                    sx={{ 
                      bgcolor: '#333', 
                      color: '#fff', 
                      fontWeight: 'bold',
                      borderBottom: '1px solid #555'
                    }}
                  >
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, index) => {
                return (
                  <TableRow hover role="checkbox" tabIndex={-1} key={row.algorithm}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell 
                            key={column.id} 
                            align={column.align}
                            sx={{ color: '#e0e0e0', borderBottom: '1px solid #444' }}
                        >
                          {/* Ειδική μορφοποίηση για score και χρόνο αν είναι αριθμοί */}
                          {column.format && typeof value === 'number'
                            ? column.format(value)
                            : value}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default MetricsSection;