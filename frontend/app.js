const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL || 'http://localhost:8000';
const PORT = process.env.FRONTEND_PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.get('/health', async (req, res) => {
  try {
    await axios.get(`${API_URL}/health`);
    res.json({ status: 'healthy', api: 'connected' });
  } catch (err) {
    res.status(503).json({ status: 'unhealthy', api: 'disconnected', error: err.message });
  }
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    console.error('Error submitting job:', err.message);
    res.status(500).json({ error: "Failed to submit job", details: err.message });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    console.error('Error getting job status:', err.message);
    res.status(500).json({ error: "Failed to get job status", details: err.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend running on port ${PORT}`);
  console.log(`API URL: ${API_URL}`);
});
