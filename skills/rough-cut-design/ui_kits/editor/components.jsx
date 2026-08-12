/* global React, Icon, Button, Pill, Tag, Hairline, KeyHint, Eyebrow, StatusDot */

const { useState, useMemo } = React;

// ---------- helpers ----------
function fmt(s) {
  if (!Number.isFinite(s)) return "00:00.0";
  const m = Math.floor(s / 60);
  const r = s - m * 60;
  return `${String(m).padStart(2, "0")}:${r.toFixed(1).padStart(4, "0")}`;
}
function fmtShort(s) { return fmt(s).slice(0, 5); }
function keptSeconds(footage) {
  return footage.passages.filter((p) => p.status !== "skip").reduce((acc, p) => acc + (p.end - p.start), 0);
}

// =========================================================================
// TOPBAR — wordmark + session-level meta. The browser session is always
// one project, started from `rough-cut-axi open …`. The only project-level
// state worth showing here is whether the session is alive, plus a way to
// end it (which terminates the local server).
// =========================================================================
function Topbar({ project, onEndSession }) {
  return (
    <header style={{
      display: "flex", alignItems: "center", gap: "14px",
      padding: "10px 20px",
      background: "var(--canvas)",
      borderBottom: "1px solid var(--line)",
      height: "52px", boxSizing: "border-box", flexShrink: 0,
    }}>
      <div style={{ lineHeight: 1, position: "relative", display: "inline-flex", flexShrink: 0, alignItems: "center" }}>
        <span style={{ fontFamily: "var(--font-display)", fontStyle: "italic", fontSize: "24px", letterSpacing: "-0.03em", color: "var(--ink)" }}>rough</span>
        <span style={{ position: "relative", display: "inline-block", width: "10px", height: "30px", margin: "0 0 0 3px" }}>
          <svg viewBox="0 0 10 34" width="10" height="34" style={{ position: "absolute", inset: 0, overflow: "visible" }}>
            <polygon points="1,2 9,2 5,8" fill="var(--vermillion)" />
            <line x1="5" y1="8" x2="5" y2="32" stroke="var(--vermillion)" strokeWidth="1.25" strokeLinecap="square" />
          </svg>
        </span>
        <span style={{ fontFamily: "var(--font-display)", fontStyle: "italic", fontSize: "24px", letterSpacing: "-0.03em", color: "var(--ink)" }}>cut</span>
      </div>

      {/* Session meta: a quiet "last saved" status. Everything lives on
          disk and updates on the fly, so this confirms persistence is
          working without ever being noisy. */}
      {project && (
        <>
          <div style={{ width: "1px", height: "22px", background: "var(--line)", flexShrink: 0 }} />
          <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: 0, flexShrink: 1, fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-3)", overflow: "hidden" }}>
            <StatusDot state="ok" size={6} />
            <span style={{ whiteSpace: "nowrap" }}>saved {project.lastSaved}</span>
          </div>
        </>
      )}

      <div style={{ flex: 1 }} />

      <Button variant="default" size="sm" icon="log-out" onClick={onEndSession}>End session</Button>
    </header>
  );
}

// =========================================================================
// TRANSCRIPT — the manuscript. Footages are separated by a horizontal rule.
// =========================================================================
function Transcript({ footages, onTogglePassage, activePassageId, activeFootageId, onSelectFootage }) {
  const totalPassages = footages.reduce((acc, f) => acc + f.passages.length, 0);

  const totalSeconds = footages.reduce((acc, f) => acc + keptSeconds(f), 0);

  return (
    <div style={{
      flex: 1, minHeight: 0, overflow: "auto",
      background: "var(--paper)",
      backgroundImage: "linear-gradient(90deg, rgba(116,78,39,0.04), transparent 4%, transparent 96%, rgba(116,78,39,0.04))",
      borderRight: "1px solid var(--line)",
    }}>
      <article style={{
        maxWidth: "780px", margin: "0 auto",
        padding: "36px 56px 64px", boxSizing: "border-box",
      }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <Eyebrow style={{ color: "var(--ink-3)", marginBottom: "10px" }}>§ Manuscript · {footages.length} footages · {totalPassages} passages</Eyebrow>
          <h1 style={{
            fontFamily: "var(--font-display)", fontWeight: 400, fontStyle: "italic",
            fontSize: "44px", lineHeight: 1, letterSpacing: "-0.035em",
            color: "var(--ink)", margin: 0,
          }}>Cinema, in two notes</h1>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-2)", marginTop: "12px", letterSpacing: "0.04em", fontVariantNumeric: "tabular-nums" }}>
            cut runs {fmt(totalSeconds)}
          </div>
          <Hairline style={{ marginTop: "24px", background: "var(--line-paper)", maxWidth: "120px", marginLeft: "auto", marginRight: "auto" }} />
        </div>

        {footages.map((footage, fi) => (
          <React.Fragment key={footage.id}>
            {fi > 0 && <FootageDivider footage={footage} />}
            <FootageSection
              footage={footage}
              isFirst={fi === 0}
              onTogglePassage={onTogglePassage}
              activePassageId={activePassageId}
            />
          </React.Fragment>
        ))}
      </article>
    </div>
  );
}

