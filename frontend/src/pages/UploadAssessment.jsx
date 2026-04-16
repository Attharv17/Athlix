import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeMovement } from "../services/analysisService";

function UploadAssessment() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
        setSelectedFile(file);
      }
    }
  };
  const clearFile = (e) => {
    if (e) e.stopPropagation();
    setSelectedFile(null);
  };
  const resetAnalysis = () => {
    clearFile();
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setError(null);

    try {
      // Pass null for both profile and session context to keep it general
      await analyzeMovement(selectedFile, { profile: null, sessionContext: null }, 'sit_to_stand');
      navigate('/analysis');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-black p-12 text-white font-sans flex items-center justify-center selection:bg-zinc-700">
        <div className="w-full max-w-lg border border-zinc-900 bg-[#050505] p-16 text-center shadow-2xl">
          <h2 className="text-red-500 font-bold uppercase tracking-[0.2em] mb-4 text-xs">Error Occurred</h2>
          <p className="text-zinc-500 font-mono text-xs mb-12 tracking-wide leading-relaxed">{error}</p>
          <button onClick={resetAnalysis} className="px-10 py-5 bg-white text-black font-bold uppercase text-[10px] tracking-widest hover:bg-zinc-300 transition-colors w-full">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-16 font-sans selection:bg-zinc-700 pb-24">
      <div className="max-w-4xl mx-auto">
        <header className="flex items-center justify-between border-b border-zinc-900 pb-10 mb-16">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-zinc-500 hover:text-white transition flex items-center group"
          >
            <svg className="w-5 h-5 mr-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="text-[10px] font-bold tracking-[0.2em] uppercase">Return to Dashboard</span>
          </button>
        </header>

        <div className="space-y-12">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-black tracking-tighter uppercase mb-4 text-[#32ade6]">Sit-to-Stand Assessment</h1>
            <p className="text-zinc-400 font-light tracking-wide text-lg max-w-2xl mx-auto">
              Please upload a video of yourself standing up from a chair and sitting back down. Ensure your full body and the chair are visible.
            </p>
          </div>

          <div className="border border-zinc-900 pt-8 rounded-2xl bg-[#050505] p-12">
            {!selectedFile ? (
              <div
                className={`relative border border-zinc-800 bg-black p-24 text-center rounded-xl transition-all cursor-pointer group ${isDragOver ? 'border-[#32ade6] bg-[#111] scale-[1.01]' : 'hover:border-[#32ade6]/50 hover:bg-[#0a0a0a]'}`}
                onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}
                onClick={() => document.getElementById('image-upload').click()}
              >
                <input type="file" id="image-upload" className="hidden" accept=".jpg,.jpeg,.png,.webp,.mp4,.mov,.webm" onChange={handleFileChange} />
                <div className="w-20 h-20 rounded-full border border-zinc-800 bg-[#050505] flex items-center justify-center mx-auto mb-8 group-hover:border-[#32ade6] group-hover:bg-[#32ade6]/10 transition-colors">
                  <svg className="w-8 h-8 text-zinc-500 group-hover:text-[#32ade6] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                <p className="text-white font-bold tracking-widest uppercase text-sm mb-4">Click or Drag File Here</p>
                <p className="text-zinc-500 text-xs font-light tracking-[0.1em] uppercase">Accepts Video or Image files</p>
              </div>
            ) : (
              <div className="bg-[#111] border border-zinc-700 p-16 rounded-xl flex flex-col items-center relative overflow-hidden group">
                <div className="w-16 h-16 rounded-full border border-[#32ade6] bg-[#32ade6] flex items-center justify-center mb-8 relative z-10 shadow-[0_0_30px_rgba(50,173,230,0.3)]">
                  <svg className="w-6 h-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                </div>
                <h3 className="text-white font-bold text-lg uppercase tracking-wider truncate max-w-sm mb-2 relative z-10" title={selectedFile.name}>{selectedFile.name}</h3>
                <p className="text-zinc-400 text-xs font-mono tracking-widest relative z-10 mb-10">STATUS: READY | {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                <button onClick={clearFile} className="text-[10px] uppercase tracking-[0.2em] font-bold text-zinc-500 hover:text-red-400 transition-all relative z-10 pb-1">Remove File</button>
              </div>
            )}
          </div>

          <div className="pt-4 flex justify-center">
            <button
              disabled={!selectedFile || isProcessing}
              onClick={handleAnalyze}
              className={`w-1/2 py-6 rounded-xl font-black uppercase tracking-[0.2em] text-sm transition-all ${selectedFile && !isProcessing
                ? 'bg-[#32ade6] hover:bg-[#32ade6]/90 text-black shadow-[0_0_40px_rgba(50,173,230,0.3)] cursor-pointer'
                : 'bg-[#111] text-zinc-700 cursor-not-allowed'
                }`}
            >
              {isProcessing ? 'Analyzing Movement...' : 'Start Assessment'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadAssessment;
