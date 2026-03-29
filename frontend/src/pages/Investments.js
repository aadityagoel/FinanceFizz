import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-hot-toast';
import { Plus, Edit, Trash2, TrendingUp, TrendingDown } from 'lucide-react';

const Investments = () => {
  const [investments, setInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingInvestment, setEditingInvestment] = useState(null);
  const [formData, setFormData] = useState({
    investment_type: 'mutual_fund',
    name: '',
    platform: '',
    amount_invested: 0,
    current_value: 0,
    investment_date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  useEffect(() => {
    fetchInvestments();
  }, []);

  const fetchInvestments = async () => {
    try {
      const response = await api.get('/investments');
      setInvestments(response.data);
    } catch (error) {
      toast.error('Failed to fetch investments');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        amount_invested: parseFloat(formData.amount_invested),
        current_value: parseFloat(formData.current_value),
        investment_date: new Date(formData.investment_date).toISOString(),
        tags: []
      };

      if (editingInvestment) {
        await api.put(`/investments/${editingInvestment.investment_id}`, {
          current_value: payload.current_value,
          notes: payload.notes
        });
        toast.success('Investment updated successfully');
      } else {
        await api.post('/investments', payload);
        toast.success('Investment added successfully');
      }
      setShowModal(false);
      setEditingInvestment(null);
      resetForm();
      fetchInvestments();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (investmentId) => {
    if (!window.confirm('Are you sure you want to delete this investment?')) return;
    try {
      await api.delete(`/investments/${investmentId}`);
      toast.success('Investment deleted successfully');
      fetchInvestments();
    } catch (error) {
      toast.error('Failed to delete investment');
    }
  };

  const resetForm = () => {
    setFormData({
      investment_type: 'mutual_fund',
      name: '',
      platform: '',
      amount_invested: 0,
      current_value: 0,
      investment_date: new Date().toISOString().split('T')[0],
      notes: ''
    });
  };

  const openEditModal = (investment) => {
    setEditingInvestment(investment);
    setFormData({
      investment_type: investment.investment_type,
      name: investment.name,
      platform: investment.platform,
      amount_invested: investment.amount_invested,
      current_value: investment.current_value,
      investment_date: investment.investment_date.split('T')[0],
      notes: investment.notes || ''
    });
    setShowModal(true);
  };

  const totalInvested = investments.reduce((sum, inv) => sum + inv.amount_invested, 0);
  const totalCurrent = investments.reduce((sum, inv) => sum + inv.current_value, 0);
  const totalGain = totalCurrent - totalInvested;
  const gainPercentage = totalInvested > 0 ? (totalGain / totalInvested * 100) : 0;

  return (
    <div className="p-4 md:p-8" data-testid="investments">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Investments</h1>
          <p className="text-gray-600 mt-1">Track your investment portfolio</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setEditingInvestment(null); resetForm(); }}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-5 h-5" />
          Add Investment
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Total Invested</p>
          <p className="text-2xl font-bold text-gray-900">₹{totalInvested.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Current Value</p>
          <p className="text-2xl font-bold text-gray-900">₹{totalCurrent.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Total Gain/Loss</p>
          <div className="flex items-center gap-2">
            <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ₹{Math.abs(totalGain).toLocaleString()}
            </p>
            {totalGain >= 0 ? <TrendingUp className="w-5 h-5 text-green-600" /> : <TrendingDown className="w-5 h-5 text-red-600" />}
          </div>
          <p className={`text-sm ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {gainPercentage.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Investments List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : investments.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-100">
          <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">No investments added yet</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {investments.map((investment) => (
            <div key={investment.investment_id} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{investment.name}</h3>
                    <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded">
                      {investment.investment_type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-3">Platform: {investment.platform}</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Invested</p>
                      <p className="text-sm font-semibold text-gray-900">₹{investment.amount_invested.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Current</p>
                      <p className="text-sm font-semibold text-gray-900">₹{investment.current_value.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Gain/Loss</p>
                      <p className={`text-sm font-semibold ${investment.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ₹{Math.abs(investment.gain_loss).toLocaleString()} ({investment.gain_loss_percentage.toFixed(2)}%)
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => openEditModal(investment)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(investment.investment_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">{editingInvestment ? 'Edit Investment' : 'Add New Investment'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Investment Type</label>
                <select
                  value={formData.investment_type}
                  onChange={(e) => setFormData({...formData, investment_type: e.target.value})}
                  disabled={!!editingInvestment}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="mutual_fund">Mutual Fund</option>
                  <option value="stock">Stock</option>
                  <option value="p2p">P2P Lending</option>
                  <option value="gold">Gold</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Investment Name</label>
                <input
                  type="text"
                  required
                  disabled={!!editingInvestment}
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., HDFC Mid Cap Fund"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
                <input
                  type="text"
                  required
                  disabled={!!editingInvestment}
                  value={formData.platform}
                  onChange={(e) => setFormData({...formData, platform: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., Groww, Zerodha"
                />
              </div>

              {!editingInvestment && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Amount Invested (₹)</label>
                    <input
                      type="number"
                      required
                      step="0.01"
                      value={formData.amount_invested}
                      onChange={(e) => setFormData({...formData, amount_invested: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Investment Date</label>
                    <input
                      type="date"
                      required
                      value={formData.investment_date}
                      onChange={(e) => setFormData({...formData, investment_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Value (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  value={formData.current_value}
                  onChange={(e) => setFormData({...formData, current_value: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows="2"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg font-semibold hover:bg-primary-700"
                >
                  {editingInvestment ? 'Update' : 'Add'} Investment
                </button>
                <button
                  type="button"
                  onClick={() => { setShowModal(false); setEditingInvestment(null); resetForm(); }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Investments;
