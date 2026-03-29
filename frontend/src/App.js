import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import useAuthStore from './store/authStore';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Investments from './pages/Investments';
import Expenses from './pages/Expenses';
import Loans from './pages/Loans';
import Insurance from './pages/Insurance';
import Documents from './pages/Documents';
import Goals from './pages/Goals';
import EmergencyVault from './pages/EmergencyVault';
import Recommendations from './pages/Recommendations';

// Components
import Layout from './components/Layout';
import Loading from './components/Loading';

function App() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />}
        />
        <Route
          path="/register"
          element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />}
        />

        {/* Protected Routes */}
        <Route
          path="/"
          element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
        >
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="accounts" element={<Accounts />} />
          <Route path="investments" element={<Investments />} />
          <Route path="expenses" element={<Expenses />} />
          <Route path="loans" element={<Loans />} />
          <Route path="insurance" element={<Insurance />} />
          <Route path="documents" element={<Documents />} />
          <Route path="goals" element={<Goals />} />
          <Route path="emergency-vault" element={<EmergencyVault />} />
          <Route path="recommendations" element={<Recommendations />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
