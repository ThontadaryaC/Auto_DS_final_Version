import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
  UploadCloud, 
  BarChart, 
  TrendingUp, 
  Presentation, 
  X, 
  LayoutDashboard,
  Zap,
  Brain,
  ArrowRight
} from 'lucide-react';

const MainPanel = ({ error, setLoading, setError, onOpenPanel, onRefreshHistory, onOpenAdvanced }) => {
  const [observation, setObservation] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    setObservation(null);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if (res.data.observation) {
        setObservation(res.data.observation);
      }
      onRefreshHistory(); 
    } catch (err) {
      setError('Error uploading file: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, onRefreshHistory]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
      'application/xhtml+xml': ['.xml']
    },
    multiple: false
  });

  return (
    <div className="space-y-6 md:space-y-10 max-w-[1400px] mx-auto animate-in fade-in duration-700 w-full">
      {/* Expanded Upload Section */}
      <div className="glass-panel p-6 sm:p-8 md:p-12 relative overflow-hidden group border-brand-500/20 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl group-hover:bg-brand-500/20 transition-all duration-1000" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl group-hover:bg-brand-500/10 transition-all duration-1000" />
        
        <div className="relative z-10 w-full">
          <div className="flex flex-col items-center text-center mb-10 w-full">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-black tracking-tighter dark:text-white flex flex-col md:flex-row items-center gap-2 md:gap-4 mb-3">
              <LayoutDashboard className="w-8 h-8 md:w-10 md:h-10 text-brand-500 shrink-0" />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-600 via-brand-400 to-indigo-500 leading-tight">AutoDS AI Ecosystem</span>
            </h2>
            <p className="text-sm md:text-base text-gray-500 dark:text-gray-400 font-medium max-w-lg px-2">
              Upload your raw datasets to unlock automated machine learning insights, interactive visualizations, and deep AI observations.
            </p>
          </div>
          
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-[2rem] p-6 sm:p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-700 min-h-[280px] md:min-h-[380px] relative w-full
              ${isDragActive ? 'border-brand-500 bg-brand-500/5 scale-[1.02]' : 'border-gray-200 dark:border-white/10 hover:border-brand-500/50 hover:bg-brand-500/5'}
            `}
          >
            <input {...getInputProps()} />
            <div className="w-20 h-20 md:w-24 md:h-24 bg-brand-500/10 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-700 relative">
               <div className="absolute inset-0 bg-brand-500/20 rounded-full animate-ping opacity-20" />
               <UploadCloud className={`w-10 h-10 md:w-12 md:h-12 ${isDragActive ? 'text-brand-500' : 'text-gray-400'}`} />
            </div>
            <p className="text-xl md:text-2xl font-black mb-2 dark:text-gray-100 text-center">Ready to Discover?</p>
            <p className="text-sm md:text-base text-gray-500 dark:text-gray-400 font-bold mb-6 text-center">Drop your CSV, XML or Excel file here</p>
            <div className="px-6 py-3 bg-brand-500 text-white rounded-full text-xs font-black uppercase tracking-widest shadow-xl shadow-brand-500/20 hover:bg-brand-600 transition-all active:scale-95">
              Browse Files
            </div>
          </div>
        </div>
      </div>

      {/* Observation Banner */}
      {observation && (
        <div className="p-6 bg-gradient-to-r from-brand-500/10 to-transparent border-l-8 border-brand-500 rounded-2xl animate-in fade-in slide-in-from-left-4 duration-1000 shadow-xl backdrop-blur-sm">
          <div className="flex items-start gap-6">
            <div className="p-3 bg-brand-500 text-white rounded-2xl shadow-xl shadow-brand-500/30">
              <Zap className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h4 className="text-[12px] font-black text-brand-500 uppercase tracking-[0.2em] mb-2">Lead Strategist Insight</h4>
              <p className="text-gray-700 dark:text-gray-300 text-lg italic font-bold leading-relaxed">"{observation}"</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg animate-in fade-in slide-in-from-left-4 duration-500 flex items-start gap-4">
          <div className="p-2 bg-red-500 text-white rounded-lg shadow-lg">
            <X className="w-4 h-4" />
          </div>
          <div className="flex-1">
            <h4 className="text-[10px] font-black text-red-600 dark:text-red-400 uppercase tracking-widest mb-1">Action Failed</h4>
            <p className="text-red-700 dark:text-red-300 text-sm font-medium">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="p-1 text-red-400 hover:text-red-600 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Featured: Strategic AI Orchestration */}
      <div className="animate-in slide-in-from-bottom-2 duration-500">
        <button 
          onClick={onOpenAdvanced}
          className="w-full glass-panel p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-8 border-brand-500/20 hover:border-brand-500/50 transition-all premium-card group relative overflow-hidden"
        >
          {/* Decorative Glow */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-brand-500/20 transition-all duration-700" />
          
          <div className="flex flex-col md:flex-row items-center gap-8 relative z-10">
            <div className="relative">
              <div className="absolute inset-0 bg-brand-500/20 blur-xl rounded-full animate-pulse group-hover:bg-brand-500/40" />
              <div className="relative w-20 h-20 bg-brand-500/10 text-brand-500 rounded-[2rem] flex items-center justify-center group-hover:scale-110 group-hover:rotate-12 transition-all duration-500 border border-brand-500/20">
                <Brain className="w-10 h-10" />
              </div>
            </div>
            <div className="text-center md:text-left">
              <h3 className="text-3xl font-black text-white group-hover:text-brand-400 transition-colors tracking-tight">Strategic AI Orchestration</h3>
              <p className="text-sm text-gray-500 font-bold uppercase tracking-[0.2em] mt-1.5">Master Brain: Pattern Discovery & Precision Execution</p>
              <div className="flex flex-wrap gap-4 mt-5 justify-center md:justify-start">
                <span className="text-[10px] px-2.5 py-1 bg-indigo-500/10 text-indigo-400 rounded-md border border-indigo-500/20 font-black tracking-widest uppercase">Clustering Matrix</span>
                <span className="text-[10px] px-2.5 py-1 bg-rose-500/10 text-rose-400 rounded-md border border-rose-500/20 font-black tracking-widest uppercase">Anomaly Radar</span>
                <span className="text-[10px] px-2.5 py-1 bg-amber-500/10 text-amber-400 rounded-md border border-amber-500/20 font-black tracking-widest uppercase">99% Accuracy AutoML</span>
              </div>
            </div>
          </div>
          
          <div className="shrink-0 flex items-center gap-4 px-8 py-4 bg-white/5 border border-white/10 rounded-3xl text-xs font-black uppercase tracking-[0.2em] group-hover:bg-brand-500 group-hover:text-white group-hover:border-brand-500 transition-all active:scale-95 shadow-xl">
             Launch Signal Brain
             <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>
      </div>

      {/* THE 3 BUTTONS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-12">
        <button 
          onClick={() => onOpenPanel('dashboard')}
          className="glass-panel p-8 flex flex-col items-center justify-center gap-5 hover:border-brand-500/50 transition-all premium-card group h-48"
        >
          <div className="w-16 h-16 bg-indigo-500/10 text-indigo-500 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-700">
            <Presentation className="w-8 h-8" />
          </div>
          <div className="text-center">
            <h3 className="font-black text-lg">Interactive Dashboard</h3>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">Multi-angle Viz</p>
          </div>
        </button>

        <button 
          onClick={() => onOpenPanel('predict')}
          className="glass-panel p-8 flex flex-col items-center justify-center gap-5 hover:border-brand-500/50 transition-all premium-card group h-48"
        >
          <div className="w-16 h-16 bg-pink-500/10 text-pink-500 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-700">
            <TrendingUp className="w-8 h-8" />
          </div>
          <div className="text-center">
            <h3 className="font-black text-lg">AutoML Prediction</h3>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">Forecast Analysis</p>
          </div>
        </button>

        <button 
          onClick={() => onOpenPanel('insights')}
          className="glass-panel p-8 flex flex-col items-center justify-center gap-5 hover:border-brand-500/50 transition-all premium-card group h-48"
        >
          <div className="w-16 h-16 bg-amber-500/10 text-amber-500 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-700">
            <BarChart className="w-8 h-8" />
          </div>
          <div className="text-center">
            <h3 className="font-black text-lg">Statistical Insights</h3>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">Distribution View</p>
          </div>
        </button>
      </div>
    </div>
  );
};

export default MainPanel;
