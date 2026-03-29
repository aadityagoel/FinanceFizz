import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import { toast } from 'react-hot-toast';
import { Plus, Edit, Trash2, Wallet } from 'lucide-react';

const Accounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [formData, setFormData] = useState({
    institution_name: '',
    account_type: 'bank',
    account_number: '',
    balance: 0,
    notes: ''
  });

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await api.get('/accounts');
      setAccounts(response.data);
    } catch (error) {
      toast.error('Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAccount) {
        await api.put(`/accounts/${editingAccount.account_id}`, {
          institution_name: formData.institution_name,
          balance: parseFloat(formData.balance),
          notes: formData.notes
        });
        toast.success('Account updated successfully');
      } else {
        await api.post('/accounts', {
          ...formData,
          balance: parseFloat(formData.balance)
        });
        toast.success('Account added successfully');
      }
      setShowModal(false);
      setEditingAccount(null);
      resetForm();
      fetchAccounts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return;
    try {
      await api.delete(`/accounts/${accountId}`);
      toast.success('Account deleted successfully');
      fetchAccounts();
    } catch (error) {
      toast.error('Failed to delete account');
    }
  };

  const resetForm = () => {
    setFormData({
      institution_name: '',
      account_type: 'bank',
      account_number: '',
      balance: 0,
      notes: ''
    });
  };

  const openEditModal = (account) => {
    setEditingAccount(account);
    setFormData({
      institution_name: account.institution_name,
      account_type: account.account_type,
      account_number: account.account_number,
      balance: account.balance,
      notes: account.notes || ''
    });
    setShowModal(true);
  };

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);

  return (
    <div className="p-4 md:p-8" data-testid="accounts">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Accounts</h1>
          <p className="text-gray-600 mt-1">Manage your bank and financial accounts</p>
        </div>
        <button
          onClick={() => { setShowModal(true); setEditingAccount(null); resetForm(); }}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-5 h-5" />
          Add Account
        </button>
      </div>

      {/* Summary Card */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl shadow-lg p-6 mb-8 text-white">
        <div className="flex items-center gap-4">
          <Wallet className="w-12 h-12" />
          <div>
            <p className="text-primary-100">Total Balance</p>
            <p className="text-3xl font-bold">₹{totalBalance.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Accounts List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : accounts.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-100">
          <Wallet className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">No accounts added yet</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <div key={account.account_id} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{account.institution_name}</h3>
                    <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded">
                      {account.account_type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">Account: {account.account_number_masked}</p>
                  <p className="text-2xl font-bold text-gray-900">₹{account.balance.toLocaleString()}</p>
                  {account.notes && <p className="text-sm text-gray-600 mt-2">{account.notes}</p>}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => openEditModal(account)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(account.account_id)}
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
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">{editingAccount ? 'Edit Account' : 'Add New Account'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Institution Name</label>
                <input
                  type="text"
                  required
                  value={formData.institution_name}
                  onChange={(e) => setFormData({...formData, institution_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., HDFC Bank"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                <select
                  value={formData.account_type}
                  onChange={(e) => setFormData({...formData, account_type: e.target.value})}
                  disabled={!!editingAccount}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="bank">Bank Account</option>
                  <option value="demat">Demat Account</option>
                  <option value="upi">UPI</option>
                  <option value="credit_card">Credit Card</option>
                </select>
              </div>

              {!editingAccount && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
                  <input
                    type="text"
                    required
                    value={formData.account_number}
                    onChange={(e) => setFormData({...formData, account_number: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="Account number"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Balance (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  value={formData.balance}
                  onChange={(e) => setFormData({...formData, balance: e.target.value})}
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
                  {editingAccount ? 'Update' : 'Add'} Account
                </button>
                <button
                  type="button"
                  onClick={() => { setShowModal(false); setEditingAccount(null); resetForm(); }}
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

export default Accounts;