// Divider between footages — a § marker with the next footage's label.
function FootageDivider({ footage }) {
  return (
    <div aria-hidden="false" style={{
      display: "flex", alignItems: "center", gap: "12px",
      margin: "40px 0 32px",
    }}>
      <div style={{ flex: 1, height: "1px", background: "var(--line-paper)" }} />
      <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--ink-2)" }}>
        <span style={{ fontFamily: "var(--font-display)", fontStyle: "italic", fontSize: "22px", color: "var(--ink-3)", lineHeight: 1 }}>§</span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--ink-3)" }}>
          footage {footage.order} · {footage.label}
        </span>
      </div>
      <div style={{ flex: 1, height: "1px", background: "var(--line-paper)" }} />
    </div>
  );
}

function FootageSection({ footage, isFirst, onTogglePassage, activePassageId }) {
  // Group passages by speaker run for marginalia.
  const lines = useMemo(() => {
    const out = [];
    let current = null;
    for (const p of footage.passages) {
      if (!current || current.speaker !== p.speaker) {
        current = { speaker: p.speaker, startTime: p.start, passages: [] };
        out.push(current);
      }
      current.passages.push(p);
    }
    return out;
  }, [footage]);

  return (
    <div style={{ fontFamily: "var(--font-body)", fontSize: "19px", lineHeight: 1.78, color: "var(--ink)", textWrap: "pretty" }}>
      {lines.map((line, i) => (
        <TranscriptLine
          key={i}
          line={line}
          isFirst={isFirst && i === 0}
          onToggle={onTogglePassage}
          activeId={activePassageId}
        />
      ))}
    </div>
  );
}

function TranscriptLine({ line, isFirst, onToggle, activeId }) {
  const speakerColor = line.speaker === "Bunting" ? "var(--ink)" : line.speaker === "Interviewer" ? "var(--ink-2)" : "var(--ink-3)";
  return (
    <section style={{
      display: "grid",
      gridTemplateColumns: "92px 1fr 32px",
      gap: "20px",
      marginBottom: "20px",
    }}>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.14em", textTransform: "uppercase", color: speakerColor, paddingTop: isFirst ? "12px" : "8px", textAlign: "right", lineHeight: 1.4 }}>
        {line.speaker}
        <div style={{ color: "var(--ink-3)", marginTop: "4px", letterSpacing: 0, textTransform: "none", fontSize: "10px" }}>
          {fmt(line.startTime)}
        </div>
      </div>

      <p style={{ margin: 0, color: "var(--ink)" }}>
        {line.passages.map((p, i) => (
          <ProsePassage
            key={p.id}
            passage={p}
            onToggle={() => onToggle?.(p.id)}
            active={p.id === activeId}
          />
        ))}
      </p>

      <div />
    </section>
  );
}

function ProsePassage({ passage, onToggle, active }) {
  const text = passage.text;
  let style = {
    padding: "1px 2px", borderRadius: "1px", cursor: "pointer",
    transition: "background var(--dur-1) var(--ease), color var(--dur-1) var(--ease)",
  };
  if (passage.status === "skip") {
    style = { ...style, color: "var(--ink-4)", textDecorationLine: "line-through", textDecorationColor: "var(--vermillion)", textDecorationThickness: "1px" };
  } else if (passage.status === "active" || active) {
    style = { ...style, background: "var(--vermillion-wash)", boxShadow: "inset 0 -2px 0 var(--vermillion)", color: "var(--ink)" };
  }
  return (
    <span
      role="button" tabIndex={0}
      onClick={onToggle}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onToggle?.(); } }}
      style={style}
      title={`${passage.id} · ${passage.status} · click to toggle`}
    >
      {text + " "}
    </span>
  );
}

