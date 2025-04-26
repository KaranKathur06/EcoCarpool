import React, { useEffect, useState } from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box,
  Container,
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

const StatCard = ({ title, value, icon, color }) => (
  <Paper
    sx={{
      p: 3,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      bgcolor: color,
      color: 'white',
    }}
  >
    <Box>
      <Typography variant="h6" component="div">
        {title}
      </Typography>
      <Typography variant="h4" component="div">
        {value}
      </Typography>
    </Box>
    {icon}
  </Paper>
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    stats: {
      total_users: 0,
      total_rides: 0,
      total_earnings: 0,
      total_expenses: 0,
      total_passengers: 0
    },
    charts: {
      monthly_earnings: [],
      weekly_rides: []
    }
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost/api/dashboard_stats.php');
      const data = await response.json();
      setDashboardData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const lineChartData = {
    labels: dashboardData.charts.monthly_earnings.map(item => {
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return monthNames[item.month - 1];
    }),
    datasets: [
      {
        label: 'Monthly Earnings',
        data: dashboardData.charts.monthly_earnings.map(item => item.earnings),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const barChartData = {
    labels: dashboardData.charts.weekly_rides.map(item => item.day),
    datasets: [
      {
        label: 'Rides per Day',
        data: dashboardData.charts.weekly_rides.map(item => item.ride_count),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Users"
            value={dashboardData.stats.total_users.toLocaleString()}
            icon={<PeopleAlt sx={{ fontSize: 40 }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Rides"
            value={dashboardData.stats.total_rides.toLocaleString()}
            icon={<DirectionsCar sx={{ fontSize: 40 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Earnings"
            value={`$${dashboardData.stats.total_earnings.toLocaleString()}`}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Expenses"
            value={`$${dashboardData.stats.total_expenses.toLocaleString()}`}
            icon={<Receipt sx={{ fontSize: 40 }} />}
            color="#9c27b0"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Net Earnings"
            value={`$${(dashboardData.stats.total_earnings - dashboardData.stats.total_expenses).toLocaleString()}`}
            icon={<Person sx={{ fontSize: 40 }} />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Passengers"
            value={dashboardData.stats.total_passengers.toLocaleString()}
            icon={<Timeline sx={{ fontSize: 40 }} />}
            color="#0288d1"
          />
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Monthly Earnings Overview
            </Typography>
            <Line data={lineChartData} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Weekly Rides Overview
            </Typography>
            <Bar data={barChartData} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 