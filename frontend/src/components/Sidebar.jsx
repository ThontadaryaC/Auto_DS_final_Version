import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2, X } from 'lucide-react';

const Sidebar = ({ theme, isOpen, onClose }) => {
  const [messages, setMessages] = useState([{ role: 'ai', content: 'Hello! Ask me anything about your uploaded dataset.' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/chat`, { query: userMsg });
      setMessages(prev => [...prev, { role: 'ai', content: response.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error answering that.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`
      fixed inset-y-0 right-0 z-50 w-[85%] sm:w-80 h-full 
      transform transition-transform duration-300 ease-in-out
      ${isOpen ? 'translate-x-0' : 'translate-x-full'}
      lg:relative lg:translate-x-0 lg:w-80 lg:z-auto
      border-l border-gray-200 dark:border-dark-border 
      bg-white dark:bg-dark-panel flex flex-col shadow-2xl lg:shadow-xl
    `}>
      <div className="p-4 border-b border-gray-200 dark:border-dark-border flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-brand-500" />
          <h2 className="font-semibold text-lg text-gray-800 dark:text-gray-100">AI Chatbot</h2>
        </div>
        <button 
          onClick={onClose}
          className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-2 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className="shrink-0 mt-1">
                {msg.role === 'ai' ? (
                  <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center">
                    <Bot className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                    <User className="w-5 h-5" />
                  </div>
                )}
              </div>
              <div className={`p-3 rounded-2xl ${
                msg.role === 'user' 
                  ? 'bg-brand-500 text-white rounded-tr-sm' 
                  : 'bg-gray-100 dark:bg-gray-800 dark:text-gray-200 text-gray-800 rounded-tl-sm'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{typeof msg.content === 'object' ? JSON.stringify(msg.content) : msg.content}</p>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center mr-2">
                  <Bot className="w-5 h-5" />
              </div>
            <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm flex items-center text-gray-500">
               <Loader2 className="w-4 h-4 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-dark-border">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your data..."
            className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-full py-3 pl-4 pr-12 focus:ring-2 focus:ring-brand-500 text-sm dark:text-gray-100 transition-shadow"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="absolute right-2 top-1.5 p-1.5 rounded-full bg-brand-500 text-white hover:bg-brand-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Sidebar;
