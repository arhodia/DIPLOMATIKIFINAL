import { ScatterChart } from '@mui/x-charts/ScatterChart';
import { Box } from '@mui/material';

export default function ScatterSection({ allAlgorithmsData, algorithmType }) {
  // 1. Δυναμική επιλογή του array
  const dataArray = allAlgorithmsData?.["Classification_Results"]?.scatter_plot?.[algorithmType];

  // 2. Έλεγχος εγκυρότητας
  if (!dataArray || !Array.isArray(dataArray)) {
    return <div>Δεν υπάρχουν διαθέσιμα δεδομένα για το γράφημα ({algorithmType}).</div>;
  }

  return (
    /* Χρησιμοποιούμε ένα Box με πλάτος 100% για να ορίσουμε τα όρια */
    <Box sx={{ width: '100%', textAlign: 'center' }}>
      <h4>{algorithmType} Visualization</h4>
      
      <ScatterChart
        // ΑΦΑΙΡΟΥΜΕ το width={500} για να γίνει responsive
        height={350} 
        series={dataArray.map((s, idx) => ({
          label: s.label || `Cluster ${idx}`, 
          data: s.data.map((d, index) => ({ 
              x: d.x, 
              y: d.y, 
              id: `${algorithmType}-${idx}-${index}` 
          })),
        }))}
        grid={{ vertical: true, horizontal: true }}
        
        /* Ρυθμίσεις για να μην ξεχειλίζει το Legend λόγω πολλών Clusters */
        slotProps={{
          legend: {
            direction: 'row',
            position: { vertical: 'top', horizontal: 'middle' },
            padding: 0,
            labelStyle: {
              fontSize: 10, // Μικρότερο font για να χωράνε τα labels
            },
          },
        }}
        // Αυξάνουμε το margin top για να χωρέσει το Legend πάνω από το γράφημα
        margin={{ top: 100, bottom: 50, left: 50, right: 20 }}
      />
    </Box>
  );
}