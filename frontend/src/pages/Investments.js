import React from 'react';

const Investments = () => {
  return (
    <div className="p-4 md:p-8" data-testid="investments">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Investments</h1>
        <p className="text-gray-600 mt-1">Manage your investments</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100">
        <div className="text-center">
          <p className="text-gray-600 mb-4">This feature is under development</p>
          <p className="text-sm text-gray-500">Complete investments management coming soon</p>
        </div>
      </div>
    </div>
  );
};

export default Investments;
