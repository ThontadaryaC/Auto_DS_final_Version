import React from 'react';
import { Database, Languages, Moon, Sun, LayoutDashboard, LogOut, Bot } from 'lucide-react';
import { AuthService } from '../auth/AuthService';

const Header = ({ theme, toggleTheme, onHistoryOpen, onSidebarToggle }) => {
  return (
    <header className="h-16 flex items-center justify-between px-4 sm:px-6 bg-white dark:bg-dark-panel border-b border-gray-200 dark:border-dark-border shadow-sm">
      <div className="flex items-center gap-2">
        <LayoutDashboard className="text-brand-500 w-8 h-8" />
        <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-brand-600 to-blue-600 bg-clip-text text-transparent">
          AutoDS AI
        </h1>
      </div>
      
      <div className="flex items-center gap-2 sm:gap-4">
        <button 
          onClick={onHistoryOpen}
          className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors tooltip-trigger" 
          title="Dataset Library"
        >
          <Database className="w-5 h-5 text-brand-500" />
        </button>
        <button 
          onClick={toggleTheme}
          className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors focus:ring-2 focus:ring-brand-500"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button 
          onClick={onSidebarToggle}
          className="lg:hidden p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors tooltip-trigger"
          title="AI Chatbot"
        >
          <Bot className="w-5 h-5 text-brand-500" />
        </button>

        <button 
          onClick={() => {
            AuthService.logout();
            window.location.reload();
          }}
          className="flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-xl transition-all border border-red-100 dark:border-red-900/30 group tooltip-trigger"
          title="Logout"
        >
          <LogOut className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-xs font-bold uppercase tracking-wider">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
