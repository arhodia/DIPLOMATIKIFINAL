import React, { useState } from 'react';
import { 
  Box, Paper, Table, TableBody, TableCell, TableContainer, 
  TableHead, TablePagination, TableRow, Typography, ThemeProvider, CssBaseline 
} from '@mui/material';
import { darkTheme } from './theme';

const columns = [
  { id: 'id', label: 'ID', minWidth: 70 },
  { id: 'researcher_id', label: 'Researcher ID', minWidth: 100 },
  { id: 'researcher_name', label: 'Name', minWidth: 130 },
  { id: 'surname', label: 'Surname', minWidth: 130 },
  { id: 'source_type', label: 'Source Type', minWidth: 120 },
  { id: 'age', label: 'Age', minWidth: 70 },
  { id: 'profile', label: 'Profile', minWidth: 150 },
  { id: 'company_name', label: 'Company', minWidth: 150 },
  { id: 'url', label: 'URL', minWidth: 150 },
  { id: 'distance_to_center', label: 'Distance', minWidth: 100, align: 'right' },
];

const TableClustering = ({ allAlgorithmsData, algorithm, resultType }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Δυναμική πρόσβαση στα δεδομένα: matching_results ή recommended_results
  // και μετά στον αλγόριθμο: KMeans ή BisectingKMeans
  const currentData = allAlgorithmsData?.Classification_Results?.[resultType]?.[algorithm] || [];

  const handleChangePage = (event, newPage) => setPage(newPage);
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  // Έλεγχος αν υπάρχουν δεδομένα
  if (currentData.length === 0) {
    return (
         <Box 
                  sx={{ 
                    p: 4,               // Αυξήθηκε λίγο το padding για καλύτερη αίσθηση κενού χώρου
                    textAlign: 'center', 
                    border: 'none',     // Αφαίρεση του πλαισίου
                    borderRadius: 2,
                    boxShadow: '0px 10px 15px -10px rgba(0,0,0,0.5)',
                    bgcolor: 'transparent' // Ή κράτα το 'rgba(255,255,255,0.02)' αν θες ελαφρύ φόντο
                  }}
                >
        <Typography sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
          Δεν υπάρχουν {resultType.replace('_', ' ')} για τον  {algorithm}
        </Typography>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Paper sx={{ width: '100%', overflow: 'hidden', mb: 4, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle1" sx={{ p: 2, fontWeight: 'bold', textTransform: 'capitalize' }}>
          {resultType.replace('_', ' ')} - {algorithm}
        </Typography>
        <TableContainer sx={{ height: 400, overflow: 'auto' }}>
          <Table stickyHeader aria-label="sticky table">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column.id} align={column.align} style={{ minWidth: column.minWidth }}>
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {currentData
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => (
                  <TableRow hover role="checkbox" tabIndex={-1} key={row.id || index}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell key={column.id} align={column.align}>
                          {value !== undefined && value !== null ? value : '-'}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 100]}
          component="div"
          count={currentData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </ThemeProvider>
  );
};

export default TableClustering;