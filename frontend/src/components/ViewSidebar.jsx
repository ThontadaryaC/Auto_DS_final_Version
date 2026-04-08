import React from 'react';
import { Palette, BarChart3, TrendingDown, Settings, Maximize, Check } from 'lucide-react';

const ViewSidebar = ({ 
    viewType, 
    onColorChange, 
    onChartTypeChange, 
    onModelChange, 
    onPeriodsChange,
    currentSettings 
}) => {
    const colorPresets = [
        { name: 'Default', value: 'plotly_white', colors: ['#6366f1', '#818cf8', '#a5b4fc'] },
        { name: 'Sunset', value: 'plotly_dark', colors: ['#f43f5e', '#fb923c', '#facc15'] },
        { name: 'Ocean', value: 'ggplot2', colors: ['#0891b2', '#22d3ee', '#67e8f9'] },
        { name: 'Modern', value: 'simple_white', colors: ['#334155', '#64748b', '#94a3b8'] }
    ];

    const chartTypes = [
        { id: 'bar', name: 'Bar Chart', icon: BarChart3 },
        { id: 'line', name: 'Line Chart', icon: TrendingDown },
        { id: 'area', name: 'Area Chart', icon: Maximize }
    ];

    const mlModels = [
        { id: 'linear', name: 'Linear Regression' },
        { id: 'random_forest', name: 'Random Forest' },
        { id: 'moving_average', name: 'Moving Average' }
    ];

    return (
        <div className="w-72 h-full border-r border-gray-200 dark:border-dark-border bg-white dark:bg-dark-panel flex flex-col shadow-xl z-20">
            <div className="p-4 border-b border-gray-200 dark:border-dark-border flex items-center gap-2 bg-brand-50/50 dark:bg-brand-900/10">
                <Settings className="w-5 h-5 text-brand-500" />
                <h2 className="font-semibold text-gray-800 dark:text-gray-100">Customization</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-8">
                {/* 1. Appearance / Colors */}
                <section className="space-y-4">
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                        <Palette className="w-3 h-3" />
                        Color Theme
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                        {colorPresets.map((preset) => (
                            <button
                                key={preset.name}
                                onClick={() => onColorChange(preset)}
                                className={`p-2 rounded-lg border text-sm text-left transition-all ${
                                    currentSettings.themeName === preset.name 
                                    ? 'border-brand-500 ring-2 ring-brand-500/20 bg-brand-50 dark:bg-brand-900/20' 
                                    : 'border-gray-200 dark:border-gray-700 hover:border-brand-300'
                                }`}
                            >
                                <div className="flex gap-1 mb-1">
                                    {preset.colors.map((c, i) => (
                                        <div key={i} className="w-2 h-2 rounded-full" style={{ backgroundColor: c }} />
                                    ))}
                                </div>
                                <span className="font-medium dark:text-gray-200">{preset.name}</span>
                            </button>
                        ))}
                    </div>
                </section>

                {/* 2. Plot Type (Applicable to all except complex dashboards maybe) */}
                <section className="space-y-4">
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                        <BarChart3 className="w-3 h-3" />
                        Visual Type
                    </h3>
                    <div className="space-y-2">
                        {chartTypes.map((type) => (
                            <button
                                key={type.id}
                                onClick={() => onChartTypeChange(type.id)}
                                className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all ${
                                    currentSettings.chartType === type.id
                                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300'
                                    : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50'
                                }`}
                            >
                                <div className="flex items-center gap-2 text-sm font-medium">
                                    <type.icon className="w-4 h-4" />
                                    {type.name}
                                </div>
                                {currentSettings.chartType === type.id && <Check className="w-4 h-4" />}
                            </button>
                        ))}
                    </div>
                </section>

                {/* 3. ML Model Selection (Prediction Specific) */}
                {viewType === 'predict' && (
                    <section className="space-y-4">
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <TrendingDown className="w-3 h-3" />
                            ML Models
                        </h3>
                        <div className="space-y-2">
                            {mlModels.map((model) => (
                                <button
                                    key={model.id}
                                    onClick={() => onModelChange(model.id)}
                                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                                        currentSettings.model === model.id
                                        ? 'border-pink-500 bg-pink-50 dark:bg-pink-900/20 text-pink-700 dark:text-pink-300'
                                        : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50'
                                    }`}
                                >
                                    <span className="text-sm font-medium">{model.name}</span>
                                </button>
                            ))}
                        </div>

                        <div className="pt-4">
                            <label className="text-xs font-bold text-gray-400 uppercase block mb-3">
                                Future Prediction Steps ({currentSettings.periods})
                            </label>
                            <input 
                                type="range" 
                                min="5" 
                                max="50" 
                                step="5"
                                value={currentSettings.periods}
                                onChange={(e) => onPeriodsChange(parseInt(e.target.value))}
                                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-brand-500"
                            />
                            <div className="flex justify-between text-[10px] text-gray-500 mt-2">
                                <span>5</span>
                                <span>25</span>
                                <span>50</span>
                            </div>
                        </div>
                    </section>
                )}
            </div>

            <div className="p-4 bg-gray-50 dark:bg-dark-panel border-t border-gray-200 dark:border-dark-border text-[10px] text-gray-400 text-center">
                Powered by AutoDS AI Analytics
            </div>
        </div>
    );
};

export default ViewSidebar;