// =========================================================================
// PLAYER + FOOTAGES — the live preview surface.
// The Footages strip lives directly beneath the player frame, in the same
// panel: there is no separate "media bin" / "timeline".
// =========================================================================
function PlayerSurface({ project, footages, activeFootageId, onSelectFootage, scrub = 0.34 }) {
  const activeFootage = footages.find((f) => f.id === activeFootageId);
  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "14px", padding: "16px", borderBottom: "1px solid var(--line)" }}>
      <Eyebrow>Live preview</Eyebrow>

      {/* Video frame */}
      <div style={{
        position: "relative", aspectRatio: "16 / 9", width: "100%",
        background: "var(--frame)", borderRadius: "2px", overflow: "hidden",
        border: "1px solid var(--line-dark)",
      }}>
        <div style={{
          position: "absolute", inset: 0,
          background: `
            radial-gradient(ellipse at 36% 42%, #3a2e22 0%, transparent 32%),
            radial-gradient(ellipse at 70% 60%, #2d3a3e 0%, transparent 38%),
            linear-gradient(180deg, #1a1714 0%, #0a0908 100%)
          `,
        }} />
        <svg viewBox="0 0 320 180" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} preserveAspectRatio="xMidYMid slice">
          <ellipse cx="120" cy="92" rx="38" ry="44" fill="#2a221a" />
          <path d="M 60 180 Q 60 130 120 130 Q 180 130 180 180 Z" fill="#1c1612" />
        </svg>

        {/* Bottom transport — protection gradient + scrubber */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "10px 12px", background: "linear-gradient(180deg, rgba(15,14,12,0), rgba(15,14,12,0.7))" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--ink-on-dark)" }}>
            <button style={{ background: "transparent", border: 0, padding: 0, cursor: "pointer", color: "#FBF7EB", display: "flex" }}>
              <Icon name="play" size={14} color="#FBF7EB" />
            </button>
            <div style={{ flex: 1, position: "relative", height: "3px", background: "rgba(251,247,235,0.18)", borderRadius: "999px" }}>
              <div style={{ position: "absolute", inset: "0 0 0 0", width: `${scrub * 100}%`, background: "var(--vermillion)", borderRadius: "999px" }} />
              <div style={{ position: "absolute", left: `${scrub * 100}%`, top: "50%", transform: "translate(-50%, -50%)", width: "10px", height: "10px", borderRadius: "999px", background: "#FBF7EB", border: "2px solid var(--vermillion)" }} />
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "#FBF7EB", fontVariantNumeric: "tabular-nums" }}>00:21.7 / 01:04.0</div>
          </div>
        </div>

        <div style={{ position: "absolute", top: "10px", left: "12px", fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.14em", textTransform: "uppercase", color: "rgba(251,247,235,0.7)" }}>
          {activeFootage ? `footage ${activeFootage.order} · ${activeFootage.label}` : "—"}
        </div>
      </div>

      {/* Footages strip — the consolidated timeline + media bin */}
      <FootagesStrip footages={footages} activeFootageId={activeFootageId} onSelect={onSelectFootage} />
    </section>
  );
}

