import React from 'react';
import { X, Trash2, Database, Clock, FileCheck } from 'lucide-react';

const HistoryModal = ({ isOpen, onClose, history, onSelect, onClear }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-300">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
        onClick={onClose} 
      />
      
      <div className="relative w-full max-w-2xl h-[70vh] glass-panel overflow-hidden flex flex-col shadow-2xl border-brand-500/20">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-dark-panel/50 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-500/10 rounded-lg text-brand-500">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Dataset Registry</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">View and load previously uploaded files</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
             {history.length > 0 && (
              <button 
                onClick={onClear}
                className="flex items-center gap-2 px-3 py-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all text-xs font-bold"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </button>
            )}
            <button 
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
          {history.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center opacity-40 text-center">
              <Clock className="w-12 h-12 mb-4" />
              <p className="font-medium text-lg">Your registry is empty</p>
              <p className="text-sm">Upload some files to see them here.</p>
            </div>
          ) : (
            history.map((record) => (
              <div 
                key={record.id}
                className="group p-4 rounded-2xl border border-gray-100 dark:border-white/5 bg-white/50 dark:bg-white/5 hover:border-brand-500/50 transition-all premium-card flex items-center justify-between"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-10 h-10 bg-brand-500/10 rounded-xl flex items-center justify-center text-brand-500">
                    <FileCheck className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-sm dark:text-gray-200 group-hover:text-brand-500 transition-colors uppercase truncate">
                      {record.filename}
                    </h4>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        {record.record_count} Records
                      </span>
                      <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                        {new Date(record.upload_time).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <button 
                  onClick={() => {
                    onSelect(record.id);
                    onClose();
                  }}
                  className="px-4 py-2 bg-brand-500 text-white rounded-xl text-[10px] font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity shadow-lg shadow-brand-500/20"
                >
                  Load Dataset
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;
