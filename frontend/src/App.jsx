import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Login from "./pages/Login";
import Analysis from "./pages/Analysis";
import Results from "./pages/Results";
import Navbar from "./components/Navbar";
import Signup from "./pages/Signup";
import Profile from "./pages/Profile";
import UploadAssessment from "./pages/UploadAssessment";
import SitStandResults from "./pages/SitStandResults";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/upload-assessment" element={<UploadAssessment />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/results" element={<Results />} />
        <Route path="/sit-stand-results" element={<SitStandResults />} />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;