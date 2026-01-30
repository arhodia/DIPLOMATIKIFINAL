import React from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow 
} from '@mui/material';

const columns = [
  { id: 'algorithm', label: 'Algorithm', minWidth: 170 },
  { 
    id: 'time', 
    label: 'Time (sec)', 
    minWidth: 100, 
    align: 'right',
    format: (value) => (typeof value === 'number' ? value.toFixed(4) : value),
  },
];

const GeneralResults = ({ allAlgorithmsData }) => {
  // 1. Πρόσβαση στα δεδομένα βάσει του screenshot
  const rawData = allAlgorithmsData?.Classification_Results?.execution_time || [];

  // 2. Mapping των δεδομένων
  const rows = rawData.map((item, index) => ({
    id: index,
    algorithm: item[0] || 'Unknown',
    time: item[1] ?? 0,
  }));

  return (
    <Box sx={{ mb: 4, width: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'white', textAlign: 'center' }}>
        Algorithm Execution Time
      </Typography>

      <Paper sx={{ 
        width: '100%', 
        overflow: 'hidden', 
        boxShadow: 3, 
        bgcolor: '#1e1e1e', // Σκούρο background για να δένει με το dashboard
        backgroundImage: 'none',
        border: '1px solid #333'
      }}>
        <TableContainer>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align}
                    style={{ 
                      minWidth: column.minWidth,
                      backgroundColor: '#252525', // Ελαφρώς πιο ανοιχτό γκρι για το header
                      color: '#fff',
                      fontWeight: 'bold',
                      borderBottom: '2px solid #444'
                    }}
                  >
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length > 0 ? (
                rows.map((row) => (
                  <TableRow hover key={row.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell 
                          key={column.id} 
                          align={column.align}
                          sx={{ color: '#e0e0e0', borderBottom: '1px solid #333' }}
                        >
                          {column.format ? column.format(value) : value}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={2} align="center" sx={{ color: '#888', py: 3 }}>
                    No execution data available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {/* Αφαιρέσαμε το TablePagination αφού τα rows είναι < 5 */}
      </Paper>
    </Box>
  );
};

export default GeneralResults;