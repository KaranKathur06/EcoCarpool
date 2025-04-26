import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress
} from '@mui/material';
import {
  PeopleAlt,
  DirectionsCar,
  AttachMoney,
  Receipt,
  Person,
  Timeline
} from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Stat Card Component
const StatCard = ({ title, value, icon, color }) => (
  <Card sx={{ height: '100%', backgroundColor: color, color: 'white' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          <Typography variant="h4">
            {value}
          </Typography>
        </Box>
        {icon}
      </Box>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalRides: 0,
    totalEarnings: 0,
    totalExpenses: 0,
    yourEarnings: 0,
    totalPassengers: 0,
    monthlyEarnings: [],
    weeklyRides: []
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost/api/dashboard_stats.php');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const earningsChartData = {
    labels: stats.monthlyEarnings.map(item => item.month),
    datasets: [{
      label: 'Monthly Earnings',
      data: stats.monthlyEarnings.map(item => item.amount),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  const ridesChartData = {
    labels: stats.weeklyRides.map(item => item.day),
    datasets: [{
      label: 'Weekly Rides',
      data: stats.weeklyRides.map(item => item.count),
      backgroundColor: 'rgba(53, 162, 235, 0.5)'
    }]
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Users"
            value={stats.totalUsers.toLocaleString()}
            icon={<PeopleAlt sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Rides"
            value={stats.totalRides.toLocaleString()}
            icon={<DirectionsCar sx={{ fontSize: 40 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Earnings"
            value={`$${stats.totalEarnings.toLocaleString()}`}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Expenses"
            value={`$${stats.totalExpenses.toLocaleString()}`}
            icon={<Receipt sx={{ fontSize: 40 }} />}
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Your Earnings"
            value={`$${stats.yourEarnings.toLocaleString()}`}
            icon={<Person sx={{ fontSize: 40 }} />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Passengers"
            value={stats.totalPassengers.toLocaleString()}
            icon={<Timeline sx={{ fontSize: 40 }} />}
            color="#0288d1"
          />
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Earnings Overview
              </Typography>
              <Line data={earningsChartData} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Rides Overview
              </Typography>
              <Bar data={ridesChartData} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 