export default { content: ['./index.html','./src/**/*.{ts,tsx}'], theme: { extend: {
  colors: { bg:'var(--bg)', surf:'var(--surf)', surf2:'var(--surf2)', line:'var(--line)', ink:'var(--ink)', mute:'var(--mute)', acc:'var(--acc)', onacc:'var(--onacc)', bad:'var(--bad)', ok:'var(--ok)' },
  fontFamily: { sans:['Inter Tight','system-ui','sans-serif'], serif:['Instrument Serif','serif'], mono:['JetBrains Mono','monospace'] } } }, plugins: [] };
