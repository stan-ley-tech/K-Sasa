import React from 'react';

export default function ECitizenPanel() {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <h2 className="text-2xl font-semibold mb-4">E-Citizen Integration</h2>
      <p className="text-sm text-gray-600 mb-4">
        This is the integration area for Kenya eCitizen services. You can continue to their
        portal to authenticate and access services.
      </p>
      <a
        href="https://www.ecitizen.go.ke"
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
      >
        Open eCitizen Portal
      </a>
    </div>
  );
}
