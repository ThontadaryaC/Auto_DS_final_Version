import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { 
  Brain, 
  Target, 
  Fingerprint, 
  Layers, 
  Loader2, 
  TrendingUp, 
  Zap,
  Activity,
  ArrowRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';

const AdvancedAnalysis = ({ onClose }) => {
  const [strategy, setStrategy] = useState(null);
  const [loadingStrategy, setLoadingStrategy] = useState(true);
  const [activeAnalysis, setActiveAnalysis] = useState(null); // 'clustering', 'anomaly', 'automl'
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Vite compatibility fix for CommonJS react-plotly.js module export
  const PlotComponent = typeof Plot === 'object' && Plot.default ? Plot.default : Plot;

  useEffect(() => {
    fetchStrategy();
  }, []);

  const fetchStrategy = async () => {
    setLoadingStrategy(true);
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/api/analyze/strategy`);
      setStrategy(res.data);
    } catch (err) {
      console.error("Strategy fetch failed", err);
    } finally {
      setLoadingStrategy(false);
    }
  };

  const runAnalysis = async (type) => {
    setActiveAnalysis(type);
    setLoadingAnalysis(true);
    setAnalysisResult(null);
    try {
      let endpoint = '';
      let payload = {};

      if (type === 'clustering') {
        endpoint = '/api/analyze/clustering';
        payload = { n_clusters: strategy?.clustering?.suggested_k, features: strategy?.clustering?.recommended_features };
      } else if (type === 'anomaly') {
        endpoint = '/api/analyze/anomaly';
        payload = { contamination: strategy?.anomaly?.contamination };
      } else if (type === 'automl') {
        endpoint = '/api/analyze/automl';
        payload = { 
          target_col: strategy?.automl?.target_col,
          task_type: strategy?.automl?.task_type
        };
      }

      const res = await axios.post(`${import.meta.env.VITE_API_URL}${endpoint}`, payload);
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(`${type} analysis failed`, err);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 md:p-10 animate-in fade-in duration-500">
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xl" onClick={onClose} />
      
      <div className="relative w-full max-w-7xl h-[90vh] glass-panel bg-slate-900 border-brand-500/30 overflow-hidden flex flex-col shadow-2xl">
        {/* Animated Glows */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-500/5 rounded-full blur-[120px] -mr-64 -mt-64 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[120px] -ml-64 -mb-64 pointer-events-none" />

        {/* Header */}
        <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between relative z-10 bg-white/[0.02]">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="absolute inset-0 bg-brand-500/20 blur-xl rounded-full animate-pulse" />
              <div className="relative p-3.5 bg-brand-500 rounded-2xl shadow-lg shadow-brand-500/20">
                <Brain className="w-7 h-7 text-white" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-black text-white flex items-center gap-3">
                Strategic AI Orchestration
                <span className="text-[10px] py-1 px-2 bg-brand-500/10 text-brand-500 border border-brand-500/20 rounded-md font-black uppercase tracking-widest">Master Brain v3</span>
              </h2>
              <p className="text-sm text-slate-400 font-bold uppercase tracking-widest mt-0.5">Automated Neural Decision & Execute Engine</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="p-3 bg-white/5 hover:bg-white/10 rounded-full transition-all text-slate-400 hover:text-white border border-white/5"
          >
            <Activity className="w-6 h-6 rotate-90" />
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden relative z-10">
          {/* Strategy & Control Pane */}
          <div className="w-1/3 border-r border-white/5 p-8 overflow-y-auto space-y-8 bg-slate-900/50">
            {loadingStrategy ? (
              <div className="h-64 flex flex-col items-center justify-center space-y-4 opacity-40">
                <Cpu className="w-12 h-12 text-brand-500 animate-pulse" />
                <p className="text-xs font-black text-brand-500 uppercase tracking-widest">Cognitive Mapping in Progress...</p>
              </div>
            ) : (
              <div className="space-y-8 animate-in slide-in-from-left-4 duration-700">
                {/* Domain Insight */}
                <div className="space-y-3">
                   <h3 className="text-[10px] font-black text-brand-500 uppercase tracking-widest flex items-center gap-2">
                     <ShieldCheck className="w-3 h-3" /> Data Domain Detected
                   </h3>
                   <div className="p-5 bg-white/[0.02] border border-white/5 rounded-2xl">
                     <p className="text-2xl font-black text-white">{strategy?.domain}</p>
                     <p className="text-xs font-medium text-slate-500 mt-2 leading-relaxed">"{strategy?.thinking}"</p>
                   </div>
                </div>

                {/* Tactical Operations */}
                <div className="space-y-4">
                  <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Targeted ML Executions</h3>
                  
                  {/* Clustering */}
                  <button 
                    onClick={() => runAnalysis('clustering')}
                    className={`w-full group p-6 rounded-2xl border transition-all text-left flex items-start gap-4 ${
                      activeAnalysis === 'clustering' 
                      ? 'bg-brand-500/10 border-brand-500 ring-1 ring-brand-500/20' 
                      : 'bg-white/[0.02] border-white/5 hover:border-brand-500/40'
                    }`}
                  >
                    <Layers className={`w-6 h-6 mt-1 transition-transform group-hover:scale-110 ${activeAnalysis === 'clustering' ? 'text-brand-500' : 'text-slate-500'}`} />
                    <div>
                      <h4 className="font-black text-sm text-white uppercase tracking-tight mb-1">Neural Clustering</h4>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Group similar patterns ({strategy?.clustering?.suggested_k} segments)</p>
                    </div>
                  </button>

                  {/* Anomaly */}
                  <button 
                    onClick={() => runAnalysis('anomaly')}
                    className={`w-full group p-6 rounded-2xl border transition-all text-left flex items-start gap-4 ${
                      activeAnalysis === 'anomaly' 
                      ? 'bg-rose-500/10 border-rose-500 ring-1 ring-rose-500/20' 
                      : 'bg-white/[0.02] border-white/5 hover:border-rose-500/40'
                    }`}
                  >
                    <Fingerprint className={`w-6 h-6 mt-1 transition-transform group-hover:scale-110 ${activeAnalysis === 'anomaly' ? 'text-rose-500' : 'text-slate-500'}`} />
                    <div>
                      <h4 className="font-black text-sm text-white uppercase tracking-tight mb-1">Anomaly Radar</h4>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Outlier isolation @ {strategy?.anomaly?.contamination * 100}% contamination</p>
                    </div>
                  </button>

                  {/* AutoML */}
                  <button 
                    onClick={() => runAnalysis('automl')}
                    className={`w-full group p-6 rounded-2xl border transition-all text-left flex items-start gap-4 ${
                      activeAnalysis === 'automl' 
                      ? 'bg-amber-500/10 border-amber-500 ring-1 ring-amber-500/20' 
                      : 'bg-white/[0.02] border-white/5 hover:border-amber-500/40'
                    }`}
                  >
                    <Target className={`w-6 h-6 mt-1 transition-transform group-hover:scale-110 ${activeAnalysis === 'automl' ? 'text-amber-500' : 'text-slate-500'}`} />
                    <div>
                      <h4 className="font-black text-sm text-white uppercase tracking-tight mb-1">High-Precision AutoML</h4>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Target: {strategy?.automl?.target_col} ({strategy?.automl?.task_type})</p>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Execution Environment */}
          <div className="flex-1 bg-black/40 flex flex-col">
            {loadingAnalysis ? (
              <div className="flex-1 flex flex-col items-center justify-center space-y-6 opacity-60">
                <div className="relative">
                  <Activity className="w-16 h-16 text-brand-500 animate-pulse" />
                  <Loader2 className="absolute inset-0 w-16 h-16 text-brand-500/30 animate-spin" />
                </div>
                <div className="text-center">
                  <h3 className="text-xl font-black text-white uppercase tracking-tighter">Processing Signal Vectors</h3>
                  <p className="text-xs font-black text-slate-500 uppercase tracking-widest mt-2">Industrial Precision Training in Progress...</p>
                </div>
              </div>
            ) : analysisResult ? (
              <div className="flex-1 p-8 space-y-8 overflow-y-auto">
                {/* Result KPI Header */}
                <div className="grid grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
                  <div className="p-6 bg-white/[0.03] border-l-4 border-brand-500 rounded-r-2xl border border-white/5">
                    <h5 className="text-[10px] font-black text-brand-500 uppercase tracking-widest mb-1.5">Primary Precision Metric</h5>
                    <p className="text-4xl font-black text-white">{analysisResult.accuracy || "N/A"}</p>
                    <p className="text-[10px] font-bold text-slate-500 mt-2 uppercase flex items-center gap-1.5">
                       <ShieldCheck className="w-3 h-3 text-emerald-500" /> Signal Logic Validated
                    </p>
                  </div>
                  <div className="p-6 bg-white/[0.03] border-l-4 border-slate-500 rounded-r-2xl border border-white/5">
                    <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Orchestrator Observation</h5>
                    <p className="text-sm font-bold text-slate-300 leading-tight italic">"{analysisResult.summary}"</p>
                  </div>
                </div>

                {/* Plot Space */}
                <div className="p-4 bg-white/[0.02] border border-white/5 rounded-3xl h-[500px] shadow-inner relative group">
                  <div className="absolute top-4 right-4 z-20">
                    <span className="px-3 py-1 bg-black/40 backdrop-blur-md rounded-full text-[10px] font-black text-slate-500 border border-white/5 group-hover:text-brand-500 transition-colors uppercase tracking-widest">Live Signal Feed</span>
                  </div>
                  <PlotComponent
                    data={(analysisResult.main_chart || analysisResult.chart).data}
                    layout={{ 
                      ...(analysisResult.main_chart || analysisResult.chart).layout,
                      autosize: true,
                      paper_bgcolor: 'transparent',
                      plot_bgcolor: 'transparent',
                      font: { color: '#94a3b8', family: "'Inter', sans-serif" },
                      xaxis: { ...((analysisResult.main_chart || analysisResult.chart).layout.xaxis || {}), gridcolor: '#1e293b' },
                      yaxis: { ...((analysisResult.main_chart || analysisResult.chart).layout.yaxis || {}), gridcolor: '#1e293b' }
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                    config={{ responsive: true, displayModeBar: false }}
                  />
                </div>

                {/* Accessory View (e.g. Elbow Chart) */}
                {analysisResult.elbow_chart && (
                  <div className="p-4 bg-white/[0.01] border border-white/5 rounded-3xl h-[300px]">
                    <PlotComponent
                      data={analysisResult.elbow_chart.data}
                      layout={{ 
                        ...analysisResult.elbow_chart.layout,
                        autosize: true,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        font: { color: '#64748b', size: 10 }
                      }}
                      useResizeHandler={true}
                      style={{ width: '100%', height: '100%' }}
                      config={{ responsive: true, displayModeBar: false }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center opacity-20">
                <div className="relative mb-8">
                   <div className="absolute inset-0 bg-brand-500/10 blur-3xl animate-pulse" />
                   <Cpu className="w-24 h-24 text-slate-700 relative" />
                </div>
                <div className="text-center max-w-md">
                   <h3 className="text-2xl font-black text-slate-700 uppercase tracking-tighter">Command Center Standby</h3>
                   <p className="text-xs font-bold text-slate-700 uppercase tracking-widest mt-3 leading-relaxed">
                     Awaiting tactical signal from the strategic brain. Select an execution path from the left control pane to begin.
                   </p>
                   <div className="mt-10 flex items-center justify-center gap-2 text-brand-500 font-black italic text-sm">
                      <ArrowRight className="w-6 h-6 animate-bounce" /> Tactical Signal Required
                   </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalysis;
