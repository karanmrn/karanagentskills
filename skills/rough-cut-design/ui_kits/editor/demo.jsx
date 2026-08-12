/* global React, ReactDOM, RC_DATA,
   Topbar, Transcript, PlayerSurface, AgentDock */

const { useState } = React;

function App() {
  const [footages, setFootages] = useState(RC_DATA.footages);
  const [activeFootageId, setActiveFootageId] = useState(RC_DATA.footages[0].id);
  const [activePassageId, setActivePassageId] = useState("p_a4");
  const [draft, setDraft] = useState("");

  const togglePassage = (passageId) => {
    setFootages((fs) => fs.map((f) => ({
      ...f,
      passages: f.passages.map((p) => {
        if (p.id !== passageId) return p;
        const next = p.status === "keep" ? "skip" : p.status === "skip" ? "keep" : "skip";
        return { ...p, status: next };
      }),
    })));
    // Also set active footage to the one containing the touched passage.
    const owner = footages.find((f) => f.passages.some((p) => p.id === passageId));
    if (owner) setActiveFootageId(owner.id);
    setActivePassageId(passageId);
  };

  const project = RC_DATA.project;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--canvas)" }}>
      <Topbar project={project} onEndSession={() => { /* no-op in demo */ }} />

      <main style={{
        flex: 1, minHeight: 0,
        display: "grid",
        gridTemplateColumns: "minmax(0, 1.35fr) minmax(380px, 0.65fr)",
        minHeight: "780px",
      }}>
        <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
          <Transcript
            footages={footages}
            onTogglePassage={togglePassage}
            activePassageId={activePassageId}
            activeFootageId={activeFootageId}
            onSelectFootage={setActiveFootageId}
          />
        </div>

        <aside style={{ display: "flex", flexDirection: "column", minHeight: 0, background: "var(--canvas)", borderLeft: "1px solid var(--line)" }}>
          <PlayerSurface
            project={project}
            footages={footages}
            activeFootageId={activeFootageId}
            onSelectFootage={setActiveFootageId}
          />
          <AgentDock
            messages={RC_DATA.chatMessages}
            presence={project.agentPresence}
            draft={draft}
            setDraft={setDraft}
            onSend={() => { setDraft(""); }}
          />
        </aside>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
