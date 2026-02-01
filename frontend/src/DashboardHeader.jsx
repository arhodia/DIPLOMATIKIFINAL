import React from 'react';
import { 
  Box, 
  Paper, 
  Select, 
  MenuItem, 
  OutlinedInput, 
  Chip, 
  TextField, 
  RadioGroup, 
  FormControlLabel, 
  Radio, 
  Slider, 
  Button, 
  Typography 
} from '@mui/material';

// --- Reusable Component για το ζευγάρι Slider + Input ---
const InputSliderGroup = ({ 
  label, 
  fieldKey, 
  val, 
  min, 
  max, 
  step, 
  onGenericChange 
}) => {
  // Υπολογισμός τιμής για το Slider (πρέπει να είναι number)
  const parsed = Number(val);
  const sliderValue = (val === '' || Number.isNaN(parsed)) ? min : parsed;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}> 
      <Slider
        size="small"
        value={sliderValue}
        min={min}
        max={max}
        step={step}
        onChange={(_, newValue) => onGenericChange(fieldKey, String(newValue), min, max, step)}
        valueLabelDisplay="auto"
        sx={{ width: 60, mr: 0.5 }} // Μικρό πλάτος για να χωρέσουν όλα
      />
      
      <TextField
        label={`${label} (${min}-${max})`}
        type="number"
        size="small"
        sx={{ width: 110 }} 
        value={val}
        onChange={(e) => onGenericChange(fieldKey, e.target.value, min, max, step)}
        InputProps={{ inputProps: { min, max, step } }}
      />
    </Box>
  );
};

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

  const ALGORITHMS = ["LSH_BRP", "LSH_MinHash", "KMeans", "BisectingKMeans"];
  const FILE_SIZES = ["5000", "20000", "50000"];
  // --- Configuration για όλα τα Slider Inputs ---
  // Εδώ ορίζεις τα όρια (min, max, step) για το κάθε πεδίο
  const SLIDER_FIELDS = [
    { key: 'neighbor',    label: 'Limit',    min: 3,   max: 80,   step: 1 },
    { key: 'k_min',       label: 'K Min',    min: 1,   max: 50,   step: 1 },
    { key: 'k_max',       label: 'K Max',    min: 1,   max: 50,   step: 1 },
    { key: 'seed',        label: 'Seed',     min: 0,   max: 100,  step: 1 },
    { key: 'maxIter',     label: 'Max Iter', min: 10,  max: 500,  step: 10 },
    { key: 'sample_frac', label: 'Sample',   min: 0.1, max: 1.0,  step: 0.1 },
  ];

  const handleDeleteAlgorithm = (algoToDelete) => {
    const newSelection = filters.algorithms.filter((algo) => algo !== algoToDelete);
    onFilterChange('algorithms', newSelection);
  };

  // --- Generic Handler για όλα τα numeric inputs ---
  const handleGenericChange = (key, value, min, max, step) => {
    if (value === '') {
      onFilterChange(key, '');
      return;
    }

    // Έλεγχος: Αν το step είναι δεκαδικό (π.χ. sample_frac), επιτρέπουμε '.'
    // Αν το step είναι ακέραιο, επιτρέπουμε μόνο ψηφία.
    const isFloat = step % 1 !== 0; 
    
    // Regex: Αν είναι float επιτρέπει αριθμούς και τελείες, αλλιώς μόνο ψηφία
    const isValidFormat = isFloat ? /^[0-9]*\.?[0-9]*$/.test(value) : /^\d+$/.test(value);

    if (!isValidFormat) return;

    // Έλεγχος ορίων (parse number)
    const n = Number(value);
    
    // Αν ο χρήστης πληκτρολογεί "0." ή σκέτο ".", το αφήνουμε να περάσει προσωρινά
    if (value === '.' || (value.endsWith('.') && isFloat)) {
       onFilterChange(key, value);
       return;
    }

    // Αυστηρός έλεγχος ορίων (αν θέλεις να μπλοκάρεις τιμές εκτός ορίων live)
    if (n > max) return; // Μπορείς να το αφήσεις ή να το βγάλεις αν θες να επιτρέπεις typing

    onFilterChange(key, value);
  };

  return (
    <Paper elevation={3} sx={{ p: 2, mx: 2, my: 2, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>

      {/* --- Ομάδα Input Fields (Όλα μαζί σε ένα Flex container) --- */}
      <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          alignItems: 'center', 
          flexWrap: 'wrap', // Σημαντικό: Τα πεδία θα πάνε από κάτω αν δεν χωράνε
          flex: 1 
      }}>

        {/* 1. Industry Select */}
        <Select
          size="small"
          value={filters.industry}
          onChange={(e) => onFilterChange('industry', e.target.value)}
          displayEmpty
          MenuProps={{ PaperProps: { sx: { maxHeight: 300 } } }}
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="" sx={{ display: 'none' }}><em>Category</em></MenuItem>
          {STATIC_OPTIONS.map((option) => (
            <MenuItem key={option} value={option}>{option}</MenuItem>
          ))}
        </Select>

        {/* 2. Algorithms Select */}
        <Select
          size="small"
          multiple
          value={filters.algorithms}
          onChange={(e) => onFilterChange('algorithms', e.target.value)}
          displayEmpty
          sx={{ minWidth: 180, maxWidth: 250 }}
          input={<OutlinedInput />}
          renderValue={(selected) => {
            if (selected.length === 0) return <em>Algorithm</em>;
            return (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip size="small" key={value} label={value} onDelete={() => handleDeleteAlgorithm(value)} onMouseDown={(e) => e.stopPropagation()} />
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

        {/* 3. Name Input */}
        <TextField
          label="Name.."
          size="small"
          value={filters.name || ''} 
          onChange={(e) => onFilterChange('name', e.target.value)} 
          sx={{ width: 130 }}
        />

        {/* 4. Radio Buttons */}
        <RadioGroup
          size="small"
          row
          value={filters.radioOption}
          onChange={(e) => onFilterChange('radioOption', e.target.value)}
          sx={{ flexWrap: 'nowrap' }}
        >
          <FormControlLabel value="start-up" control={<Radio size="small" />} label={<Typography variant="body2" sx={{fontSize:'0.8rem'}}>start-up</Typography>} />
          <FormControlLabel value="researcher" control={<Radio size="small" />} label={<Typography variant="body2" sx={{fontSize:'0.8rem'}}>researcher</Typography>} />
        </RadioGroup>

        {/* 5. Δυναμική δημιουργία όλων των Slider Inputs */}
        {SLIDER_FIELDS.map((field) => (
          <InputSliderGroup
            key={field.key}
            label={field.label}
            fieldKey={field.key}
            val={filters[field.key] ?? ''} // Default σε empty string αν είναι undefined
            min={field.min}
            max={field.max}
            step={field.step}
            onGenericChange={handleGenericChange}
          />
        ))}

        {/* 6. File Size Select - Το νέο πεδίο */}
        <Select
        size="small"
        value={filters.file_size || ""} // Changed from fileSize
        onChange={(e) => onFilterChange('file_size', e.target.value)} // Changed from fileSize
        displayEmpty
        sx={{ minWidth: 120 }}
      >
        <MenuItem value="" sx={{ display: 'none' }}>
          <em>File Size</em>
        </MenuItem>
        {FILE_SIZES.map((size) => (
          <MenuItem key={size} value={size}>
            {size}
          </MenuItem>
        ))}
      </Select>



      </Box>

      {/* --- Run Button --- */}
      <Button 
        variant="contained" 
        color="primary" 
        onClick={onSubmit}
        sx={{ height: 40, px: 3, whiteSpace: 'nowrap' }} 
      >
        Run
      </Button>

    </Paper>
  );
};

export default DashboardHeader;