import React from 'react';
import { Box, Typography, Paper, Divider } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ChartSection = ({ allAlgorithmsData }) => {
  // Αν δεν υπάρχουν δεδομένα, μην δείξεις τίποτα
  if (!allAlgorithmsData || Object.keys(allAlgorithmsData).length === 0) {
    return null;
  }

  const algorithmsList = Object.entries(allAlgorithmsData);

  // Helper function: Μετράει πόσοι ερευνητές είναι σε κάθε cluster
  const prepareChartData = (results) => {
    const clusterCounts = {};
    
    results.forEach(item => {
      const cluster = `Cluster ${item.prediction}`;
      clusterCounts[cluster] = (clusterCounts[cluster] || 0) + 1;
    });

    // Μετατροπή σε format που θέλει η Recharts: [{ name: 'Cluster 0', count: 10 }, ...]
    return Object.keys(clusterCounts).map(key => ({
      name: key,
      count: clusterCounts[key]
    })).sort((a, b) => a.name.localeCompare(b.name));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Typography variant="h5" sx={{ textAlign: 'center', mb: 2 }}>
        Οπτικοποίηση Clusters
      </Typography>

      {algorithmsList.map(([algoName, algoContent]) => {
        const dataForChart = prepareChartData(algoContent.results || []);

        return (
          <Paper key={algoName} sx={{ p: 2, borderRadius: 2, boxShadow: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#90caf9' }}>
              Κατανομή: {algoName}
            </Typography>
            
            <Box sx={{ height: 300, width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dataForChart}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="name" stroke="#fff" />
                  <YAxis stroke="#fff" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#333', border: 'none' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Bar dataKey="count" name="Αριθμός Ερευνητών" fill="#82ca9d" barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        );
      })}
    </Box>
  );
};

export default ChartSection;