import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#FDFDF7] text-zinc-900 p-6 md:p-12 font-sans selection:bg-zinc-200">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:justify-between md:items-end border-b border-zinc-200 pb-8 mb-12 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-4">
               <div className="w-4 h-4 bg-zinc-900 text-[#FDFDF7] flex items-center justify-center rounded-sm">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <span className="font-semibold text-sm tracking-tight">Athlix</span>
            </div>
            <h1 className="text-3xl font-medium tracking-tight mb-2">Workspace</h1>
            <p className="text-md text-zinc-500 font-light">Select a movement to analyze or view recent feedback.</p>
          </div>
          <button 
            onClick={() => navigate('/upload')}
            className="px-6 py-3 bg-zinc-900 text-[#FDFDF7] font-medium rounded-sm hover:bg-zinc-800 transition w-full md:w-auto text-sm"
          >
            Upload Video
          </button>
        </header>

        <main className="grid lg:grid-cols-3 gap-16">
          
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-12">
            <div>
              <h2 className="text-lg font-medium text-zinc-900 mb-6">
                Active Modules
              </h2>
              
              <div className="grid sm:grid-cols-2 gap-6">
                {/* Squat Card */}
                <div 
                  className="group relative bg-white border border-zinc-200 rounded-sm p-8 hover:border-zinc-400 transition-colors cursor-pointer" 
                  onClick={() => navigate('/upload')}
                >
                  <div className="absolute top-6 right-6 flex items-center">
                    <span className="flex h-1.5 w-1.5 rounded-full bg-zinc-800 mr-2"></span>
                    <span className="text-zinc-500 text-[10px] font-medium uppercase tracking-wider">Available</span>
                  </div>
                  <h3 className="text-xl font-medium text-zinc-900 mb-3 group-hover:text-zinc-600 transition">Squat Analysis</h3>
                  <p className="text-zinc-500 mb-8 text-sm font-light leading-relaxed">
                    Full-body biomechanical tracking. Detect depth, forward lean, and form decay.
                  </p>
                  <div className="flex items-center text-zinc-800 font-medium text-xs uppercase tracking-wide group-hover:translate-x-1 transition-transform">
                    Start Analysis <span className="ml-2">→</span>
                  </div>
                </div>

                {/* Bowling Card */}
                <div className="relative bg-[#FAF9F5] border border-zinc-200 p-8 rounded-sm">
                  <div className="absolute top-6 right-6 flex items-center">
                    <span className="text-zinc-400 text-[10px] font-medium uppercase tracking-wider">Demo / Beta</span>
                  </div>
                  <h3 className="text-xl font-medium text-zinc-400 mb-3">Cricket Bowling</h3>
                  <p className="text-zinc-400 mb-8 text-sm font-light leading-relaxed">
                    Pace and spin kinematics. Run-up momentum, release angle, and front-foot contact.
                  </p>
                  <div className="flex items-center text-zinc-400 font-medium text-xs uppercase tracking-wide">
                    Coming Soon
                  </div>
                </div>
              </div>
            </div>
            
            {/* Short Info Banner */}
            <div className="bg-white border text-center border-zinc-200 p-8 rounded-sm text-sm font-light leading-relaxed text-zinc-600">
              Athlix processes high-speed video through proprietary vision models. Keep your camera stable and ensure full body visibility for accurate kinematic extraction.
            </div>

          </div>

          {/* Right Sidebar Area */}
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-zinc-900 mb-6 border-b border-zinc-200 pb-2">
              Capabilities
            </h2>
            
            <div className="space-y-6">
              
              <div>
                <h4 className="text-zinc-900 font-medium text-sm mb-1">Pose Flaw Detection</h4>
                <p className="text-zinc-500 text-sm font-light">Automatic detection of severe posture mistakes.</p>
              </div>

              <div>
                <h4 className="text-zinc-900 font-medium text-sm mb-1">Form Decay Tracking</h4>
                <p className="text-zinc-500 text-sm font-light">Monitor form degradation across all repetitions.</p>
              </div>

              <div>
                <h4 className="text-zinc-900 font-medium text-sm mb-1">Explainable Injury Risk</h4>
                <p className="text-zinc-500 text-sm font-light">Correlate kinematic data with potential strain injuries.</p>
              </div>

              <div>
                <h4 className="text-zinc-900 font-medium text-sm mb-1">Coaching Feedback</h4>
                <p className="text-zinc-500 text-sm font-light">Get precise cues instantly to fix your form.</p>
              </div>

            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
