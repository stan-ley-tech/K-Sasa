import React, { useState } from 'react';
import { FiPlus, FiGlobe, FiFileText, FiClock } from 'react-icons/fi';

const ChatSidebar = ({ conversations = [], onSelectConversation, onNewChat, onOpenECitizen, onOpenForms }) => {
  const [historyOpen, setHistoryOpen] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className={`sidebar ${collapsed ? 'w-16' : 'w-64'}`}>
      {/* Logo + collapse toggle */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-sm font-bold text-blue-600">KS</span>
          </div>
          {!collapsed && (
            <span className="font-semibold text-gray-800">K-Sasa</span>
          )}
        </div>
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="ml-2 text-xs text-gray-500 hover:text-gray-700"
        >
          {collapsed ? '›' : '‹'}
        </button>
      </div>

      {/* Primary actions */}
      <div className="p-4 border-b border-gray-200 space-y-2">
        <button
          onClick={onNewChat}
          className={`w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md font-medium flex items-center ${
            collapsed ? 'justify-center' : 'justify-center space-x-2'
          } transition-colors`}
          type="button"
        >
          <FiPlus className="h-4 w-4" />
          {!collapsed && <span>New Chat</span>}
        </button>

        <nav className="space-y-1">
          <button
            onClick={onOpenECitizen}
            className={`w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 text-gray-700 flex items-center ${
              collapsed ? 'justify-center' : 'space-x-2'
            }`}
            type="button"
          >
            <FiGlobe className="h-4 w-4 text-gray-500" />
            {!collapsed && <span>E-Citizen</span>}
          </button>
          <button
            onClick={onOpenForms}
            className={`w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 text-gray-700 flex items-center ${
              collapsed ? 'justify-center' : 'space-x-2'
            }`}
            type="button"
          >
            <FiFileText className="h-4 w-4 text-gray-500" />
            {!collapsed && <span>Forms</span>}
          </button>
          <button
            onClick={() => setHistoryOpen((v) => !v)}
            className={`w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 text-gray-700 flex items-center ${
              collapsed ? 'justify-center' : 'space-x-2'
            }`}
            type="button"
          >
            <FiClock className="h-4 w-4 text-gray-500" />
            {!collapsed && <span>History</span>}
          </button>
          {!collapsed && historyOpen && (
            <div className="mt-1 space-y-1 pl-2 border-l border-gray-200">
              {conversations.length === 0 ? (
                <div className="px-3 py-2 text-xs text-gray-500">No history yet</div>
              ) : (
                conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => onSelectConversation && onSelectConversation(conv.id)}
                    className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 text-gray-700"
                    type="button"
                  >
                    <div className="flex flex-col items-start space-y-0.5">
                      <div className="flex w-full items-center justify-between space-x-2">
                        <span className="truncate block font-medium">
                          {conv.title || 'New Chat'}
                        </span>
                        {conv.updatedAt && (
                          <span className="text-[10px] text-gray-400 whitespace-nowrap">
                            {new Date(conv.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                      </div>
                      {conv.lastSnippet && (
                        <span className="truncate text-[11px] text-gray-500">
                          {conv.lastSnippet}
                        </span>
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>
          )}
        </nav>
      </div>
    </div>
  );
};

export default ChatSidebar;
