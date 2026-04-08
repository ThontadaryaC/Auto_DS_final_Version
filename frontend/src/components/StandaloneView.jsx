import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Loader2, AlertCircle, Maximize2, Minimize2, Sun, Moon } from 'lucide-react';
import ViewSidebar from './ViewSidebar';
import OutputArea from './OutputArea';

const StandaloneView = ({ theme, toggleTheme }) => {
    const { viewType } = useParams();
    const [searchParams] = useSearchParams();
    
    const [charts, setCharts] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const [settings, setSettings] = useState({
        themeName: 'Default',
        plotlyTemplate: 'plotly_white',
        colors: ['#6366f1', '#818cf8', '#a5b4fc'],
        chartType: 'line',
        model: 'linear',
        periods: 10
    });

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            let endpoint = viewType;
            if (viewType === 'predict') {
                endpoint = `predict?model=${settings.model}&periods=${settings.periods}`;
            }
            const res = await axios.get(`${import.meta.env.VITE_API_URL}/api/${endpoint}`);
            setCharts(res.data);
        } catch (err) {
            setError(`Error fetching ${viewType}: ` + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    }, [viewType, settings.model, settings.periods]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleColorChange = (preset) => {
        setSettings(prev => ({ 
            ...prev, 
            themeName: preset.name, 
            plotlyTemplate: preset.value,
            colors: preset.colors 
        }));
    };

    const handleChartTypeChange = (type) => {
        setSettings(prev => ({ ...prev, chartType: type }));
    };

    const handleModelChange = (model) => {
        setSettings(prev => ({ ...prev, model }));
    };

    const handlePeriodsChange = (periods) => {
        setSettings(prev => ({ ...prev, periods }));
    };

    // Apply customization to the chart data before passing it to OutputArea
    const getProcessedCharts = () => {
        if (!charts) return null;
        
        const applyCustomization = (plot) => {
            if (!plot || !plot.data) return plot;
            
            const newPlot = JSON.parse(JSON.stringify(plot)); // Deep clone
            
            // Apply plotly template
            if (!newPlot.layout) newPlot.layout = {};
            newPlot.layout.template = settings.plotlyTemplate;
            
            // Apply chart type (if applicable)
            newPlot.data = newPlot.data.map((trace, idx) => {
                const updatedTrace = { ...trace };
                if (settings.chartType === 'bar') {
                    updatedTrace.type = 'bar';
                } else if (settings.chartType === 'area') {
                    updatedTrace.type = 'scatter';
                    updatedTrace.fill = 'tozeroy';
                } else if (settings.chartType === 'line') {
                    updatedTrace.type = 'scatter';
                    updatedTrace.mode = 'lines+markers';
                }
                
                // Color mapping
                if (settings.colors[idx % settings.colors.length]) {
                     if (!updatedTrace.marker) updatedTrace.marker = {};
                     updatedTrace.marker.color = settings.colors[idx % settings.colors.length];
                }
                
                return updatedTrace;
            });
            
            return newPlot;
        };

        if (charts.charts) { // Dashboard
            const updatedDashboard = { ...charts, charts: {} };
            Object.entries(charts.charts).forEach(([key, plot]) => {
                updatedDashboard.charts[key] = applyCustomization(plot);
            });
            return updatedDashboard;
        } else if (charts.chart) { // Single chart
            return { ...charts, chart: applyCustomization(charts.chart) };
        }
        return charts;
    };

    return (
        <div className={`flex h-screen w-screen overflow-hidden ${theme === 'dark' ? 'bg-dark-bg text-gray-100' : 'bg-gray-100 text-gray-900'}`}>
            <ViewSidebar 
                viewType={viewType}
                onColorChange={handleColorChange}
                onChartTypeChange={handleChartTypeChange}
                onModelChange={handleModelChange}
                onPeriodsChange={handlePeriodsChange}
                currentSettings={settings}
            />
            
            <div className="flex-1 flex flex-col h-full overflow-hidden relative">
                {/* Minimal Header */}
                <header className="h-14 border-b border-gray-200 dark:border-dark-border px-6 flex items-center justify-between bg-white dark:bg-dark-panel">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
                            <Maximize2 className="w-5 h-5 text-white" />
                        </div>
                        <h1 className="font-bold text-lg uppercase tracking-wider">
                            {viewType} <span className="text-brand-500">Standalone</span>
                        </h1>
                    </div>
                    
                    <button 
                        onClick={toggleTheme}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                        {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5 text-amber-400" />}
                    </button>
                </header>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto p-8 bg-gray-50 dark:bg-dark-bg custom-scrollbar">
                    {loading ? (
                        <div className="h-full flex flex-col items-center justify-center gap-4">
                            <Loader2 className="w-12 h-12 animate-spin text-brand-500" />
                            <p className="text-gray-500 font-medium animate-pulse">Computing and Stylizing...</p>
                        </div>
                    ) : error ? (
                        <div className="glass-panel p-8 border-red-500 flex flex-col items-center justify-center text-red-500 mx-auto max-w-2xl mt-20">
                            <AlertCircle className="w-12 h-12 mb-4" />
                            <p className="font-semibold text-xl mb-2">Analysis Failed</p>
                            <p className="text-center opacity-80">{error}</p>
                        </div>
                    ) : (
                        <div className="max-w-[1400px] mx-auto animate-in fade-in zoom-in-95 duration-500">
                             <OutputArea charts={getProcessedCharts()} theme={theme} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StandaloneView;
