import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-hot-toast';
import { Wallet, TrendingUp, AlertCircle, Shield, Target, Award } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [netWorth, portfolio, healthScore, recommendations] = await Promise.all([
        api.get('/analytics/net-worth'),
        api.get('/analytics/portfolio-allocation'),
        api.get('/analytics/financial-health-score'),
        api.get('/recommendations')
      ]);

      setAnalytics({
        netWorth: netWorth.data,
        portfolio: portfolio.data,
        healthScore: healthScore.data,
        recommendations: recommendations.data.recommendations.slice(0, 3)
      });
    } catch (error) {
      toast.error('Failed to load analytics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="p-4 md:p-8" data-testid="dashboard">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Your financial overview</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Net Worth</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ₹{analytics?.netWorth?.net_worth?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-primary-50 rounded-lg">
              <Wallet className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Assets</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                ₹{analytics?.netWorth?.total_assets?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Liabilities</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                ₹{analytics?.netWorth?.total_liabilities?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Health Score</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {analytics?.healthScore?.total_score?.toFixed(0) || 0}/100
              </p>
              <p className="text-xs text-gray-500 mt-1">{analytics?.healthScore?.rating}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Award className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Portfolio Allocation */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Allocation</h2>
          {analytics?.portfolio?.breakdown && analytics.portfolio.breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={analytics.portfolio.breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percentage }) => `${type}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="percentage"
                >
                  {analytics.portfolio.breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No investment data available</p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Recommendations</h2>
          <div className="space-y-4">
            {analytics?.recommendations && analytics.recommendations.length > 0 ? (
              analytics.recommendations.map((rec, index) => (
                <div key={index} className="border-l-4 border-primary-500 pl-4 py-2">
                  <h3 className="font-medium text-gray-900">{rec.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                  <span className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded ${
                    rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                    rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {rec.priority} priority
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No recommendations available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
