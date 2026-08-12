/* global React */
// Inline Lucide-style icons. 24px viewBox, 1.5 stroke, square caps, no fill.
// Drop-in: <Icon name="play" size={16} />

const ICON_PATHS = {
  // navigation / chrome
  "chevron-right":  <polyline points="9 18 15 12 9 6" />,
  "chevron-left":   <polyline points="15 18 9 12 15 6" />,
  "chevron-down":   <polyline points="6 9 12 15 18 9" />,
  "more-horizontal":<><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /><circle cx="5" cy="12" r="1" /></>,
  "x":              <><path d="M18 6 6 18" /><path d="m6 6 12 12" /></>,
  "search":         <><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></>,
  "plus":           <><path d="M12 5v14" /><path d="M5 12h14" /></>,
  "log-out":        <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></>,

  // edit verbs
  "check":          <polyline points="20 6 9 17 4 12" />,
  "scissors":       <><circle cx="6" cy="6" r="3" /><circle cx="6" cy="18" r="3" /><line x1="20" y1="4" x2="8.12" y2="15.88" /><line x1="14.47" y1="14.48" x2="20" y2="20" /><line x1="8.12" y1="8.12" x2="12" y2="12" /></>,
  "chevrons-left-right": <><polyline points="7 7 2 12 7 17" /><polyline points="17 7 22 12 17 17" /></>,
  "arrow-up-down":  <><path d="m21 16-4 4-4-4" /><path d="M17 20V4" /><path d="m3 8 4-4 4 4" /><path d="M7 4v16" /></>,
  "rotate-ccw":     <><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" /></>,
  "trash":          <><path d="M3 6h18" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></>,

  // playback / render
  "play":           <polygon points="6 3 20 12 6 21 6 3" />,
  "pause":          <><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></>,
  "play-circle":    <><circle cx="12" cy="12" r="10" /><polygon points="10 8 16 12 10 16 10 8" /></>,
  "film":           <><rect x="2" y="2" width="20" height="20" rx="2" /><path d="M7 2v20" /><path d="M17 2v20" /><path d="M2 12h20" /><path d="M2 7h5" /><path d="M2 17h5" /><path d="M17 17h5" /><path d="M17 7h5" /></>,
  "skip-back":      <><polygon points="19 20 9 12 19 4 19 20" /><line x1="5" y1="19" x2="5" y2="5" /></>,
  "skip-forward":   <><polygon points="5 4 15 12 5 20 5 4" /><line x1="19" y1="5" x2="19" y2="19" /></>,
  "download":       <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></>,

  // objects
  "file-text":      <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></>,
  "clapperboard":   <><path d="M4 11v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8z" /><path d="m4 11-1-5 19-2 1 5z" /><path d="m7.5 7.5 2 4" /><path d="m12.5 6 2 4" /><path d="m18 5 2 4" /></>,
  "folder-plus":    <><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /><line x1="12" y1="11" x2="12" y2="17" /><line x1="9" y1="14" x2="15" y2="14" /></>,
  "folder":         <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />,

  // agent
  "sparkle":        <path d="M12 3 13.6 9.4 20 11 13.6 12.6 12 19 10.4 12.6 4 11 10.4 9.4z" />,
  "terminal":       <><polyline points="4 17 10 11 4 5" /><line x1="12" y1="19" x2="20" y2="19" /></>,
  "send":           <><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></>,

  // status
  "circle":         <circle cx="12" cy="12" r="10" />,
  "circle-dot":     <><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="2.5" /></>,
  "loader":         <><line x1="12" y1="2" x2="12" y2="6" /><line x1="12" y1="18" x2="12" y2="22" /><line x1="4.93" y1="4.93" x2="7.76" y2="7.76" /><line x1="16.24" y1="16.24" x2="19.07" y2="19.07" /><line x1="2" y1="12" x2="6" y2="12" /><line x1="18" y1="12" x2="22" y2="12" /><line x1="4.93" y1="19.07" x2="7.76" y2="16.24" /><line x1="16.24" y1="7.76" x2="19.07" y2="4.93" /></>,
  "align-left":     <><line x1="21" y1="6" x2="3" y2="6" /><line x1="15" y1="12" x2="3" y2="12" /><line x1="17" y1="18" x2="3" y2="18" /></>,
  "settings":       <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></>,
};

function Icon({ name, size = 16, color = "currentColor", strokeWidth = 1.5, style = {}, className = "" }) {
  const path = ICON_PATHS[name];
  if (!path) return null;
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="square"
      strokeLinejoin="miter"
      className={className}
      style={{ display: "inline-block", flexShrink: 0, ...style }}
      aria-hidden="true"
    >
      {path}
    </svg>
  );
}

Object.assign(window, { Icon });
