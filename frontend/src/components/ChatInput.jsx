import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiPaperclip, FiMic } from 'react-icons/fi';

export default function ChatInput({ onSend, loading, onFocusChange, compact = false }) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleFocus = () => {
    onFocusChange?.(true);
  };

  const handleBlur = () => {
    onFocusChange?.(false);
  };

  return (
    <div className={`transition-all duration-200 ${compact ? 'w-full' : 'w-full'}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className={`relative transition-all duration-200 ${
          compact ? 'max-w-2xl mx-auto' : 'w-full'
        }`}>
          <div className={`relative flex items-center ${
            compact 
              ? 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-full px-4 py-2 shadow-sm' 
              : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl p-2 shadow-sm'
          }`}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={handleFocus}
              onBlur={handleBlur}
              placeholder={compact ? "Message K-Sasa..." : "Message K-Sasa..."}
              className={`w-full bg-transparent outline-none ${
                compact ? 'px-2 py-1' : 'min-h-[40px] max-h-[200px] py-2 px-3'
              }`}
              disabled={loading}
            />
            
            {!compact && (
              <div className="flex items-center space-x-1 pr-1">
                <button
                  type="button"
                  className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Attach file"
                >
                  <FiPaperclip className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Voice input"
                >
                  <FiMic className="h-4 w-4" />
                </button>
              </div>
            )}
            
            <button
              type="submit"
              disabled={!message.trim() || loading}
              className={`ml-2 p-2 text-white ${
                message.trim() 
                  ? 'bg-blue-500 hover:bg-blue-600' 
                  : 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
              } rounded-full transition-colors`}
              title="Send message"
            >
              <FiSend className="h-4 w-4" />
            </button>
          </div>
        </div>
      </form>
      
      {!compact && (
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center px-2">
          K-Sasa may produce inaccurate information. Consider verifying important details.
        </div>
      )}
    </div>
  );
}
