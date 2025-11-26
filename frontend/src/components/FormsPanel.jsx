import React from 'react';

const forms = [
  { name: 'Business Registration (BN2)', url: 'https://business.egov.go.ke/forms' },
  { name: 'KRA PIN Registration', url: 'https://itax.kra.go.ke/KRA-Portal/' },
  { name: 'Passport Application', url: 'https://immigration.ecitizen.go.ke' },
  { name: 'NTSA Services', url: 'https://ntsa.ecitizen.go.ke' },
  { name: 'Huduma Services', url: 'https://www.ecitizen.go.ke' },
];

export default function FormsPanel() {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <h2 className="text-2xl font-semibold mb-4">Government Forms</h2>
      <p className="text-sm text-gray-600 mb-4">Browse and download forms from official portals.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {forms.map((f) => (
          <a
            key={f.name}
            href={f.url}
            target="_blank"
            rel="noreferrer"
            className="block border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
          >
            <div className="font-medium">{f.name}</div>
            <div className="text-xs text-blue-600 truncate">{f.url}</div>
          </a>
        ))}
      </div>
    </div>
  );
}
