function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <span className="logo-mark">H</span>
        <span>Holocron</span>
      </div>

      <nav className="sidebar-nav">

        <a href="/">Overview</a>

        <a href="/movement">Movement</a>

        <a href="/sessions">Sessions</a>

        <a href="/stimulation">Stimulation</a>

        <a href="/reports">Reports</a>

      </nav>

    </aside>
  );
}

export default Sidebar;