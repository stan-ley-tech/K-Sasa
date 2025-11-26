import React, { useState, useEffect } from 'react';
import { FiSettings, FiMoon, FiSun, FiMenu, FiX } from 'react-icons/fi';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import ChatSidebar from './components/ChatSidebar';
import FormsPanel from './components/FormsPanel';
import ECitizenPanel from './components/ECitizenPanel';
import { agentAsk } from './utils/api';
import { detectLanguage, normalizeLanguageForReply, mapShengToReplyCode, routeDomain } from './utils/lang';

// Generate a random user ID if not exists
const getUserId = () => {
  let userId = localStorage.getItem('ksasa_user_id');
  if (!userId) {
    userId = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('ksasa_user_id', userId);
  }
  return userId;
};

export default function App() {
  const [domain, setDomain] = useState('education');
  const domains = [
    { id: 'education', name: 'Education' },
    { id: 'governance', name: 'Governance' },
    { id: 'health', name: 'Health' }
  ];
  const [messages, setMessages] = useState([]);
  const [messagesByConversation, setMessagesByConversation] = useState({});
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [activeView, setActiveView] = useState('chat'); // chat | forms | ecitizen
  const userId = getUserId();

  // Toggle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Load conversations from localStorage
  useEffect(() => {
    const savedConversations = localStorage.getItem('ksasa_conversations');
    if (savedConversations) {
      const parsed = JSON.parse(savedConversations);
      setConversations(parsed);
      if (parsed.length > 0 && !currentConversation) {
        setCurrentConversation(parsed[0].id);
      }
    }
  }, []);

  useEffect(() => {
    const savedMessagesMap = localStorage.getItem('ksasa_messages_by_conversation');
    if (savedMessagesMap) {
      try {
        const parsed = JSON.parse(savedMessagesMap);
        setMessagesByConversation(parsed);
        if (parsed[currentConversation]) {
          setMessages(parsed[currentConversation]);
        }
      } catch (e) {
        console.error('Failed to parse saved messages', e);
      }
    }
  }, []);

  // Save conversations to localStorage when they change
  useEffect(() => {
    localStorage.setItem('ksasa_conversations', JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    setMessagesByConversation((prev) => {
      const updated = { ...prev, [currentConversation]: messages };
      localStorage.setItem('ksasa_messages_by_conversation', JSON.stringify(updated));
      return updated;
    });
  }, [messages, currentConversation]);

  const onSend = async (text) => {
    if (!text.trim()) return;
    
    const userMessage = { role: 'user', text };
    const updatedMessages = [...messages, userMessage];

    // Ensure there is an active conversation; if not, create one now
    if (!currentConversation) {
      const newId = Date.now().toString();
      const newConversation = {
        id: newId,
        title: 'New Chat',
        createdAt: new Date().toISOString(),
      };
      setConversations((prev) => [newConversation, ...prev]);
      setCurrentConversation(newId);
    }

    setMessages(updatedMessages);

    // Update conversation metadata (latest snippet + timestamp)
    setConversations(prev =>
      prev.map(conv =>
        conv.id === currentConversation
          ? {
              ...conv,
              updatedAt: new Date().toISOString(),
              lastSnippet: text.length > 60 ? text.substring(0, 60) + '...' : text
            }
          : conv
      )
    );
    setLoading(true);
    
    try {
      // Auto language detect and domain route
      const detected = detectLanguage(text);
      const replyLangCode = mapShengToReplyCode(detected);
      const routedDomain = routeDomain(text);
      setDomain(routedDomain);

      // Define context based on routed domain
      let context = { language: replyLangCode };
      if (routedDomain === 'education') {
        let subject = 'Math';
        if (replyLangCode === 'sw') subject = 'Hisabati';
        else if (replyLangCode === 'luo') subject = 'Kisomo';
        else if (replyLangCode === 'kik') subject = 'Mathi';
        
        context = {
          ...context,
          grade: 4,
          subject,
          duration_minutes: 30
        };
      } else if (routedDomain === 'health') {
        context = {
          ...context,
          category: 'general',
          urgency: 'normal'
        };
      } else if (routedDomain === 'governance') {
        context = {
          ...context,
          department: 'general'
        };
      }
      
      const data = await agentAsk({ 
        user_id: userId, 
        channel: 'web', 
        domain: routedDomain, 
        prompt: text, 
        context 
      });
      
      // Wrap reply in required output structure
      const domainAcr = routedDomain === 'education' ? 'EDU' : routedDomain === 'health' ? 'HLT' : 'GOV';
      const langLabel = normalizeLanguageForReply(replyLangCode);
      const formatted = data.reply;

      const botMessage = { 
        role: 'assistant', 
        text: formatted, 
        citations: data.citations, 
        confidence: data.confidence, 
        audit_id: data.audit_id 
      };
      
      setMessages(prev => {
        const nextMessages = [...prev, botMessage];

        // Update conversation metadata based on bot reply as well
        const lastText = formatted || text;
        setConversations(prevConvs =>
          prevConvs.map(conv =>
            conv.id === currentConversation
              ? {
                  ...conv,
                  updatedAt: new Date().toISOString(),
                  lastSnippet:
                    lastText.length > 60 ? lastText.substring(0, 60) + '...' : lastText
                }
              : conv
          )
        );

        return nextMessages;
      });
      
      // Update conversation title if it's the first message
      if (messages.length === 0) {
        const title = text.length > 30 ? text.substring(0, 30) + '...' : text;
        updateConversationTitle(currentConversation, title);
      }
      
    } catch (e) {
      console.error('Error sending message:', e);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `Error: ${e?.message || 'Failed to get response'}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const startNewChat = () => {
    const newId = Date.now().toString();
    const newConversation = { 
      id: newId, 
      title: 'New Chat',
      createdAt: new Date().toISOString()
    };
    
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversation(newId);
    setMessages([]);
    setActiveView('chat');
  };

  const selectConversation = (conversationId) => {
    setCurrentConversation(conversationId);
    const history = messagesByConversation[conversationId] || [];
    setMessages(history); // Load messages for this conversation
    setActiveView('chat'); // Always return to chat view when picking from history
    setSidebarOpen(false); // Close sidebar on mobile
  };

  const updateConversationTitle = (conversationId, title) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === conversationId ? { ...conv, title } : conv
      )
    );
  };

  const currentConversationData = conversations.find(c => c.id === currentConversation) || {};

  const [isInputFocused, setIsInputFocused] = useState(false);

  // Sidebar action handlers (History is inline in sidebar)
  const handleOpenForms = () => {
    setActiveView('forms');
    setSidebarOpen(false);
  };
  const handleOpenECitizen = () => {
    setActiveView('ecitizen');
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Mobile sidebar toggle */}
      <button 
        className="md:hidden fixed top-4 left-4 z-20 p-2 rounded-md bg-white dark:bg-gray-800 shadow-md"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <FiX /> : <FiMenu />}
      </button>

      {/* Sidebar */}
      <div className={`
        fixed md:static z-10 h-full w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <ChatSidebar
          conversations={conversations}
          onSelectConversation={selectConversation}
          onNewChat={startNewChat}
          onOpenForms={handleOpenForms}
          onOpenECitizen={handleOpenECitizen}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header - Only show when there are messages */}
        {messages.length > 0 && (
          <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center max-w-7xl mx-auto">
              <h1 className="text-xl font-bold text-blue-600 dark:text-blue-400">K-Sasa</h1>
            </div>
          </header>
        )}

      {/* Main content area */}
      <div className="flex-1 overflow-auto flex flex-col p-4">
        {activeView === 'chat' && (
          <div
            className={`flex-1 flex flex-col ${
              messages.length === 0 ? 'items-center justify-center' : ''
            }`}
          >
            {messages.length === 0 ? (
              <div className="text-center max-w-2xl w-full px-4">
                {/* K-Sasa Logo */}
                <div className="mb-8 flex justify-center">
                  <div className="w-24 h-24 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <span className="text-3xl font-bold text-blue-600 dark:text-blue-300">KS</span>
                  </div>
                </div>
                
                <h1 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">How can I help you today?</h1>
              </div>
            ) : (
              <ChatWindow 
                messages={messages} 
                loading={loading} 
              />
            )}
          </div>
        )}
        {activeView === 'forms' && (
          <FormsPanel />
        )}
        {activeView === 'ecitizen' && (
          <ECitizenPanel />
        )}
      </div>
        
        {/* Chat input - only when in chat view */}
      {activeView === 'chat' && (
        <div className={`border-t border-gray-200 dark:border-gray-700 transition-all duration-200 ${
          isInputFocused ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'
        }`}>
          <div className="max-w-3xl mx-auto px-4 py-4">
            <ChatInput 
              onSend={onSend} 
              loading={loading}
              onFocusChange={setIsInputFocused}
              compact={messages.length === 0}
            />
          </div>
        </div>
      )}
        
        {/* Domain tip */}
        {domain === 'governance' && (
          <div className="bg-blue-50 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs p-2 border-t border-blue-100 dark:border-blue-800">
            <p>Tip: You can include a JSON form in your message context via backend or paste details in your prompt. Required: business_name, owner_name, id_number, business_type, address, contact, docs_required.</p>
          </div>
        )}
      </div>
    </div>
  );
}
