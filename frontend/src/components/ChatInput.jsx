import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiPaperclip, FiMic, FiPlus } from 'react-icons/fi';

export default function ChatInput({ onSend, loading, onFocusChange, compact = false }) {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      const filesMeta = attachments.map((f) => ({
        name: f.name,
        size: f.size,
        type: f.type,
      }));
      onSend(message, filesMeta);
      setMessage('');
      setAttachments([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
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

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    setAttachments(files);
  };

  const handleOpenFilePicker = () => {
    if (!loading && fileInputRef.current) {
      fileInputRef.current.click();
    }
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
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />

            <button
              type="button"
              onClick={handleOpenFilePicker}
              className="mr-2 flex items-center justify-center w-8 h-8 rounded-full border border-gray-300 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              title="Add attachments"
            >
              <FiPlus className="h-4 w-4" />
            </button>

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
