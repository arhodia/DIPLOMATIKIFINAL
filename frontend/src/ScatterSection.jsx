import { ScatterChart } from '@mui/x-charts/ScatterChart';

export default function ClusterVisual({ allAlgorithmsData }) {
  // 1. Εξαγωγή του array από το αντικείμενο scatter_kmeans
  // Στο screenshot βλέπουμε: scatter_kmeans: { KMeans: Array(26) }
  // 1. Το KMeans είναι ΗΔΗ το array (Array(26))
const dataArray = allAlgorithmsData?.["Classification_Results"]?.scatter_plot?.KMeans;

  // 2. Έλεγχος αν το dataArray υπάρχει και είναι όντως array
  if (!dataArray || !Array.isArray(dataArray)) {
    return <div>Δεν υπάρχουν διαθέσιμα δεδομένα για το γράφημα.</div>;
  }

  return (
    <ScatterChart
      width={600}
      height={400}
      series={dataArray.map((s, idx) => ({
        // Χρήση του index αν δεν υπάρχει s.label στο αντικείμενο
        label: s.label || `Cluster ${idx}`, 
        data: s.data.map((d, index) => ({ 
            x: d.x, 
            y: d.y, 
            id: `${idx}-${index}` // Μοναδικό ID για κάθε σημείο
        })),
      }))}
      grid={{ vertical: true, horizontal: true }}
    />
  );
}