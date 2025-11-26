import React from 'react';
import { FiCopy, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';

const ChatWindow = ({ messages, loading }) => {
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.length === 0 && (
          <div className="text-sm text-gray-500">No messages yet. Ask something to get started.</div>
        )}
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`message-bubble ${
                msg.role === 'user' ? 'user-message' : 'ai-message message-enter'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs font-medium text-gray-500 mb-2">Sources:</div>
                  <div className="space-y-2">
                    {msg.citations.map((cite, i) => (
                      <div 
                        key={i} 
                        className="text-xs text-blue-600 hover:underline cursor-pointer"
                        onClick={() => window.open(cite, '_blank')}
                      >
                        {typeof cite === 'string' ? cite : `${cite.source || 'Source'} - ${cite.snippet || cite}`}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-end mt-2 space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => copyToClipboard(msg.text)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
                  title="Copy to clipboard"
                >
                  <FiCopy className="h-3.5 w-3.5" />
                </button>
                {msg.role === 'assistant' && (
                  <>
                    <button 
                      className="p-1 text-gray-400 hover:text-green-500 rounded-full hover:bg-gray-100"
                      title="Good response"
                    >
                      <FiThumbsUp className="h-3.5 w-3.5" />
                    </button>
                    <button 
                      className="p-1 text-gray-400 hover:text-red-500 rounded-full hover:bg-gray-100"
                      title="Needs improvement"
                    >
                      <FiThumbsDown className="h-3.5 w-3.5" />
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex items-center justify-start">
            <div className="ai-message message-bubble">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWindow;
