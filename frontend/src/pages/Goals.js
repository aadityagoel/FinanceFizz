import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-hot-toast';

const Goals = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const endpoint = 'goals'.replace('emergencyvault', 'emergency');
      const response = await api.get(`/${endpoint}`);
      setData(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-8" data-testid="goals">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Goals</h1>
        <p className="text-gray-600 mt-1">Manage your goals</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100">
          <p className="text-gray-600 text-center">
            {data.length === 0 ? 'No data available' : `${data.length} items found`}
          </p>
          <p className="text-sm text-gray-500 text-center mt-2">Full UI coming soon</p>
        </div>
      )}
    </div>
  );
};

export default Goals;