function FootagesStrip({ footages, activeFootageId, onSelect }) {
  const total = footages.reduce((acc, f) => acc + keptSeconds(f), 0);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "8px" }}>
        <Eyebrow style={{ whiteSpace: "nowrap" }}>Footages · {footages.length} in cut · {fmt(total)}</Eyebrow>
        <button style={{
          background: "transparent", border: 0, padding: 0, cursor: "pointer",
          fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-2)",
          display: "inline-flex", alignItems: "center", gap: "4px", whiteSpace: "nowrap", flexShrink: 0,
        }}>
          <Icon name="plus" size={12} /> Add footage
        </button>
      </div>
      <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "2px", minWidth: 0 }}>
        {footages.map((f, i) => (
          <React.Fragment key={f.id}>
            <FootageCard footage={f} active={f.id === activeFootageId} onClick={() => onSelect?.(f.id)} />
            {i < footages.length - 1 && (
              <span style={{ alignSelf: "center", color: "var(--ink-4)", fontFamily: "var(--font-mono)", fontSize: "12px", flexShrink: 0 }}>→</span>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function FootageCard({ footage, active, onClick }) {
  const kept = footage.passages.filter((p) => p.status !== "skip").length;
  const total = footage.passages.length;
  const out = keptSeconds(footage);

  return (
    <button onClick={onClick} style={{
      display: "flex", flexDirection: "column", gap: 0,
      background: "var(--canvas-2)", border: `1px solid ${active ? "var(--vermillion)" : "var(--line-strong)"}`,
      boxShadow: active ? "inset 0 -2px 0 var(--vermillion)" : "none",
      borderRadius: "2px", padding: 0,
      cursor: "pointer", flexShrink: 0, width: "168px",
      fontFamily: "var(--font-mono)", textAlign: "left",
      font: "inherit",
      transition: "border-color var(--dur-1) var(--ease)",
    }}>
      {/* Thumbnail strip */}
      <div style={{
        height: "60px",
        background: `linear-gradient(135deg, #2a221a 0%, #1a1714 60%, #0a0908 100%)`,
        position: "relative", overflow: "hidden",
        borderBottom: `1px solid ${active ? "var(--vermillion)" : "var(--line-strong)"}`,
      }}>
        <svg viewBox="0 0 168 60" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} preserveAspectRatio="xMidYMid slice">
          {footage.label.includes("B-roll") ? (
            <>
              <rect x="0" y="36" width="168" height="24" fill="#1c1612" />
              <line x1="20" y1="40" x2="148" y2="40" stroke="#3a2e22" strokeWidth="1" />
              <line x1="20" y1="48" x2="148" y2="48" stroke="#3a2e22" strokeWidth="1" />
            </>
          ) : (
            <>
              <ellipse cx="58" cy="28" rx="18" ry="22" fill="#2a221a" />
              <path d="M 30 60 Q 30 44 58 44 Q 86 44 86 60 Z" fill="#1c1612" />
            </>
          )}
        </svg>
        <div style={{
          position: "absolute", top: "6px", left: "8px",
          fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.14em", textTransform: "uppercase", color: "rgba(251,247,235,0.7)",
        }}>{footage.order.toString().padStart(2, "0")}</div>
        <div style={{
          position: "absolute", bottom: "6px", right: "8px",
          fontFamily: "var(--font-mono)", fontSize: "10px", color: "rgba(251,247,235,0.7)", fontVariantNumeric: "tabular-nums",
        }}>{footage.duration}</div>
      </div>
      {/* Meta */}
      <div style={{ padding: "8px 10px", display: "flex", flexDirection: "column", gap: "2px" }}>
        <div style={{ fontSize: "12px", color: "var(--ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {footage.label}
        </div>
        <div style={{ fontSize: "10px", color: "var(--ink-3)", display: "flex", justifyContent: "space-between" }}>
          <span>{kept}/{total} kept</span>
          <span style={{ fontVariantNumeric: "tabular-nums" }}>{fmt(out)}</span>
        </div>
      </div>
    </button>
  );
}

// =========================================================================
// AGENT DOCK
// =========================================================================
function AgentDock({ messages, presence, onSend, draft, setDraft }) {
  return (
    <section style={{
      display: "flex", flexDirection: "column", minHeight: 0, flex: 1,
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px 6px", gap: "8px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: 0, flexShrink: 1 }}>
          <StatusDot state={presence === "listening" ? "agent" : presence === "working" ? "live" : "waiting"} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "13px", color: "var(--ink)", fontWeight: 500 }}>agent</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-3)", whiteSpace: "nowrap" }}>· {presence}</span>
        </div>
        <Button variant="quiet" size="sm" icon="more-horizontal" style={{ padding: "4px 6px", flexShrink: 0 }}>{""}</Button>
      </div>

      <div style={{ flex: 1, minHeight: 0, overflow: "auto", padding: "6px 16px 12px", display: "flex", flexDirection: "column", gap: "14px" }}>
        {messages.map((m) => <AgentMessage key={m.id} m={m} />)}
      </div>

      <div style={{ padding: "10px 12px 12px", borderTop: "1px solid var(--line)", background: "var(--canvas-2)" }}>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Note to the agent — e.g. tighten the intro, strike anything before the first &quot;the&quot;."
          rows={2}
          style={{
            width: "100%", boxSizing: "border-box",
            fontFamily: "var(--font-body)", fontSize: "14px", lineHeight: 1.5,
            background: "transparent", border: "1px solid var(--line)",
            borderRadius: "2px", padding: "10px 12px",
            color: "var(--ink)", outline: "none", resize: "none",
          }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", marginTop: "8px" }}>
          <Button variant="agent" size="sm" icon="send" onClick={onSend}>Send</Button>
        </div>
      </div>
    </section>
  );
}

function AgentMessage({ m }) {
  const isAgent = m.author === "agent";
  return (
    <div style={{
      paddingLeft: "12px",
      borderLeft: `2px solid ${isAgent ? "var(--ultramarine)" : "var(--vermillion)"}`,
    }}>
      <div style={{
        fontFamily: "var(--font-mono)", fontSize: "10px",
        letterSpacing: "0.16em", textTransform: "uppercase",
        color: isAgent ? "var(--ultramarine)" : "var(--vermillion)",
        marginBottom: "4px", display: "flex", justifyContent: "space-between", alignItems: "center", gap: "8px",
      }}>
        <span style={{ whiteSpace: "nowrap" }}>↳ {m.author}</span>
        <span style={{ color: "var(--ink-4)", letterSpacing: "0.04em", textTransform: "none", whiteSpace: "nowrap" }}>{m.time}</span>
      </div>
      <div style={{ fontFamily: "var(--font-body)", fontSize: "14px", lineHeight: 1.6, color: "var(--ink)" }}>
        {m.body}
      </div>
    </div>
  );
}

Object.assign(window, { Topbar, Transcript, PlayerSurface, AgentDock });
