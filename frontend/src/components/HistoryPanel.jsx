import React from 'react';

export default function HistoryPanel({ conversations = [], onSelectConversation }) {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <h2 className="text-2xl font-semibold mb-4">History</h2>
      {conversations.length === 0 ? (
        <div className="text-sm text-gray-600">No history yet. Start a new chat to begin.</div>
      ) : (
        <ul className="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
          {conversations.map((conv) => (
            <li key={conv.id}>
              <button
                type="button"
                onClick={() => onSelectConversation && onSelectConversation(conv.id)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center justify-between"
              >
                <span className="truncate pr-2">{conv.title || 'New Chat'}</span>
                {conv.createdAt && (
                  <span className="text-xs text-gray-500">{new Date(conv.createdAt).toLocaleString()}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
