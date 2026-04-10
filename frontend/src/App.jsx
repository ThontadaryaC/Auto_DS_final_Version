import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import OutputArea from './components/OutputArea';
import StandaloneView from './components/StandaloneView';
import InteractiveModal from './components/InteractiveModal';
import HistoryModal from './components/HistoryModal';
import AdvancedAnalysis from './components/AdvancedAnalysis';

function App() {
  const [theme, setTheme] = useState('light');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // History State
  const [history, setHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Interactive Modal State
  const [activePanel, setActivePanel] = useState(null);
  const [interactiveData, setInteractiveData] = useState(null);
  const [panelLoading, setPanelLoading] = useState(false);

  // Mobile Sidebar State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Advanced Analysis State
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);

  // Toggle Dark Mode
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/api/history`);
      setHistory(res.data);
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const clearHistory = async () => {
    if (window.confirm('Are you sure you want to completely clear the file registry history?')) {
      try {
        await axios.delete(`${import.meta.env.VITE_API_URL}/api/history`);
        fetchHistory();
      } catch (err) {
        setError('Failed to clear history: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleOpenPanel = async (type, params = {}) => {
    setActivePanel(type);
    setPanelLoading(true);
    setInteractiveData(null);
    try {
      const queryParams = new URLSearchParams(params).toString();
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/api/${type}${queryParams ? '?' + queryParams : ''}`);
      setInteractiveData(res.data);
    } catch (err) {
      setError(`Error fetching ${type}: ` + (err.response?.data?.detail || err.message));
      setActivePanel(null);
    } finally {
      setPanelLoading(false);
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <Routes>
      <Route path="/" element={
        <div className="min-h-screen flex flex-col font-sans bg-gray-50 dark:bg-dark-bg transition-colors duration-500">
          <Header 
            theme={theme} 
            toggleTheme={toggleTheme} 
            onHistoryOpen={() => setIsHistoryOpen(true)}
            onSidebarToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          />
          
          <div className="flex flex-col lg:flex-row flex-1 overflow-hidden h-[calc(100vh-64px)] relative">
            <div className="flex-1 flex flex-col overflow-y-auto px-4 sm:px-6 py-6 sm:py-8 relative custom-scrollbar z-0 w-full">
              <MainPanel 
                error={error}
                setLoading={setLoading} 
                setError={setError} 
                onOpenPanel={handleOpenPanel}
                onRefreshHistory={fetchHistory}
                onOpenAdvanced={() => setIsAdvancedOpen(true)}
              />
            </div>
            {/* Backdrop for mobile sidebar */}
            {isSidebarOpen && (
              <div 
                className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 lg:hidden backdrop-blur-sm"
                onClick={() => setIsSidebarOpen(false)}
              />
            )}
            <Sidebar 
              theme={theme} 
              isOpen={isSidebarOpen} 
              onClose={() => setIsSidebarOpen(false)} 
            />
          </div>

          {/* Dataset Registry Modal */}
          <HistoryModal 
            isOpen={isHistoryOpen}
            onClose={() => setIsHistoryOpen(false)}
            history={history}
            onSelect={async (id) => {
              setLoading(true);
              setError(null);
              try {
                const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/load/${id}`);
                // Notify parent through a success message or similar if needed
              } catch (err) {
                setError('Error loading from history: ' + (err.response?.data?.detail || err.message));
              } finally {
                setLoading(false);
              }
            }}
            onClear={clearHistory}
          />

          {/* Interactive Window Panel */}
          <InteractiveModal 
            isOpen={!!activePanel}
            onClose={() => setActivePanel(null)}
            type={activePanel}
            data={interactiveData}
            loading={panelLoading}
            theme={theme}
            onUpdateParams={(newParams) => handleOpenPanel(activePanel, newParams)}
          />

          {/* Advanced AI Orchestration Modal */}
          {isAdvancedOpen && (
            <AdvancedAnalysis onClose={() => setIsAdvancedOpen(false)} />
          )}
        </div>
      } />
      <Route path="/standalone/:viewType" element={<StandaloneView theme={theme} toggleTheme={toggleTheme} />} />
    </Routes>
  );
}

export default App;
