import React from 'react';
import Plot from 'react-plotly.js';
import { Loader2, AlertCircle, Sparkles } from 'lucide-react';

const OutputArea = ({ charts, loading, error, theme, compact = false }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 min-h-[300px] bg-white/5 dark:bg-black/20 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700">
        <Loader2 className="w-10 h-10 animate-spin text-brand-500 mb-4" />
        <p className="text-gray-500 text-sm font-medium animate-pulse">AI is thinking...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 min-h-[300px] bg-red-500/5 rounded-2xl border border-red-500/20 text-red-500">
        <AlertCircle className="w-10 h-10 mb-4" />
        <p className="text-sm font-medium text-center">{error}</p>
      </div>
    );
  }

  if (!charts) {
    return (
      <div className="flex flex-col items-center justify-center p-8 min-h-[300px] bg-gray-50/50 dark:bg-dark-panel/20 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 opacity-40">
        <p className="text-gray-400 text-sm font-medium italic">Pending Analysis</p>
      </div>
    );
  }

  const plotLayout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: {
      color: theme === 'dark' ? '#f3f4f6' : '#1f2937',
      size: compact ? 10 : 12
    },
    autosize: true,
    showlegend: !compact,
  };

  const renderChart = (chartData) => (
    <div className="w-full h-full min-h-[300px]">
      <Plot
        data={chartData.data}
        layout={{ 
          ...chartData.layout, 
          ...plotLayout,
          margin: { t: 30, r: 10, l: 30, b: 30 }
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* AI Analysis Report Card */}
      {charts.report && (
        <div className="p-4 bg-brand-500/5 border border-brand-500/20 rounded-xl animate-in fade-in slide-in-from-top-2 duration-500">
            <h4 className="flex items-center gap-2 text-brand-500 font-bold uppercase tracking-widest text-[10px] mb-2">
                <Sparkles className="w-3 h-3" />
                AI Insight
            </h4>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-xs italic">
                "{charts.report}"
            </p>
        </div>
      )}

      <div className="flex-1 min-h-0">
        {charts.charts ? ( // Dashboard case
          Object.keys(charts.charts).length > 0 ? (
            <div className="grid grid-cols-1 gap-4 h-full overflow-y-auto custom-scrollbar pr-2">
                {Object.entries(charts.charts).map(([key, chart]) => (
                <div key={key} className="bg-white/50 dark:bg-black/20 rounded-xl p-2 border border-gray-200 dark:border-gray-800 h-[250px]">
                    {renderChart(chart)}
                </div>
                ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-8 bg-amber-500/5 rounded-2xl border border-amber-500/20">
              <AlertCircle className="w-8 h-8 mb-2 text-amber-500" />
              <p className="text-xs font-medium text-gray-500">No data for visual.</p>
            </div>
          )
        ) : charts.chart ? ( // Single chart case (Insights or Predict)
            <div className="bg-white/50 dark:bg-black/20 rounded-xl p-2 border border-gray-200 dark:border-gray-800 h-full min-h-[300px]">
                {renderChart(charts.chart)}
            </div>
        ) : null}
      </div>
    </div>
  );
};

export default OutputArea;
