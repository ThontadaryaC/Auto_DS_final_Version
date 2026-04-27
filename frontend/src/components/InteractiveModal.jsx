import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';
import { 
  X, 
  Download, 
  Palette, 
  BarChart3, 
  PieChart, 
  LineChart, 
  Settings, 
  FileText, 
  Loader2,
  Check,
  Maximize2,
  RefreshCw
} from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const InteractiveModal = ({ isOpen, onClose, type, data, loading, theme, onUpdateParams }) => {
  const [chartType, setChartType] = useState('bar');
  const [brandColor, setBrandColor] = useState('#6366f1'); // Indigo-500 default
  const [showGrid, setShowGrid] = useState(true);
  const [localReport, setLocalReport] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const chartRef = useRef(null);

  // Vite compatibility fix for CommonJS react-plotly.js module export
  const PlotComponent = typeof Plot === 'object' && Plot.default ? Plot.default : Plot;

  // Sync data.report into local state if it ever changes
  useEffect(() => {
    if (data?.report) {
      setLocalReport(data.report);
    } else {
      setLocalReport(null);
    }
  }, [data]);

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/report`, { view_type: type });
      setLocalReport(res.data.report);
    } catch (err) {
      console.error("Error generating report", err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.report || "Error generating report. Please check the backend connection.";
      setLocalReport(errorMsg);
    } finally {
      setGeneratingReport(false);
    }
  };

  const colors = [
    { name: 'Indigo', value: '#6366f1' },
    { name: 'Rose', value: '#f43f5e' },
    { name: 'Emerald', value: '#10b981' },
    { name: 'Amber', value: '#f59e0b' },
    { name: 'Sky', value: '#0ea5e9' },
    { name: 'Violet', value: '#8b5cf6' },
  ];

  const graphTypes = [
    { id: 'bar', icon: BarChart3, label: 'Bar' },
    { id: 'scatter', icon: LineChart, label: 'Line' },
    { id: 'pie', icon: PieChart, label: 'Pie' },
    { id: 'histogram', icon: Maximize2, label: 'Histogram' },
  ];

  const downloadPDF = async () => {
    if (!chartRef.current) return;
    
    const canvas = await html2canvas(chartRef.current, {
      scale: 2,
      backgroundColor: theme === 'dark' ? '#111827' : '#ffffff',
    });
    
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    
    pdf.setFontSize(22);
    pdf.setTextColor(theme === 'dark' ? '#ffffff' : '#000000');
    pdf.text(`AutoDS AI - ${type.toUpperCase()} Report`, 10, 20);
    
    pdf.setFontSize(12);
    pdf.text(`Generated on: ${new Date().toLocaleString()}`, 10, 30);
    
    pdf.addImage(imgData, 'PNG', 10, 40, pdfWidth - 20, pdfHeight - 20);
    
    if (localReport) {
      pdf.addPage();
      pdf.setFontSize(18);
      pdf.setTextColor(theme === 'dark' ? '#111827' : '#000000'); // PDF is usually white background
      pdf.text('Comprehensive AI Strategic Analysis', 15, 20);
      
      pdf.setFontSize(10);
      const splitText = pdf.splitTextToSize(localReport, pdfWidth - 30);
      let y = 35;
      const pageHeight = pdf.internal.pageSize.getHeight();
      
      splitText.forEach((line) => {
        if (y > pageHeight - 20) {
          pdf.addPage();
          y = 20;
        }
        pdf.text(line, 15, y);
        y += 6;
      });
    }
    
    pdf.save(`AutoDS_AI_${type}_Report.pdf`);
  };

  if (!isOpen) return null;

  // Prepare plotly data based on tools
  const getProcessedData = (traces, chartKey) => {
    if (!traces || !Array.isArray(traces)) return [];
    return traces.map(trace => {
      let newTrace = { ...trace };
      
      // Apply chart type override ONLY for 'insights' single chart view
      // If we have a suite of charts (data.charts), we respect the backend specialization
      if (type === 'insights' && !data?.charts) {
        newTrace.type = chartType;
      }
      
      // Apply color theme, BUT protect Pie charts and Heatmaps from monolithic coloring
      const isMultiColor = ['pie', 'heatmap', 'treemap', 'sunburst'].includes(newTrace.type) || 
                          ['pie', 'heatmap', 'correlation'].includes(chartKey);
      
      if (!isMultiColor) {
        if (newTrace.marker) {
          if (!Array.isArray(newTrace.marker.color)) {
            newTrace.marker = { ...newTrace.marker, color: brandColor };
          }
        } else {
          newTrace.marker = { color: brandColor };
        }
      }

      if (chartType === 'scatter' && type === 'insights' && !data?.charts) {
        newTrace.mode = 'lines+markers';
      }
      
      return newTrace;
    });
  };


  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: theme === 'dark' ? '#f3f4f6' : '#1f2937' },
    autosize: true,
    margin: { t: 40, r: 20, l: 40, b: 40 },
    xaxis: { showgrid: showGrid, gridcolor: theme === 'dark' ? '#374151' : '#e5e7eb' },
    yaxis: { showgrid: showGrid, gridcolor: theme === 'dark' ? '#374151' : '#e5e7eb' },
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-300">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
        onClick={onClose} 
      />
      
      <div className="relative w-full max-w-7xl h-[90vh] glass-panel overflow-hidden flex flex-col shadow-2xl border-brand-500/20">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-dark-panel/50 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-500/10 rounded-lg text-brand-500">
              <Settings className="w-5 h-5 animate-spin-slow" />
            </div>
            <div>
              <h2 className="text-xl font-bold capitalize">{type} Windows Panel</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">Interactive Data Exploration Tool</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={downloadPDF}
              className="flex items-center gap-2 px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-all font-medium text-sm shadow-lg shadow-brand-500/20 active:scale-95"
            >
              <Download className="w-4 h-4" />
              Download Report (PDF)
            </button>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Tool Sidebar */}
          <div className="w-64 border-r border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-dark-panel/30 p-6 space-y-8 overflow-y-auto">
            {/* Color section */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Palette className="w-4 h-4" />
                Theme Colors
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {colors.map((c) => (
                  <button
                    key={c.name}
                    onClick={() => setBrandColor(c.value)}
                    className="w-full aspect-square rounded-lg border-2 transition-all relative group"
                    style={{ 
                      backgroundColor: c.value, 
                      borderColor: brandColor === c.value ? 'white' : 'transparent' 
                    }}
                    title={c.name}
                  >
                    {brandColor === c.value && (
                      <Check className="w-4 h-4 text-white absolute inset-0 m-auto" />
                    )}
                    <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity rounded-lg" />
                  </button>
                ))}
              </div>
            </div>

            {/* Graph Type section - Only show for Insights where we modify a single chart structure */}
            {type === 'insights' && !data?.charts && (
              <div className="space-y-4">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Chart Structure
                </h3>

                <div className="space-y-2">
                  {graphTypes.map((gt) => {
                    const Icon = gt.icon;
                    return (
                      <button
                        key={gt.id}
                        onClick={() => setChartType(gt.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all border ${
                          chartType === gt.id 
                          ? 'bg-brand-500 text-white border-brand-500 shadow-md' 
                          : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-brand-400'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <span className="font-semibold text-sm">{gt.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Model Selection for Predict */}
            {type === 'predict' && (
              <div className="space-y-4">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  ML Forecast Models
                </h3>
                <div className="space-y-2">
                  {[
                    { id: 'linear', label: 'Linear Regression' },
                    { id: 'random_forest', label: 'Random Forest' },
                    { id: 'moving_average', label: 'Moving Average' }
                  ].map(m => (
                    <button
                      key={m.id}
                      onClick={() => onUpdateParams({ model: m.id })}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        // We don't have current model in props easily, let's just use it as a trigger
                        'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/10'
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* AI Report Customization */}
            <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-800">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Report Settings
              </h3>
              <div className="space-y-3">
                <label className="block text-xs font-medium text-gray-500 uppercase">Analysis Tone</label>
                <div className="grid grid-cols-2 gap-2">
                  {['Professional', 'Concise', 'Creative', 'Technical'].map(tone => (
                    <button
                      key={tone}
                      className="px-2 py-1.5 text-[10px] font-bold border border-gray-200 dark:border-gray-700 rounded-md hover:border-brand-500 transition-colors"
                    >
                      {tone}
                    </button>
                  ))}
                </div>
                <button 
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="w-full py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg text-xs font-bold flex items-center justify-center gap-2 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all border border-gray-200 dark:border-gray-700 disabled:opacity-50"
                >
                  {generatingReport ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                  Generate AI Analysis
                </button>
              </div>
            </div>

            {/* Grid Toggle */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
              <label className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm font-medium group-hover:text-brand-500 transition-colors">Show Grid Lines</span>
                <input 
                  type="checkbox" 
                  checked={showGrid} 
                  onChange={() => setShowGrid(!showGrid)}
                  className="w-4 h-4 accent-brand-500 rounded cursor-pointer"
                />
              </label>
            </div>
          </div>

          {/* Main Visualizer */}
          <div className="flex-1 flex flex-col bg-white dark:bg-dark-bg overflow-y-auto">
            {loading ? (
              <div className="flex-1 flex flex-col items-center justify-center opacity-60">
                <Loader2 className="w-12 h-12 animate-spin text-brand-500 mb-4" />
                <p className="font-medium">Synthesizing Interactive View...</p>
              </div>
            ) : (
              <div className="p-8 space-y-8 h-full overflow-y-auto custom-scrollbar">
                
                <div ref={chartRef} className="space-y-6">
                  {data?.charts ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                      {Object.entries(data.charts).map(([key, chart]) => {
                        const isWide = ['scatter', 'line', 'bar', 'impact_scatter', 'time_series', 'distribution', 'correlation', 'hierarchy'].includes(key);

                        return (
                          <div 
                            key={key} 
                            className={`glass-panel p-4 h-[350px] relative group ${isWide ? 'md:col-span-2 xl:col-span-2' : 'col-span-1'}`}
                          >
                            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                              <div className="p-1.5 bg-brand-500/10 rounded-lg text-brand-500">
                                <Maximize2 className="w-3 h-3" />
                              </div>
                            </div>
                            <PlotComponent
                              data={getProcessedData(chart.data, key)}
                              layout={{ ...chart.layout, ...layout, margin: { t: 30, r: 10, l: 30, b: 30 } }}
                              useResizeHandler={true}
                              style={{ width: '100%', height: '100%' }}
                              config={{ displayModeBar: false, responsive: true }}
                            />
                          </div>
                        );
                      })}
                    </div>
                  ) : data?.chart ? (
                    <div className="glass-panel p-6 min-h-[500px] h-[60vh] relative group">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                        <div className="p-2 bg-brand-500/10 rounded-lg text-brand-500">
                          <Maximize2 className="w-4 h-4" />
                        </div>
                      </div>
                      <PlotComponent
                        data={getProcessedData(data.chart.data)}
                        layout={{ ...data.chart.layout, ...layout }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ displayModeBar: true, responsive: true }}
                      />
                      {type === 'predict' && data?.model_name && (
                        <div className="absolute bottom-4 left-6 px-3 py-1 bg-brand-500/10 text-brand-500 rounded-full text-[10px] font-black uppercase tracking-widest border border-brand-500/20 animate-bounce-slow">
                          AutoML Selected: {data.model_name}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="glass-panel p-8 min-h-[400px] flex flex-col items-center justify-center opacity-50">
                      <p className="font-medium text-gray-500">No data available for display.</p>
                    </div>
                  )}

                  {/* AI Report Card */}
                  <div className="p-6 bg-brand-50 dark:bg-brand-900/10 border border-brand-200 dark:border-brand-800 rounded-2xl relative">
                    <h4 className="flex items-center gap-2 text-brand-700 dark:text-brand-400 font-bold uppercase tracking-widest text-xs mb-4">
                      <FileText className="w-4 h-4" />
                      AI Analysis Report
                    </h4>
                    
                    {!localReport ? (
                      <div className="flex flex-col items-center justify-center py-6 text-brand-600/70 dark:text-brand-400/70">
                        {generatingReport ? (
                          <>
                            <Loader2 className="w-8 h-8 animate-spin mb-3" />
                            <p className="text-sm font-medium animate-pulse text-center">
                              AI is researching the web for industry context <br/>
                              and analyzing your dataset...
                            </p>
                          </>
                        ) : (
                          <>
                            <p className="text-sm font-medium mb-4">No AI report generated yet.</p>
                            <button 
                              onClick={handleGenerateReport}
                              className="px-6 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-full text-xs font-bold transition-all shadow-lg active:scale-95"
                            >
                              Generate Insight Report
                            </button>
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="prose dark:prose-invert max-w-none max-h-[600px] overflow-y-auto custom-scrollbar pr-4">
                        <div className="text-gray-700 dark:text-gray-300 leading-relaxed space-y-4 whitespace-pre-wrap text-base font-medium">
                          {localReport}
                        </div>
                        <div className="mt-8 pt-6 border-t border-brand-200 dark:border-brand-800 flex items-center justify-between">
                           <p className="text-[10px] font-black text-brand-500 uppercase tracking-widest">End of Master Analysis</p>
                           <button 
                             onClick={handleGenerateReport}
                             disabled={generatingReport}
                             className="text-xs font-bold text-brand-500 hover:text-brand-600 flex items-center gap-1 transition-colors"
                           >
                             {generatingReport ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                             Regenerate Detailed Report
                           </button>
                        </div>
                      </div>
                    )}
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

export default InteractiveModal;
