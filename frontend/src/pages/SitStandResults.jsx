import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function SitStandResults() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem('temp_analysis');
    if (saved) {
      setData(JSON.parse(saved));
    } else {
      navigate('/dashboard');
    }
  }, [navigate]);

  if (!data) return null;

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-12 font-sans pb-24">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex justify-between items-center border-b border-zinc-900 pb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#32ade6] mb-2">Sit-to-Stand Results</h1>
            <p className="text-zinc-400">Your movement and balance analysis.</p>
          </div>
          <button 
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-[#111] hover:bg-[#222] border border-zinc-800 rounded-lg text-sm font-bold uppercase transition"
          >
            Done
          </button>
        </header>

        {/* Overall Feedback Card */}
        <div className="bg-[#111] border border-zinc-800 rounded-2xl p-8 flex flex-col md:flex-row items-center gap-8">
          <div className="w-32 h-32 flex-shrink-0 bg-black rounded-full border-4 border-[#32ade6] flex flex-col items-center justify-center shadow-[0_0_20px_rgba(50,173,230,0.2)]">
            <span className="text-5xl font-black text-white">{data.score}</span>
            <span className="text-xs text-zinc-500 font-bold uppercase tracking-widest mt-1">/ 100</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold mb-4">Overall Feedback</h2>
            <p className="text-zinc-300 text-lg leading-relaxed">{data.summary}</p>
          </div>
        </div>

        {/* Key Observations */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold border-b border-zinc-900 pb-4">Key Observations</h2>
          <div className="grid gap-6 md:grid-cols-2">
            {data.keyIssues?.slice(0, 4).map((issue, idx) => (
              <div key={idx} className="bg-[#0a0a0a] border border-zinc-800 rounded-2xl p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 rounded-full bg-[#32ade6]/10 text-[#32ade6] flex items-center justify-center font-bold text-lg">
                    {idx + 1}
                  </div>
                  <h3 className="font-bold text-lg leading-tight">{issue.issue}</h3>
                </div>
                <p className="text-zinc-400 text-sm mb-6 leading-relaxed min-h-[40px]">{issue.detail}</p>
                <div className="bg-[#111] border border-zinc-800 rounded-xl p-4 text-[#32ade6]">
                  <strong className="block mb-1 text-[10px] uppercase tracking-widest text-zinc-500">Suggestion</strong>
                  <span className="font-medium text-sm">{issue.fix}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simple Recommendation Box */}
        <div className="bg-gradient-to-br from-[#111] to-[#050505] border border-zinc-800 rounded-2xl p-8 mt-8">
          <h2 className="text-xl font-bold mb-8">Basic Tips for You</h2>
          <ul className="space-y-6">
            {data.coachingTips?.slice(0, 3).map((tip, idx) => (
              <li key={idx} className="flex items-start gap-4">
                <div className="mt-2 w-2 h-2 bg-[#32ade6] rounded-full flex-shrink-0 animate-pulse"></div>
                <p className="text-zinc-300 leading-relaxed font-medium">
                  {tip.cue}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default SitStandResults;
