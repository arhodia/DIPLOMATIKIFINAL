
import { Paper, Button, Select, MenuItem, RadioGroup, FormControlLabel, Radio, Box, Chip, OutlinedInput, Slider} from '@mui/material';
import TextField from '@mui/material/TextField';
const DashboardHeader = ({ filters, onFilterChange, onSubmit }) => {
 const STATIC_OPTIONS = [
  'business products   services',
  'consumer products   services',
  'it management',
  'real estate',
  'financial services',
  'engineering',
  'security',
  'logistics   transportation',
  'insurance',
  'telecommunications',
  'manufacturing',
  'travel   hospitality',
  'software',
  'construction',
  'environmental services',
  'health',
  'education',
  'advertising   marketing',
  'human resources',
  'food   beverage',
  'government services',
  'media',
  'energy',
  'retail',
  'it system development',
  'it services',
  'computer hardware'
  ];
  // Η πηγή δεδομένων παρέμεινε ακριβώς όπως ζήτησες
  const ALGORITHMS = ["LSH_BRP", "LSH_MinHash","KMeans", "BisectingKMeans"];
  // Συνάρτηση για τη διαγραφή ενός αλγορίθμου μέσω του Chip 'X'
  const handleDeleteAlgorithm = (algoToDelete) => {
  // Φιλτράρουμε το array για να βγάλουμε αυτόν που διαγράφηκε
  // Προϋποθέτει ότι το filters.algorithms είναι Array
  const newSelection = filters.algorithms.filter((algo) => algo !== algoToDelete);
  // Ενημερώνουμε τον γονέα με το νέο array
  onFilterChange('algorithms', newSelection);
  };
  
  const MIN_K = 3;
  const MAX_K = 80;

  const parsed = Number(filters.neighbor);
  const kValue =
  filters.neighbor === '' || Number.isNaN(parsed)
    ? MIN_K
    : Math.min(MAX_K, Math.max(MIN_K, parsed));


  const handleNeighborChange = (e) => {
  const v = e.target.value;

  if (v === '') {
    onFilterChange('neighbor', '');
    return;
  }

  if (!/^\d+$/.test(v)) return;

  const n = Number(v);
  if (n < MIN_K || n > MAX_K) return;

  onFilterChange('neighbor', v);
};
  return (
    <Paper elevation={3} sx={{ p:3,mx:2,my:2, width: '100%',display: 'flex',alignItems: 'center',  minHeight: 120 ,justifyContent: 'space-between', flexWrap: 'wrap' }}>

      {/* Ομάδα Input Fields - Μετακίνηση δεξιά */}
      <Box sx={{ 
          display: 'flex', 
          gap:2, 
          alignItems: 'center', 
          flexWrap: 'wrap',
          ml: 4 // 2. Μετακινεί όλο το γκρουπ των inputs πιο δεξιά (Margin Left)
      }}>

        {/* --- Select 1: Industry --- */}
        <Select
          size="small"
          value={filters.industry}
          onChange={(e) => onFilterChange('industry', e.target.value)}
          displayEmpty
          MenuProps={{ PaperProps: { sx: { maxHeight: 300 } } }}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="" sx={{ display: 'none' }}><em>Select Category</em></MenuItem>
          {STATIC_OPTIONS.map((option) => (
            <MenuItem key={option} value={option}>{option}</MenuItem>
          ))}
        </Select>

        {/* --- Select 2: Algorithms --- */}
        <Select
          size="small"
          multiple
          value={filters.algorithms}
          onChange={(e) => onFilterChange('algorithms', e.target.value)}
          displayEmpty
          sx={{ minWidth: 250 }}
          input={<OutlinedInput />}
          renderValue={(selected) => {
            if (selected.length === 0) return <em>Select Algorithm</em>;
            return (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value} onDelete={() => handleDeleteAlgorithm(value)} onMouseDown={(e) => e.stopPropagation()} />
                ))}
              </Box>
            );
          }}
        >
          <MenuItem disabled value="" sx={{ display: 'none' }}><em>Select Algorithm</em></MenuItem>
          {ALGORITHMS.map((algo) => (
            <MenuItem key={algo} value={algo} disabled={filters.algorithms.includes(algo)}>{algo}</MenuItem>
          ))}
        </Select>

        {/* --- TextField 1: Name --- */}
        <TextField
          label="Type the name.."
          size="small"
          value={filters.name || ''} 
          onChange={(e) => onFilterChange('name', e.target.value)} 
        />

        {/* --- Radio Buttons --- */}
        <RadioGroup
          size="small"
          row
          value={filters.radioOption}
          onChange={(e) => onFilterChange('radioOption', e.target.value)}
        >
          <FormControlLabel value="start-up" control={<Radio />} label="start-up" />
          <FormControlLabel value="researcher" control={<Radio />} label="researcher" />
        </RadioGroup>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, minWidth: 260 }}>
        <Slider
          value={kValue}
          min={MIN_K}
          max={MAX_K}
          step={1}
          onChange={(_, val) => onFilterChange('neighbor', String(val))}
          valueLabelDisplay="auto"
        />
        <TextField
        label="Limit (k)"
        type="number"
        size="small"
        sx={{ width: 110 }}
        value={filters.neighbor ?? ''}
        onChange={handleNeighborChange}
        inputProps={{ min: MIN_K, max: MAX_K, step: 1 }}
        helperText={`Εύρος: ${MIN_K}–${MAX_K}`}
      />

        </Box>

      </Box>
      {/* Τέλος ομάδας Inputs */}

      {/* --- Run Button (Εκτός του Box για να πάει άκρη δεξιά ή να μείνει ξεχωριστά) --- */}
      <Button 
        variant="contained" 
        color="primary" 
        onClick={onSubmit}
        sx={{ height: 'fit-content', px: 4 }} // Λίγο πιο φαρδύ κουμπί
      >
        Run
      </Button>

    </Paper>
  );
};

export default DashboardHeader;