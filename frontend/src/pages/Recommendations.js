import React from 'react';

const Recommendations = () => {
  return (
    <div className="p-4 md:p-8" data-testid="recommendations">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
        <p className="text-gray-600 mt-1">Manage your recommendations</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100">
        <div className="text-center">
          <p className="text-gray-600 mb-4">This feature is under development</p>
          <p className="text-sm text-gray-500">Complete recommendations management coming soon</p>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
