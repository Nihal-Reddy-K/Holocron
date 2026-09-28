function Stimulation() {
  return (
    <div
      style={{
        maxWidth: "1100px",
        margin: "0 auto",
        padding: "10px 0",
      }}
    >
      <div style={{ marginBottom: "28px" }}>
        <div
          style={{
            fontSize: "11px",
            fontWeight: "700",
            letterSpacing: "1.4px",
            color: "#7a817c",
            marginBottom: "8px",
          }}
        >
          STIMULATION
        </div>

        <h1
          style={{
            margin: 0,
            fontSize: "32px",
            color: "#202321",
          }}
        >
          Stimulation
        </h1>

        <p
          style={{
            color: "#737a75",
            fontSize: "14px",
            marginTop: "8px",
          }}
        >
          Monitor and review stimulation sessions.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "16px",
        }}
      >
        <div
          style={{
            height: "360px",
            border: "1px solid #e1e5e2",
            borderRadius: "12px",
            background: "#fff",
            padding: "24px",
          }}
        >
          <h2 style={{ margin: 0, fontSize: "16px" }}>
            Session monitor
          </h2>

          <div
            style={{
              height: "260px",
              marginTop: "20px",
              borderRadius: "8px",
              border: "1px solid #edf0ee",
              background:
                "linear-gradient(#f0f2f0 1px, transparent 1px), linear-gradient(90deg, #f0f2f0 1px, transparent 1px)",
              backgroundSize: "40px 40px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#8a918c",
              fontSize: "13px",
            }}
          >
            Session monitor · Demo
          </div>
        </div>

        <div
          style={{
            border: "1px solid #e1e5e2",
            borderRadius: "12px",
            background: "#fff",
            padding: "24px",
          }}
        >
          <h2 style={{ margin: 0, fontSize: "16px" }}>
            Session
          </h2>

          <div style={{ marginTop: "24px" }}>
            <p>Protocol</p>
            <strong>Demo / unconfigured</strong>

            <p>Target</p>
            <strong>Not configured</strong>

            <p>Device</p>
            <strong>Backend pending</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Stimulation;