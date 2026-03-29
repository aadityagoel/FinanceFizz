import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-hot-toast';
import { Lightbulb, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';

const Recommendations = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/recommendations');
      setData(response.data);
    } catch (error) {
      toast.error('Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityIcon = (priority) => {
    switch(priority) {
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'medium':
        return <Lightbulb className="w-5 h-5 text-yellow-600" />;
      default:
        return <CheckCircle className="w-5 h-5 text-green-600" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-green-500 bg-green-50';
    }
  };

  return (
    <div className="p-4 md:p-8" data-testid="recommendations">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Smart Recommendations</h1>
        <p className="text-gray-600 mt-1">Personalized financial advice based on your data</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* AI Status Banner */}
          {data?.ai_enabled && (
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 mb-8 text-white">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-8 h-8" />
                <div>
                  <h3 className="text-lg font-semibold">AI-Powered Insights Active</h3>
                  <p className="text-purple-100 text-sm">Using {data.ai_provider} for enhanced recommendations</p>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations List */}
          {data?.recommendations && data.recommendations.length > 0 ? (
            <div className="space-y-4">
              {data.recommendations.map((rec, index) => (
                <div 
                  key={index} 
                  className={`border-l-4 rounded-lg p-6 shadow-sm ${getPriorityColor(rec.priority)}`}
                >
                  <div className="flex items-start gap-4">
                    <div className="mt-1">
                      {getPriorityIcon(rec.priority)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{rec.title}</h3>
                        <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                          rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                          rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {rec.priority.toUpperCase()} PRIORITY
                        </span>
                      </div>
                      <p className="text-gray-700 mb-3">{rec.description}</p>
                      <div className="bg-white rounded-lg p-4 mb-3 border border-gray-200">
                        <p className="text-sm font-medium text-gray-900 mb-1">💡 Recommended Action:</p>
                        <p className="text-sm text-gray-700">{rec.action}</p>
                      </div>
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-sm font-medium text-gray-900 mb-1">📈 Impact:</p>
                        <p className="text-sm text-gray-700">{rec.impact}</p>
                      </div>
                      {rec.category && (
                        <div className="mt-3">
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                            Category: {rec.category}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-100">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Looking Good!</h3>
              <p className="text-gray-600">
                No critical recommendations at the moment. Keep up the good financial habits!
              </p>
            </div>
          )}

          {/* Summary */}
          <div className="mt-8 bg-gradient-to-r from-primary-50 to-primary-100 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommendation Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">Total Recommendations</p>
                <p className="text-2xl font-bold text-gray-900">{data?.total_count || 0}</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-red-600">
                  {data?.recommendations?.filter(r => r.priority === 'high').length || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600">AI Enabled</p>
                <p className="text-2xl font-bold text-purple-600">{data?.ai_enabled ? 'Yes' : 'No'}</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Recommendations;
