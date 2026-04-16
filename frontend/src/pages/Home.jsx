import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#FDFDF7] text-zinc-900 selection:bg-zinc-200 font-sans">

      {/* Navigation / Header */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-8 flex justify-between items-center bg-[#FDFDF7] z-50">
        <div className="text-xl font-bold tracking-tight flex items-center gap-2">
          <div className="w-6 h-6 bg-zinc-900 text-[#FDFDF7] flex items-center justify-center rounded-sm">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          Athlix.
        </div>
      </nav>

      <main className="pb-24">
        {/* Hero Section */}
        <div className="relative w-full bg-zinc-900 pt-32 pb-40 mb-24 flex items-center justify-center">
          {/* Background Image Layer */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-40 mix-blend-luminosity"
            style={{ backgroundImage: "url('https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=2069&auto=format&fit=crop')" }}
          ></div>
          {/* Gradient Overlay for Readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/80 to-zinc-900/30"></div>

          {/* Hero Content */}
          <div className="relative z-10 max-w-4xl mx-auto text-center px-6 mt-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 border border-zinc-600 rounded-full text-xs font-medium text-zinc-300 mb-8 tracking-wide">
              Athlix Beta
            </div>

            <h1 className="text-5xl md:text-7xl font-semibold tracking-tight text-white leading-[1.1] mb-8 shadow-sm">
              The movement <br className="hidden md:block" />
              intelligence platform.
            </h1>

            <p className="mt-6 text-xl md:text-2xl text-zinc-300 max-w-2xl mx-auto leading-relaxed mb-12 font-light">
              Analyze biomechanics for gym and sports with computer vision. Detect form flaws, track fatigue decay, and prevent injuries.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-8 py-4 bg-white text-zinc-900 text-md font-medium rounded-sm hover:bg-zinc-100 transition"
              >
                Explore Dashboard
              </button>

              <button
                onClick={() => navigate('/upload')}
                className="px-8 py-4 bg-transparent border border-zinc-500 text-white text-md font-medium rounded-sm hover:border-white transition"
              >
                Upload Video
              </button>
            </div>
          </div>
        </div>

        {/* Problem Section */}
        <div className="max-w-5xl mx-auto py-16 mb-24 border-y border-zinc-200 text-center">
          <h2 className="text-2xl font-medium text-zinc-900 mb-6">
            Why Athletes Get Injured
          </h2>
          <p className="text-lg text-zinc-600 max-w-3xl mx-auto font-light leading-relaxed">
            Injuries are rarely structural; they are usually postural. Athletes push beyond their boundaries, often not realizing their biomechanical form is degrading under accumulating fatigue. Athlix makes this invisible problem visible.
          </p>
        </div>

        {/* Vision/Movement Types Section */}
        <div className="mb-32">
          <h2 className="text-3xl font-semibold mb-12 text-center text-zinc-900">One platform. Every movement.</h2>

          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8">
            {/* MVP Squat */}
            <div className="bg-white border border-zinc-200 p-10 rounded-sm relative group transition-colors">
              <div className="absolute top-8 right-8 text-xs font-medium text-zinc-400 tracking-wide">
                MVP Available
              </div>
              <h3 className="text-2xl font-medium mb-4 text-zinc-900">Gym Movements</h3>
              <p className="text-zinc-600 mb-8 font-light leading-relaxed">Fully implemented biomechanical analysis for heavy lifts. Currently featuring deep Squat analysis with real-time risk assessment.</p>
              <ul className="space-y-4">
                <li className="flex items-start text-zinc-800 text-sm">
                  <span className="mr-3 text-zinc-400">—</span>
                  Knee varus and valgus tracking
                </li>
                <li className="flex items-start text-zinc-800 text-sm">
                  <span className="mr-3 text-zinc-400">—</span>
                  Hip depth & torso lean detection
                </li>
              </ul>
            </div>

            {/* Vision Bowling */}
            <div className="bg-[#FAF9F5] border border-zinc-200 p-10 rounded-sm relative">
              <div className="absolute top-8 right-8 text-xs font-medium text-zinc-400 tracking-wide">
                Coming Soon
              </div>
              <h3 className="text-2xl font-medium mb-4 text-zinc-900">Sports Biomechanics</h3>
              <p className="text-zinc-500 mb-8 font-light leading-relaxed">Extensible architecture built to support highly dynamic, explosive sports actions. Starting with fast bowling.</p>
              <ul className="space-y-4 opacity-70">
                <li className="flex items-start text-zinc-600 text-sm">
                  <span className="mr-3 text-zinc-300">—</span>
                  Release angle & run-up momentum
                </li>
                <li className="flex items-start text-zinc-600 text-sm">
                  <span className="mr-3 text-zinc-300">—</span>
                  Front-foot contact force modeling
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-semibold mb-12 text-center text-zinc-900">The Intelligence Engine</h2>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-16">

            <div className="border-t border-zinc-200 pt-6">
              <h3 className="text-xl font-medium text-zinc-900 mb-3">Flaw Detection</h3>
              <p className="text-zinc-600 font-light leading-relaxed">
                Automatically identify critical posture mistakes down to the exact degree without needing manual video scrubbing.
              </p>
            </div>

            <div className="border-t border-zinc-200 pt-6">
              <h3 className="text-xl font-medium text-zinc-900 mb-3">Form Decay</h3>
              <p className="text-zinc-600 font-light leading-relaxed">
                Track how technique visibly deteriorates rep-by-rep under accumulating fatigue across sets.
              </p>
            </div>

            <div className="border-t border-zinc-200 pt-6">
              <h3 className="text-xl font-medium text-zinc-900 mb-3">Risk Assessment</h3>
              <p className="text-zinc-600 font-light leading-relaxed">
                Understand exactly why specific kinematic patterns drastically elevate localized injury probabilities.
              </p>
            </div>

            <div className="border-t border-zinc-200 pt-6">
              <h3 className="text-xl font-medium text-zinc-900 mb-3">Coaching Feedback</h3>
              <p className="text-zinc-600 font-light leading-relaxed">
                Receive actionable, personalized coaching cues to correct form and improve mechanical efficiency instantly.
              </p>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}

export default Home;

