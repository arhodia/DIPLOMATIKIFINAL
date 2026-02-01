import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  ThemeProvider, 
  CssBaseline, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TablePagination, 
  TableRow, 
  Typography 
} from '@mui/material';
import { darkTheme } from './theme';

// Ορισμός των στηλών βάσει των απαιτήσεών σου
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

// Ξεχωριστό component για τον πίνακα ώστε να επαναχρησιμοποιηθεί
const StickyTable = ({ title, data }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  if (!data || data.length === 0) return null;

  return (
    <Box sx={{ mb: 0 }}>
      <Typography variant="h6" gutterBottom sx={{ color: 'white', ml: 1 }}>
        {title}
      </Typography>
      <Paper sx={{ width: '100%', overflow: 'hidden', bgcolor: 'background.paper' }}>
        <TableContainer sx={{ height: 400, overflow: 'auto' }}>
          <Table stickyHeader aria-label="sticky table">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align}
                    style={{ minWidth: column.minWidth }}
                  >
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {data
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => {
                  return (
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
                  );
                })}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 100]}
          component="div"
          count={data.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

const TableSection = ({ allAlgorithmsData, tableType, dataType }) => {
  // 1. Εξασφαλίζουμε ότι παίρνουμε το σωστό τύπο (γιατί στο ResultsSection χρησιμοποιείς και τα δύο ονόματα props)
  const activeType = tableType || dataType;

  // 2. Εξαγωγή των δεδομένων με ασφάλεια (fallback σε άδειο πίνακα [])
  const brpData = allAlgorithmsData?.Classification_Results?.lsh_brp || [];
  const minihashData = allAlgorithmsData?.Classification_Results?.lsh_minihash || [];

  // 3. Ορισμός του currentData βάσει του τι ζητήθηκε
  const currentData = activeType === 'brp' ? brpData : minihashData;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ width: '100%', mt: 1 }}>
        
        {/* Έλεγχος αν υπάρχουν δεδομένα στον πίνακα */}
        {currentData && currentData.length > 0 ? (
          <StickyTable 
            title={activeType === 'brp' ? "LSH BRP Results" : "LSH Minihash Results"} 
            data={currentData} 
          />
        ) : (
          /* Εμφάνιση μηνύματος αν ο πίνακας είναι άδειος */
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
            <Typography  sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
              Δεν υπάρχουν διαθέσιμα δεδομένα για το συγκεκριμένο αλγόριθμο
            </Typography>
          </Box>
        )}

      </Box>
    </ThemeProvider>
  );
};

export default TableSection;