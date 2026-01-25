// theme.js
import { createTheme } from "@mui/material";

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
    primary: {
      main: '#90caf9',
    },
    success: {
      main: '#2e7d32',
    }
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h4: { fontWeight: 600 },
    h6: { fontWeight: 500 },
  },
  components: {
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #333',
        },
        head: {
          backgroundColor: '#2c2c2c',
          color: '#fff',
          fontWeight: 'bold',
        }
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          '& fieldset': { borderColor: '#555' },
          '&:hover fieldset': { borderColor: '#888' },
        }
      }
    },
    // Προσθέτουμε ένα global style για το Paper για να έχουν όλα το ίδιο ύψος/στυλ
    MuiPaper: {
        styleOverrides: {
            root: {
                borderRadius: 8,
            }
        }
    }
  }
});
