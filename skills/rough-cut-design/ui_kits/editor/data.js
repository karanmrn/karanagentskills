// Sample project data for the UI kit demo.
//
// Two concepts, plain and simple:
//
//   FOOTAGE  — the original video file. The thing on disk.
//              Has a label, duration, transcript, and an ordered list of
//              passages.
//
//   PASSAGE  — a speaker segment inside a footage. Has a start, an end, a
//              transcribed text, and a status: keep | skip | active.
//
// The final cut is simply the project's footages in order, each playing
// only the passages that are kept. The timeline = the footages list.

window.RC_DATA = {
  project: {
    id: "20260515-153012-footage",
    title: "Cinema, in two notes",
    duration: "1m 04s",
    lastSaved: "2s ago",
    agentPresence: "listening",
  },

  // Footages in cut order. The first one is "active" (the player is on it).
  footages: [
    {
      id: "ftg_a",
      filename: "interview-bunting.mp4",
      label: "Interview, daylight",
      duration: "04:23",
      durationSec: 263,
      transcribed: true,
      order: 1,
      active: true,
      passages: [
        { id: "p_a1", speaker: "Bunting",     start: 0.4,  end: 4.2,  status: "keep",
          text: "The thing nobody admits about editing on a timeline" },
        { id: "p_a2", speaker: "Bunting",     start: 4.2,  end: 7.8,  status: "keep",
          text: "is that you stop reading the film and start watching the rectangles." },
        { id: "p_a3", speaker: "Bunting",     start: 7.8,  end: 9.4,  status: "skip",
          text: "Um, you know — sort of, yeah, it's —" },
        { id: "p_a4", speaker: "Bunting",     start: 9.4,  end: 13.2, status: "active",
          text: "And the moment you cut by transcript, you remember the cadence." },
        { id: "p_a5", speaker: "Bunting",     start: 13.2, end: 16.0, status: "keep",
          text: "You hear when someone has finished a thought, instead of guessing at it." },
        { id: "p_a6", speaker: "Interviewer", start: 16.0, end: 18.6, status: "keep",
          text: "Like reading a galley before a press run." },
        { id: "p_a7", speaker: "Bunting",     start: 18.6, end: 22.0, status: "keep",
          text: "Exactly. The transcript is the manuscript." },
        { id: "p_a8", speaker: "Bunting",     start: 22.0, end: 24.3, status: "skip",
          text: "I mean, basically — well, kind of." },
      ],
    },
    {
      id: "ftg_b",
      filename: "broll-typecase.mov",
      label: "B-roll, type cases",
      duration: "02:11",
      durationSec: 131,
      transcribed: true,
      order: 2,
      passages: [
        { id: "p_b1", speaker: "VO",      start: 0.0, end: 4.0, status: "keep",
          text: "[ B-roll § type case, hands moving slugs into a chase ]" },
        { id: "p_b2", speaker: "VO",      start: 4.0, end: 7.4, status: "keep",
          text: "[ B-roll § the chase locks, ink on the rollers ]" },
      ],
    },
    {
      id: "ftg_a2",
      filename: "interview-bunting.mp4",
      label: "Interview, return",
      duration: "04:23",
      durationSec: 263,
      transcribed: true,
      order: 3,
      passages: [
        { id: "p_a9",  start: 24.3, end: 28.0, speaker: "Bunting", status: "keep",
          text: "And the agent — it just sits there and waits, like a good copy-editor would." },
        { id: "p_a10", start: 28.0, end: 32.4, speaker: "Bunting", status: "keep",
          text: "It reads your snapshot, proposes a strike, and you decide." },
        { id: "p_a11", start: 32.4, end: 37.0, speaker: "Bunting", status: "keep",
          text: "The render is the press run. ffmpeg does what it's told." },
      ],
    },
  ],

  // Agent chat messages.
  chatMessages: [
    { id: "m1", author: "you",   time: "2 min ago",
      body: "Tighten the intro. Strike anything before the first \"the\"." },
    { id: "m2", author: "agent", time: "2 min ago",
      body: "Polled snapshot. Found two passages before the first \"the\". Striking p_a3 (\"um, you know…\") and trimming p_a1 to begin at 00:00.40." },
    { id: "m3", author: "you",   time: "1 min ago",
      body: "Apply." },
    { id: "m4", author: "agent", time: "1 min ago",
      body: "Done. timeline.json updated. preview is live." },
  ],
};
