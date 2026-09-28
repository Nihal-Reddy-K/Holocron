import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Movement from "./pages/Movement";
import Sessions from "./pages/Sessions";
import Stimulation from "./pages/Stimulation";
import Reports from "./pages/Reports";

function App() {
  return (
    <BrowserRouter>
      <div className="app">

        <Sidebar />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/movement" element={<Movement />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/stimulation" element={<Stimulation />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>

      </div>
    </BrowserRouter>
  );
}

export default App;