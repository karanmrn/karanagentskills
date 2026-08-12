/* global React, Icon */

// ---------- Button ----------
const buttonStyles = {
  base: {
    fontFamily: "var(--font-mono)",
    fontSize: "13px",
    fontWeight: 500,
    letterSpacing: "-0.005em",
    lineHeight: 1,
    padding: "9px 14px",
    borderRadius: "2px",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    border: "1px solid transparent",
    transition:
      "background var(--dur-1) var(--ease), color var(--dur-1) var(--ease), border-color var(--dur-1) var(--ease), transform var(--dur-1) var(--ease)",
    userSelect: "none",
    textDecoration: "none",
    whiteSpace: "nowrap",
  },
  primary: { background: "var(--ink)", color: "var(--ink-on-dark)", borderColor: "var(--ink)" },
  default: { background: "var(--canvas-2)", color: "var(--ink)", borderColor: "var(--line-strong)" },
  quiet:   { background: "transparent",    color: "var(--ink)", borderColor: "transparent" },
  keep:    { background: "var(--vermillion)", color: "#FBF7EB", borderColor: "var(--vermillion)" },
  skip:    { background: "transparent",    color: "var(--ink)", borderColor: "var(--line-strong)" },
  danger:  { background: "transparent",    color: "var(--danger)", borderColor: "var(--vermillion-soft)" },
  agent:   { background: "var(--ultramarine)", color: "var(--ink-on-dark)", borderColor: "var(--ultramarine)" },
};

function Button({
  variant = "default", icon, iconRight, size = "md", children, style = {}, onClick, disabled, type = "button", ...rest
}) {
  const sizeStyles = size === "sm"
    ? { padding: "6px 10px", fontSize: "12px" }
    : size === "lg"
    ? { padding: "12px 18px", fontSize: "14px" }
    : {};
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        ...buttonStyles.base,
        ...(buttonStyles[variant] || buttonStyles.default),
        ...sizeStyles,
        ...(disabled ? { opacity: 0.4, cursor: "not-allowed" } : {}),
        ...style,
      }}
      {...rest}
    >
      {icon && <Icon name={icon} size={size === "sm" ? 12 : 14} />}
      {children}
      {iconRight && <Icon name={iconRight} size={size === "sm" ? 12 : 14} />}
    </button>
  );
}

// ---------- Pill ----------
function Pill({ tone = "neutral", dot = true, k, v, children, style = {} }) {
  const tones = {
    neutral: { bg: "var(--canvas-2)", border: "var(--line)", dot: "var(--ink-3)" },
    ok:      { bg: "var(--canvas-2)", border: "var(--line)", dot: "var(--ok)" },
    warn:    { bg: "var(--canvas-2)", border: "var(--line)", dot: "var(--caution)" },
    danger:  { bg: "var(--canvas-2)", border: "var(--line)", dot: "var(--danger)" },
    live:    { bg: "var(--canvas-2)", border: "var(--line)", dot: "var(--vermillion)" },
    agent:   { bg: "var(--ultramarine-wash)", border: "var(--ultramarine-soft)", dot: "var(--ultramarine)" },
    keep:    { bg: "var(--vermillion-wash)", border: "var(--vermillion-soft)", dot: "var(--vermillion)", color: "var(--vermillion)" },
  };
  const t = tones[tone] || tones.neutral;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "6px",
      fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 500,
      letterSpacing: "0.04em",
      padding: "4px 10px", borderRadius: "999px",
      background: t.bg, border: `1px solid ${t.border}`,
      color: t.color || "var(--ink)",
      whiteSpace: "nowrap",
      ...style,
    }}>
      {dot && <span style={{ width: "6px", height: "6px", borderRadius: "999px", background: t.dot, flexShrink: 0 }} />}
      {k && <span style={{ color: "var(--ink-3)" }}>{k}</span>}
      {v && <span>{v}</span>}
      {children}
    </span>
  );
}

// ---------- Tag ----------
function Tag({ children, tone = "neutral", style = {} }) {
  const tones = {
    neutral: { bg: "var(--mute-wash)", color: "var(--ink-2)" },
    agent:   { bg: "var(--ultramarine-wash)", color: "var(--ultramarine)" },
    keep:    { bg: "var(--vermillion-wash)", color: "var(--vermillion)" },
  };
  const t = tones[tone] || tones.neutral;
  return (
    <span style={{
      fontFamily: "var(--font-mono)", fontSize: "11px", letterSpacing: "0.04em",
      padding: "3px 6px", borderRadius: "2px",
      background: t.bg, color: t.color,
      ...style,
    }}>{children}</span>
  );
}

// ---------- Hairline ----------
function Hairline({ vertical = false, style = {} }) {
  return (
    <div style={{
      background: "var(--line)",
      ...(vertical ? { width: "1px", alignSelf: "stretch" } : { height: "1px", width: "100%" }),
      ...style,
    }} />
  );
}

// ---------- KeyHint ----------
function KeyHint({ children, style = {} }) {
  return (
    <kbd style={{
      fontFamily: "var(--font-mono)", fontSize: "10px",
      padding: "2px 5px", border: "1px solid var(--line-strong)",
      borderRadius: "2px", background: "var(--canvas-2)", color: "var(--ink-2)",
      letterSpacing: 0, fontWeight: 500,
      ...style,
    }}>{children}</kbd>
  );
}

// ---------- Eyebrow ----------
function Eyebrow({ children, style = {} }) {
  return (
    <div style={{
      fontFamily: "var(--font-mono)", fontSize: "10px",
      letterSpacing: "0.18em", textTransform: "uppercase",
      color: "var(--ink-3)", fontWeight: 500, ...style,
    }}>{children}</div>
  );
}

// ---------- StatusDot ----------
function StatusDot({ state = "neutral", size = 8, style = {} }) {
  const colors = {
    neutral: "var(--ink-3)",
    ok: "var(--ok)",
    warn: "var(--caution)",
    danger: "var(--danger)",
    live: "var(--vermillion)",
    agent: "var(--ultramarine)",
    waiting: "var(--ink-4)",
  };
  return (
    <span style={{
      display: "inline-block",
      width: `${size}px`, height: `${size}px`, borderRadius: "999px",
      background: colors[state] || colors.neutral,
      boxShadow: state === "agent" ? "0 0 0 3px var(--ultramarine-wash)" : "none",
      flexShrink: 0,
      ...style,
    }} />
  );
}

Object.assign(window, { Button, Pill, Tag, Hairline, KeyHint, Eyebrow, StatusDot });
