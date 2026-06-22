/**
 * Voicera Widget — Sonic Architect Rewrite
 * v2.0.0 - Full Production Backend Integration
 */
(function() {
  const STYLE = `
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    :host {
      --bg: #060e20;
      --surface: #0f1930;
      --surface2: #141f38;
      --surface3: #192540;
      --surface4: #1f2b49;
      --border: rgba(222,229,255,0.04);
      --border-hover: rgba(222,229,255,0.1);
      --border-active: rgba(189,157,255,0.3);
      --primary: #bd9dff;
      --primary-dim: #8a4cfc;
      --primary-grad: linear-gradient(135deg,#8a4cfc 0%,#bd9dff 100%);
      --primary-glow: rgba(138,76,252,0.25);
      --green: #4ADE80;
      --red: #ff6e84;
      --amber: #FBBF24;
      --blue: #60A5FA;
      --text-1: #eef0ff;
      --text-2: rgba(238,240,255,0.55);
      --text-3: rgba(238,240,255,0.28);
      --font-h: 'Manrope', sans-serif;
      --font-b: 'Inter', sans-serif;
      --ease: cubic-bezier(0.4, 0, 0.2, 1);
      --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      
      all: initial;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    .trigger {
      position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px;
      background: var(--primary-grad); border: none; border-radius: 50%;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
      z-index: 2147483647; transition: all 0.3s var(--spring);
      box-shadow: 0 4px 24px var(--primary-glow);
    }
    .trigger:hover { transform: scale(1.08); }
    .trigger svg { width: 24px; height: 24px; color: white; }
    .trigger-pulse {
      position: absolute; inset: -4px; border-radius: 50%; border: 2px solid var(--primary);
      opacity: 0; animation: triggerPulse 2.5s ease-out infinite;
    }
    @keyframes triggerPulse {
      0% { transform: scale(0.9); opacity: 0.6; }
      100% { transform: scale(1.4); opacity: 0; }
    }

    .widget {
      position: fixed; bottom: 92px; right: 24px; width: 400px; height: 600px;
      background: var(--surface); border-radius: 24px; border: 1px solid var(--border-hover);
      display: none; flex-direction: column; overflow: hidden; z-index: 2147483646;
      transform: translateY(20px) scale(0.95); opacity: 0;
      transition: all 0.35s var(--spring); font-family: var(--font-b);
      box-shadow: 0 0 0 1px rgba(189,157,255,0.06), 0 32px 80px rgba(0,0,0,0.7);
      top: auto !important;
    }
    .widget.open { display: flex; transform: translateY(0) scale(1); opacity: 1; }

    .hdr {
      display: flex; align-items: center; justify-content: space-between;
      padding: 16px 18px; background: rgba(15,25,48,0.95); backdrop-filter: blur(40px);
      border-bottom: 1px solid var(--border); z-index: 10; flex-shrink: 0;
    }
    .hdr-left { display: flex; align-items: center; gap: 10px; }
    .back-btn, .close-x {
      width: 28px; height: 28px; background: var(--surface2); border: 1px solid var(--border-hover);
      border-radius: 8px; display: flex; align-items: center; justify-content: center;
      cursor: pointer; color: var(--text-3); transition: all 0.18s; flex-shrink: 0;
    }
    .back-btn:hover { background: var(--surface3); color: var(--text-1); }
    .close-x:hover { background: rgba(255,110,132,0.1); border-color: rgba(255,110,132,0.25); color: var(--red); }
    
    .logo-mark {
      width: 32px; height: 32px; background: var(--primary-grad); border-radius: 9px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 2px 12px var(--primary-glow);
    }
    .logo-mark svg { width: 16px; height: 16px; color: white; }
    .hdr-text { display: flex; flex-direction: column; gap: 2px; }
    .hdr-name { display: block; font-family: var(--font-h); font-size: 13px; font-weight: 700; color: #eef0ff; letter-spacing: -0.02em; }
    .hdr-status { display: flex; align-items: center; gap: 4px; font-size: 11px; color: rgba(238,240,255,0.28); }
    .live-dot {
      width: 5px; height: 5px; background: var(--green); border-radius: 50%;
      box-shadow: 0 0 6px var(--green); animation: livePulse 2.5s infinite;
    }
    @keyframes livePulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

    .scr { flex: 1; display: none; flex-direction: column; overflow: hidden; }
    .scr.on { display: flex; animation: fadeIn 0.25s var(--ease) both; }
    @keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

    /* SCREEN 1 */
    .s-channel { padding: 20px 18px; }
    .ch-eyebrow {
      display: inline-flex; align-items: center; gap: 5px; background: rgba(189,157,255,0.08);
      border: 1px solid rgba(189,157,255,0.2); border-radius: 9999px; padding: 3px 10px;
      font-size: 10px; font-weight: 600; color: var(--primary); letter-spacing: 0.06em;
      text-transform: uppercase; margin-bottom: 12px;
    }
    .s-channel h2 { font-family: var(--font-h); font-size: 22px; font-weight: 800; color: var(--text-1); letter-spacing: -0.04em; line-height: 1.15; margin-bottom: 6px; }
    .s-channel p { font-size: 13px; color: var(--text-2); line-height: 1.6; font-weight: 300; margin-bottom: 22px; }
    .ch-options { display: flex; flex-direction: column; gap: 10px; }
    .ch-option {
      background: var(--surface2); border: 1px solid var(--border); border-radius: 16px;
      padding: 16px 18px; cursor: pointer; display: flex; align-items: center; gap: 14px;
      position: relative; overflow: hidden; transition: all 0.25s var(--ease);
    }
    .ch-option::before {
      content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
      border-radius:3px 0 0 3px; opacity:0; transition:opacity 0.2s;
    }
    .ch-option.voice::before { background: var(--primary-grad); }
    .ch-option.chat::before { background: linear-gradient(180deg, var(--green), #22c55e); }
    .ch-option:hover { background: var(--surface3); border-color: var(--border-hover); transform: translateX(2px); }
    .ch-option:hover::before { opacity:1; }
    .ch-option.voice:hover { border-color: rgba(189,157,255,0.25); }
    .ch-option.chat:hover { border-color: rgba(74,222,128,0.25); }
    
    .ch-ico {
      width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    }
    .ch-option.voice .ch-ico { background: rgba(189,157,255,0.1); border: 1px solid rgba(189,157,255,0.2); }
    .ch-option.chat .ch-ico { background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.2); }
    .ch-ico svg { width: 20px; height: 20px; }
    .ch-option.voice .ch-ico svg { color: var(--primary); }
    .ch-option.chat .ch-ico svg { color: var(--green); }
    
    .ch-text h3 { font-family: var(--font-h); font-size: 14px; font-weight: 700; color: var(--text-1); letter-spacing: -0.02em; margin-bottom: 3px; }
    .ch-text p { font-size: 12px; color: var(--text-2); line-height: 1.5; font-weight: 300; }
    .ch-badge { padding: 3px 8px; border-radius: 9999px; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; margin-left: auto; }
    .ch-option.voice .ch-badge { background: rgba(189,157,255,0.1); color: var(--primary); border: 1px solid rgba(189,157,255,0.2); }
    .ch-option.chat .ch-badge { background: rgba(74, 222, 128, 0.1); color: var(--green); border: 1px solid rgba(74, 222, 128, 0.2); }

    .ch-divider { display: flex; align-items: center; gap: 10px; margin: 14px 0 4px; font-size: 11px; color: var(--text-3); }
    .ch-divider::before, .ch-divider::after { content:''; flex:1; height:1px; background: rgba(222,229,255,0.1); }
    .ch-security { display: flex; align-items: center; justify-content: center; gap: 5px; font-size: 11px; color: var(--text-3); margin-top: 16px; }
    .ch-security svg { width: 12px; height: 12px; }

    /* SCREEN 2 — CHAT */
    .s-chat { display: flex; flex-direction: column; flex: 1; min-height: 0; }
    .msgs {
      flex: 1; overflow-y: auto; padding: 16px 16px 8px; display: flex; flex-direction: column; gap: 10px;
      scrollbar-width: thin; scrollbar-color: var(--surface4) transparent;
    }
    .msgs::-webkit-scrollbar { width: 4px; }
    .msgs::-webkit-scrollbar-thumb { background: var(--surface4); border-radius: 10px; }
    .msg { display: flex; gap: 8px; align-items: flex-end; }
    .msg.u { flex-direction: row-reverse; }
    .av {
      width: 26px; height: 26px; flex-shrink: 0; background: var(--primary-grad); border-radius: 8px;
      display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px var(--primary-glow);
    }
    .av svg { width: 12px; height: 12px; color: white; }
    .bbl { max-width: 80%; padding: 9px 13px; font-size: 13px; line-height: 1.6; font-weight: 400; border-radius: 14px; }
    .msg.b .bbl { background: var(--surface2); border: 1px solid rgba(222,229,255,0.1); border-bottom-left-radius: 4px; color: var(--text-1); }
    .msg.u .bbl { background: var(--primary-grad); border-bottom-right-radius: 4px; color: white; box-shadow: 0 2px 12px var(--primary-glow); }
    
    .typing-wrap { display: flex; gap: 8px; align-items: flex-end; }
    .typing-bbl {
      padding: 10px 14px; background: var(--surface2); border: 1px solid rgba(222,229,255,0.1);
      border-radius: 14px; border-bottom-left-radius: 4px; display: flex; gap: 4px; align-items: center;
    }
    .typing-bbl span { width: 5px; height: 5px; background: var(--text-3); border-radius: 50%; animation: tdot 1.2s infinite; }
    .typing-bbl span:nth-child(2) { animation-delay: 0.15s; }
    .typing-bbl span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes tdot { 0%,60%,100%{transform:none;opacity:0.3} 30%{transform:translateY(-5px);opacity:1} }
    
    .help-btns { display: flex; gap: 6px; padding: 0 16px 6px; }
    .help-btn { padding: 6px 14px; border-radius: 9999px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.18s; border: 1px solid; }
    .help-btn.yes { background: rgba(74, 222, 128, 0.08); border-color: rgba(74, 222, 128, 0.25); color: var(--green); }
    .help-btn.no { background: rgba(255, 110, 132, 0.08); border-color: rgba(255, 110, 132, 0.25); color: var(--red); }
    
    .warn-bar, .esc-bar {
      margin: 4px 14px; padding: 8px 12px; border-radius: 10px; display: flex; align-items: flex-start; gap: 8px; font-size: 11.5px; line-height: 1.5;
    }
    .warn-bar { background: rgba(251, 191, 36, 0.07); border: 1px solid rgba(251, 191, 36, 0.2); color: var(--amber); }
    .esc-bar { background: rgba(96, 165, 250, 0.07); border: 1px solid rgba(96, 165, 250, 0.2); color: var(--blue); }
    .warn-bar svg, .esc-bar svg { width: 14px; height: 14px; flex-shrink: 0; margin-top: 1px; }

    .inp-area {
      padding: 10px 14px; border-top: 1px solid var(--border); background: rgba(15, 25, 48, 0.95);
      backdrop-filter: blur(40px); display: flex; gap: 8px; align-items: flex-end;
    }
    .inp {
      flex: 1; min-height: 38px; max-height: 90px; background: var(--surface2); border: 1px solid var(--border-hover);
      border-radius: 10px; padding: 9px 13px; font-family: var(--font-b); font-size: 13px; color: var(--text-1);
      outline: none; resize: none; line-height: 1.45; transition: border-color 0.2s;
    }
    .inp:focus { border-color: rgba(189,157,255,0.4); }
    .send-btn {
      width: 38px; height: 38px; flex-shrink: 0; background: var(--primary-grad); border: none;
      border-radius: 10px; display: flex; align-items: center; justify-content: center;
      cursor: pointer; transition: all 0.18s; box-shadow: 0 2px 10px var(--primary-glow);
    }
    .send-btn svg { width: 15px; height: 15px; color: white; }
    
    .chat-actions { display: flex; align-items: center; justify-content: center; padding: 6px 14px 8px; }
    .end-chat-link { font-size: 11px; color: var(--text-3); cursor: pointer; display: flex; align-items: center; gap: 4px; transition: color 0.18s; }
    .end-chat-link:hover { color: var(--red); }

    /* SCREEN 3 — VOICE */
    .s-voice { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; padding: 24px 20px; position: relative; overflow: hidden; }
    .v-aurora {
      position: absolute; inset: 0; z-index: 0;
      background: radial-gradient(ellipse 70% 50% at 50% 20%, rgba(138,76,252,0.08) 0%, transparent 70%);
    }
    .v-orbit { position: relative; width: 180px; height: 180px; display: flex; align-items: center; justify-content: center; margin-bottom: 28px; z-index: 1; }
    .orbit-ring { position: absolute; border-radius: 50%; border: 1px solid var(--primary); animation: orbitScale 3s infinite; }
    .orbit-ring:nth-child(1) { width: 180px; height: 180px; opacity: 0.06; }
    .orbit-ring:nth-child(2) { width: 140px; height: 140px; opacity: 0.1; animation-delay: 0.4s; }
    .orbit-ring:nth-child(3) { width: 104px; height: 104px; opacity: 0.16; animation-delay: 0.8s; }
    .orbit-ring:nth-child(4) { width: 76px; height: 76px; opacity: 0.22; animation-delay: 1.2s; }
    @keyframes orbitScale { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
    
    .mic-core {
      width: 64px; height: 64px; background: linear-gradient(145deg,#5B4FE9,#8B5CF6,#A78BFA);
      border-radius: 50%; z-index: 2; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 8px 32px rgba(138,76,252,0.5); animation: micPulse 3.5s infinite;
    }
    @keyframes micPulse { 0%,100%{box-shadow: 0 8px 32px rgba(138,76,252,0.5)} 50%{box-shadow: 0 12px 48px rgba(138,76,252,0.7)} }
    .mic-core svg { width: 26px; height: 26px; color: white; }
    
    .v-info { text-align: center; z-index: 1; }
    .v-info h3 { font-family: var(--font-h); font-size: 18px; font-weight: 800; color: var(--text-1); letter-spacing: -0.04em; margin-bottom: 5px; }
    .v-info p { font-size: 12px; color: var(--text-2); font-weight: 300; line-height: 1.5; }
    
    .v-transcript {
      width: 100%; background: var(--surface2); border: 1px solid var(--border-hover);
      border-radius: 10px; padding: 12px 14px; min-height: 50px; margin: 18px 0;
      font-size: 12.5px; color: var(--text-3); font-style: italic; text-align: center;
    }
    
    .end-call {
      background: rgba(255,110,132,0.08); border: 1px solid rgba(255,110,132,0.2);
      border-radius: 9999px; padding: 10px 24px; font-size: 13px; font-weight: 500; color: var(--red);
      cursor: pointer; display: flex; align-items: center; gap: 6px; z-index: 1;
    }
    .end-call svg { width: 14px; height: 14px; }

    /* SCREEN 4 — CALENDAR */
    .s-calendar { padding: 18px 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
    .cal-header h3 { font-family: var(--font-h); font-size: 16px; font-weight: 800; color: var(--text-1); letter-spacing: -0.03em; margin-bottom: 4px; }
    .cal-header p { font-size: 12px; color: var(--text-2); line-height: 1.5; font-weight: 300; }
    .cal-spec { display: flex; align-items: center; gap: 10px; background: var(--surface2); border: 1px solid var(--border-hover); border-radius: 10px; padding: 12px 14px; }
    .spec-av { width: 36px; height: 36px; background: var(--primary-grad); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-family: var(--font-h); font-size: 13px; font-weight: 700; color: white; flex-shrink: 0; }
    .spec-info h4 { font-family: var(--font-h); font-size: 13px; font-weight: 700; color: var(--text-1); letter-spacing: -0.02em; }
    .spec-info p { font-size: 11px; color: var(--text-2); }
    .cal-label { font-size: 10px; font-weight: 600; color: var(--text-3); letter-spacing: 0.07em; text-transform: uppercase; }
    .cal-slot {
      background: var(--surface2); border: 1px solid var(--border-hover); border-radius: 10px; padding: 12px 14px;
      display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.25s var(--ease);
      position: relative; overflow: hidden;
    }
    .cal-slot::before { content:''; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--primary-grad); opacity:0; transition:0.2s; }
    .cal-slot:hover { transform: translateX(2px); border-color: rgba(189,157,255,0.2); }
    .cal-slot:hover::before { opacity:1; }
    .slot-left span { display: block; }
    .slot-day { font-size: 10px; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; }
    .slot-time { font-family: var(--font-h); font-size: 14px; font-weight: 700; color: var(--text-1); }
    .slot-dur { font-size: 11px; color: var(--text-2); }
    .slot-pick {
      padding: 5px 14px; min-width: 70px; background: rgba(189,157,255,0.1); border: 1px solid rgba(189,157,255,0.25);
      border-radius: 9999px; font-size: 11px; font-weight: 600; color: var(--primary); cursor: pointer; flex-shrink: 0;
    }

    /* SCREEN 5 — END */
    .s-end { padding: 20px 18px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
    .end-hero { text-align: center; }
    .end-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; flex-shrink: 0; border: 1px solid; }
    .end-icon.resolved { background: rgba(74,222,128,0.1); border-color: rgba(74,222,128,0.25); color: var(--green); }
    .end-icon.escalated { background: rgba(96,165,250,0.1); border-color: rgba(96,165,250,0.25); color: var(--blue); }
    .end-icon.timeout { background: rgba(251,191,36,0.1); border-color: rgba(251,191,36,0.25); color: var(--amber); }
    .end-icon svg { width: 24px; height: 24px; }
    .end-hero h2 { font-family: var(--font-h); font-size: 20px; font-weight: 800; color: #eef0ff; letter-spacing: -0.04em; margin-bottom: 6px; }
    .end-hero p { font-size: 12.5px; color: rgba(238,240,255,0.55); line-height: 1.6; font-weight: 300; }
    
    .status-badge {
      display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border-radius: 9999px;
      font-size: 10.5px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 10px; border: 1px solid;
    }
    .status-badge.resolved { background: rgba(74,222,128,0.1); border-color: rgba(74,222,128,0.25); color: #4ADE80; }
    .status-badge.escalated { background: rgba(96,165,250,0.1); border-color: rgba(96,165,250,0.25); color: var(--blue); }
    
    .end-card { background: #141f38; border: 1px solid var(--border-hover); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 8px; }
    .end-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .end-label { font-size: 10.5px; font-weight: 600; color: rgba(238,240,255,0.28); letter-spacing: 0.05em; text-transform: uppercase; }
    .end-value { font-size: 13px; color: #eef0ff; font-weight: 500; text-align: right; }
    .end-value.mono { font-family: monospace; font-size: 12px; color: #bd9dff; }
    .sentiment-bar { display: flex; align-items: center; gap: 6px; }
    .sent-dot { width: 8px; height: 8px; border-radius: 50%; }
    .sent-dot.positive { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .sent-dot.neutral { background: var(--amber); box-shadow: 0 0 8px var(--amber); }
    .sent-dot.negative { background: var(--red); box-shadow: 0 0 8px var(--red); }
    .sent-label { font-size: 12px; font-weight: 500; }
    .end-divider { height: 1px; background: rgba(222,229,255,0.1); }
    
    .star-row { display: flex; gap: 4px; }
    .star {
      width: 28px; height: 28px; background: #192540; border: 1px solid rgba(222,229,255,0.1);
      border-radius: 7px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: rgba(238,240,255,0.28);
    }
    .star.active { background: rgba(251,191,36,0.1); border-color: rgba(251,191,36,0.3); color: #FBBF24; }
    .star svg { width: 14px; height: 14px; }
    
    .close-btn-end {
      width: 100%; background: var(--surface2); border: 1px solid var(--border-hover); border-radius: 10px;
      padding: 12px; font-family: var(--font-h); font-size: 13px; font-weight: 700; color: rgba(238,240,255,0.55);
      display: flex; align-items: center; justify-content: center; gap: 6px; cursor: pointer; transition: 0.2s;
    }
    .close-btn-end:hover { background: var(--surface3); color: #eef0ff; }
    .close-btn-end svg { width: 14px; height: 14px; }

    .ftr {
      padding: 12px 0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      border-top: 1px solid var(--border);
      background: var(--surface);
      margin-top: auto;
    }
    .ftr span { font-size: 10px; color: white; font-weight: 500; opacity: 0.8; }
    .ftr strong { font-family: var(--font-h); font-size: 10px; font-weight: 700; color: var(--primary); }

    /* SCREEN 3 — VOICE */
    .s-voice {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      width: 100%;
      position: relative;
      overflow: hidden;
      padding: 30px 18px;
      gap: 20px;
    }
    .v-aurora {
      position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
      width: 300px; height: 300px; background: radial-gradient(circle, rgba(138,76,252,0.15) 0%, transparent 70%);
      filter: blur(40px); z-index: 1; pointer-events: none;
    }
    .v-orbit {
      position: relative; width: 220px; height: 220px; display: flex; align-items: center; justify-content: center; z-index: 2;
    }
    .orbit-ring {
      position: absolute; border: 1px solid rgba(189,157,255,0.08); border-radius: 50%;
      animation: orbitRotate var(--d) linear infinite;
    }
    .orbit-ring:nth-child(1) { width: 100%; height: 100%; --d: 20s; }
    .orbit-ring:nth-child(2) { width: 80%; height: 80%; --d: 15s; border-color: rgba(189,157,255,0.12); }
    .orbit-ring:nth-child(3) { width: 60%; height: 60%; --d: 10s; }
    .orbit-ring:nth-child(4) { width: 40%; height: 40%; --d: 8s; }
    @keyframes orbitRotate { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }

    .mic-core {
      width: 76px; height: 76px; background: var(--primary-grad); border-radius: 50%;
      display: flex; align-items: center; justify-content: center; cursor: pointer;
      box-shadow: 0 0 0 0 rgba(138,76,252,0.4); transition: all 0.3s var(--ease);
      animation: micBreath 3s infinite; position: relative; z-index: 5;
    }
    .mic-core svg { width: 28px; height: 28px; color: white; transition: all 0.3s; }
    .mic-core.recording { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); animation: micPulse 1.2s infinite; }
    .mic-core.recording svg { transform: scale(1.1); }
    
    @keyframes micBreath { 0%,100%{transform:scale(1);box-shadow:0 0 0 0 rgba(138,76,252,0.2)} 50%{transform:scale(1.05);box-shadow:0 0 0 15px rgba(138,76,252,0)} }
    @keyframes micPulse { 0%{box-shadow:0 0 0 0 rgba(239,68,68,0.6)} 70%{box-shadow:0 0 0 20px rgba(239,68,68,0)} 100%{box-shadow:0 0 0 0 rgba(239,68,68,0)} }

    .v-waves { display: flex; align-items: center; gap: 4px; height: 24px; margin-top: 20px; }
    .wave-bar { width: 3px; height: 8px; background: var(--primary); border-radius: 3px; opacity: 0.3; transition: all 0.2s; }
    .recording .wave-bar { opacity: 1; animation: waveAnim 0.6s infinite alternate; }
    .recording .wave-bar:nth-child(2) { animation-delay: 0.1s; }
    .recording .wave-bar:nth-child(3) { animation-delay: 0.2s; }
    .recording .wave-bar:nth-child(4) { animation-delay: 0.3s; }
    .recording .wave-bar:nth-child(5) { animation-delay: 0.4s; }
    @keyframes waveAnim { from{height:8px} to{height:24px} }

    .v-status { font-family: var(--font-h); font-size: 15px; font-weight: 700; color: var(--text-1); margin-top: 10px; }
    .v-transcript { font-size: 12px; color: var(--text-2); text-align: center; max-width: 80%; min-height: 1.5em; font-style: italic; }
    .v-bot-text { font-size: 13px; color: var(--primary); text-align: center; max-width: 90%; background: rgba(189,157,255,0.05); padding: 12px; border-radius: 12px; border: 1px solid rgba(189,157,255,0.1); margin-top: 10px; display: none; }
    .v-bot-text.on { display: block; animation: slideUp 0.3s var(--ease); }
    @keyframes slideUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

    .end-call {
      width: 100%; max-width: 200px; padding: 12px; background: rgba(255,110,132,0.1); border: 1px solid rgba(255,110,132,0.2);
      border-radius: 12px; color: var(--red); font-family: var(--font-h); font-size: 13px; font-weight: 700;
      display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: 0.2s;
    }
    .end-call:hover { background: rgba(255,110,132,0.15); border-color: rgba(255,110,132,0.3); }
    .end-call svg { width: 14px; height: 14px; }

    @media (max-width: 480px) {
      .trigger { bottom: 16px; right: 16px; width: 52px; height: 52px; }
      .widget {
        bottom: 84px; right: 16px; 
        width: calc(100vw - 32px); height: 520px;
        max-height: calc(100vh - 120px);
        border-radius: 20px;
        transform: translateY(10px) scale(0.98);
      }
      .widget.open { transform: translateY(0) scale(1); }
      .hdr { padding: 12px 14px; }
      .s-channel { padding: 20px 16px; }
      .s-channel h2 { font-size: 20px; }
      .ch-option { padding: 12px 14px; }
      .ch-ico { width: 36px; height: 36px; }
      .ch-ico svg { width: 16px; height: 16px; }
      .v-orbit { width: 140px; height: 140px; }
      .mic-core { width: 60px; height: 60px; }
      .mic-core svg { width: 22px; height: 22px; }
    }
  `;

  class VoiceraWidget {
    constructor(config) {
      this.clientId = config.clientId;
      window._voiceraInstance = this;
      this.backendUrl = config.backendUrl;
      this.state = {
        open: false,
        token: null,
        sessionId: null,
        history: [],
        conversationHistory: [],
        startTime: null,
        firstMessage: '',
        ticketId: null,
        nameCollected: false,
        voiceSocket: null,
        voiceKeepAlive: null,
        playCtx: null,
        nextVoiceTime: 0,
        activeVoiceSources: [],
        micStream: null,
        recorder: null,
        userName: '',
        awaitingEmail: false,
        userEmail: null,
        voiceSocket: null,
        audioCtx: null,
        micStream: null,
        recorder: null,
        isRecording: false,
        recordedChunks: [],
        maxRecordingTimer: null
      };
      this.init();
    }

  cleanupVoice() {
    if (this.state.voiceSocket) { try { this.state.voiceSocket.close(); } catch(e){} this.state.voiceSocket = null; }
    if (this.state.voiceKeepAlive) { clearInterval(this.state.voiceKeepAlive); this.state.voiceKeepAlive = null; }
    this.stopVoiceMic();
    this.stopVoicePlayback();
    if (this.state.playCtx) { try { this.state.playCtx.close(); } catch(e){} this.state.playCtx = null; }
    this.state.nextVoiceTime = 0;
  }


    init() {
      this.container = document.createElement('div');
      this.shadow = this.container.attachShadow({ mode: 'open' });
      
      const styleTag = document.createElement('style');
      styleTag.textContent = STYLE;
      this.shadow.appendChild(styleTag);

      this.render();
      document.body.appendChild(this.container);
      this.attachEvents();
    }

    render() {
      this.shadow.innerHTML += `
        <button class="trigger" id="trigger">
          <div class="trigger-pulse"></div>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </button>

        <div class="widget" id="widget">
          <div class="hdr">
            <div class="hdr-left">
              <div class="back-btn" id="backBtn"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg></div>
              <div class="logo-mark"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>
              <div class="hdr-text">
                <div class="hdr-name" id="hdrName">Voicera Support</div>
                <div class="hdr-status"><div class="live-dot"></div>AI online — responds instantly</div>
              </div>
            </div>
            <div class="close-x" id="closeX"><svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
          </div>

          <div class="scr on" id="scrChannel">
            <div class="s-channel">
              <div class="ch-hero">
                <div class="ch-eyebrow"><svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>Instant resolution</div>
                <h2>How can we<br>help you today?</h2>
                <p>Our AI resolves most issues in under 30 seconds. Pick how you'd like to connect.</p>
              </div>
              <div class="ch-options">
                <div class="ch-option voice" id="optVoice">
                  <div class="ch-ico"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/></svg></div>
                  <div class="ch-text"><h3>Voice Call</h3><p>Speak naturally — AI listens and responds in real time</p></div>
                  <span class="ch-badge">Fastest</span>
                </div>
                <div class="ch-divider">or</div>
                <div class="ch-option chat" id="optChat">
                  <div class="ch-ico"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
                  <div class="ch-text"><h3>Live Chat</h3><p>Type your issue and get a response in seconds</p></div>
                  <span class="ch-badge">Available now</span>
                </div>
              </div>
              <div class="ch-security"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>End-to-end encrypted · Your data stays private</div>
            </div>
          </div>

          <div class="scr" id="scrChat">
            <div class="s-chat">
              <div class="msgs" id="msgArea"></div>
              <div id="statusArea"></div>
              <div class="inp-area">
                <textarea class="inp" id="chatInp" placeholder="Type your message..." rows="1"></textarea>
                <button class="send-btn" id="sendBtn"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
              </div>
              <div class="chat-actions"><span class="end-chat-link" id="endChatLink"><svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>End this chat</span></div>
            </div>
          </div>

          <div class="scr" id="scrVoice" style="pointer-events:auto;">
            <div class="s-voice" id="vContainer" style="pointer-events:auto;">
              <div class="v-aurora"></div>
              <div class="v-orbit">
                <div class="orbit-ring"></div><div class="orbit-ring"></div><div class="orbit-ring"></div><div class="orbit-ring"></div>
                <div class="mic-core" id="micBtn" style="cursor:pointer;z-index:999;position:relative;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/></svg></div>
              </div>
              <div class="v-waves">
                <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
              </div>
              <div class="v-status" id="vStatus">Tap to speak</div>
              <div class="v-transcript" id="vTranscript"></div>
              <div class="v-bot-text" id="vBotText"></div>
              <button class="end-call" id="endVoiceBtn" onclick="window._voiceraInstance.handleEndCall()" style="margin-top: 24px"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>End Call</button>
            </div>
          </div>

          <div class="scr" id="scrCalendar">
            <div style="padding:16px;display:flex;flex-direction:column;gap:12px;height:100%;overflow-y:auto;">
              
              <!-- Step 1: Choose Specialist -->
              <div id="voicera-step1">
                <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:10px;">Choose a Specialist</div>
                <div id="voicera-specialists" style="display:flex;flex-direction:column;gap:8px;"></div>
              </div>
              
              <!-- Step 2: Choose Date -->
              <div id="voicera-step2" style="display:none;">
                <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:10px;">Choose a Date</div>
                <div id="voicera-calendar-grid" style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:12px;">
                  <!-- Days header -->
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Mon</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Tue</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Wed</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Thu</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Fri</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Sat</div>
                  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;">Sun</div>
                </div>
                <div id="voicera-slots-for-date" style="display:none;">
                  <div style="font-size:12px;font-weight:600;color:#a78bfa;margin-bottom:8px;" id="voicera-selected-date-label"></div>
                  <div id="voicera-time-slots" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;"></div>
                </div>
              </div>
              
              <!-- Step 3: Your Details -->
              <div id="voicera-step3" style="display:none;">
                <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:10px;">Your Details</div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                  <input id="voicera-book-name" placeholder="Your name" autocomplete="name"
                    style="padding:10px 12px;border:1px solid rgba(255,255,255,0.2);border-radius:8px;font-size:13px;background:rgba(255,255,255,0.08);color:#fff;outline:none;-webkit-text-fill-color:#fff;">
                  <input id="voicera-book-email" placeholder="Your email" type="email" autocomplete="email"
                    style="padding:10px 12px;border:1px solid rgba(255,255,255,0.2);border-radius:8px;font-size:13px;background:rgba(255,255,255,0.08);color:#fff;outline:none;-webkit-text-fill-color:#fff;">
                  <div id="voicera-booking-summary" style="padding:10px;background:rgba(109,40,217,0.2);border-radius:8px;font-size:11px;color:rgba(255,255,255,0.7);"></div>
                  <button id="voicera-confirm-btn"
                    style="padding:12px;background:linear-gradient(135deg,#6D28D9,#4F46E5);color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;letter-spacing:0.3px;">
                    Confirm Booking
                  </button>
                </div>
              </div>
              
              <!-- Success -->
              <div id="voicera-booking-success" style="display:none;text-align:center;padding:30px 20px;">
                <div style="width:56px;height:56px;background:rgba(52,211,153,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:24px;">✓</div>
                <div style="font-size:15px;font-weight:700;color:#34d399;margin-bottom:8px;">Call Scheduled!</div>
                <div style="font-size:12px;color:rgba(255,255,255,0.5);line-height:1.5;">Check your email for the Google Meet link and calendar invite.</div>
              </div>
              
              <button id="voicera-cancel-booking"
                style="padding:8px;background:transparent;border:1px solid rgba(255,255,255,0.15);border-radius:8px;font-size:12px;color:rgba(255,255,255,0.5);cursor:pointer;margin-top:auto;">
                Continue chatting instead
              </button>
            </div>
          </div>

          <div class="scr" id="scrEnd" style="background:#0f1930">
            <div class="s-end">
              <div class="end-hero">
                <div class="end-icon" id="endIcon"></div>
                <div class="end-title" id="endTitle" style="color:#eef0ff;font-family:Manrope,sans-serif;font-size:20px;font-weight:800;text-align:center;letter-spacing:-0.04em;margin-bottom:6px"></div>
                <div class="end-sub" id="endSub" style="color:rgba(238,240,255,0.55);font-size:12.5px;text-align:center;line-height:1.6;font-weight:300"></div>
                <div class="status-badge" id="statusBadge"></div>
              </div>
              <div class="end-card" id="endSummaryCard" style="background:#141f38;border:1px solid rgba(222,229,255,0.1);border-radius:10px;padding:14px"></div>
              <div class="end-card" style="background:#141f38;border:1px solid rgba(222,229,255,0.1);border-radius:10px;padding:14px">
                <div class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:8px">Rate your experience</div>
                <div class="star-row" id="starRow">
                  ${[1,2,3,4,5].map(n => `<div class="star" data-v="${n}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>`).join('')}
                </div>
              </div>
              <button class="close-btn-end" id="closeEndBtn" style="color:rgba(238,240,255,0.55);background:#141f38;border:1px solid rgba(222,229,255,0.1);width:100%;border-radius:10px;padding:12px;font-family:Manrope;font-size:13px;font-weight:700;cursor:pointer"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>Close chat</button>
            </div>
          </div>

          <div class="ftr"><span>Powered by</span><strong>Voicera</strong></div>
        </div>
      `;
    }

    attachEvents() {
      const get = (id) => this.shadow.getElementById(id);
      get('trigger').onclick = () => this.toggle();
      get('closeX').onclick = () => { this.toggle(); this.cleanupVoice(); };
      get('backBtn').onclick = () => { this.goBack(); this.cleanupVoice(); };
      get('optChat').onclick = () => this.goToChat();
      get('optVoice').onclick = () => this.goToVoice();
      get('sendBtn').onclick = () => this.sendMsg();
      get('endChatLink').onclick = () => this.goToEnd('resolved');
      get('closeEndBtn').onclick = () => this.reset();
      get('chatInp').onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMsg();
        }
      };
      get('chatInp').oninput = (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 90) + 'px';
      };
      this.shadow.querySelectorAll('.star').forEach(s => {
        s.onclick = () => this.rate(parseInt(s.dataset.v));
      });
    }

    toggle() {
      this.state.open = !this.state.open;
      const w = this.shadow.getElementById('widget');
      const t = this.shadow.getElementById('trigger');
      if (this.state.open) {
        w.classList.add('open');
        t.style.transform = 'scale(0)';
      } else {
        w.classList.remove('open');
        t.style.transform = 'scale(1)';
      }
    }

    switchScreen(id) {
      this.shadow.querySelectorAll('.scr').forEach(s => s.classList.remove('on'));
      this.shadow.getElementById(id).classList.add('on');
    }

    goBack() {
      if (this.state.history.length) {
        const prev = this.state.history.pop();
        this.switchScreen(prev);
        if (this.state.history.length === 0) {
          this.shadow.getElementById('backBtn').style.display = 'none';
          this.shadow.getElementById('hdrName').textContent = 'Voicera Support';
        }
      }
    }

  async goToVoice() {
    this.state.history.push('scrChannel');
    this.shadow.getElementById('backBtn').style.display = 'flex';
    this.shadow.getElementById('hdrName').textContent = 'Voice Support';
    this.switchScreen('scrVoice');
    const status = this.shadow.getElementById('vStatus');
    const botText = this.shadow.getElementById('vBotText');
    const transcript = this.shadow.getElementById('vTranscript');
    status.textContent = 'Starting microphone...';
    if (botText) { botText.classList.remove('on'); botText.textContent = ''; }
    if (transcript) transcript.textContent = '';
    try {
      // Fetch bot config for dynamic voice prompt
      let voiceSystemPrompt = `You are a helpful AI customer support assistant. Be warm and concise. Keep responses to 1-2 sentences. If you cannot help, say you will connect them with a specialist.`;
      let voiceGreeting = 'Hi! How can I help you today?';
      let voiceModel = 'aura-asteria-en';
      
      try {
        const cfgRes = await fetch(`${this.backendUrl}/api/v1/bot-config/public?client_id=${this.clientId}`);
        if (cfgRes.ok) {
          const cfgData = await cfgRes.json();
          const cfg = cfgData.config || {};
          const botName = cfg.bot_name || 'AI Assistant';
          voiceGreeting = cfg.voice_greeting || cfg.default_greeting || `Hi! I am ${botName}. How can I help you today?`;
          voiceModel = cfg.voice_model || 'aura-asteria-en';
          if (cfg.system_prompt) {
            voiceSystemPrompt = `${cfg.system_prompt}\n\nBEHAVIOR RULES:\n- This is a voice call. Keep ALL responses to 1-2 sentences maximum.\n- Greet the user by saying: ${voiceGreeting}\n- When a customer asks a question about products, policies, pricing, or company information, ALWAYS call the search_knowledge_base function first before answering.\n- Use the function result to give accurate answers.\n- Do not guess or make up answers.\n- Only offer to connect with a specialist if the knowledge base has absolutely nothing relevant.`;
          } else {
            voiceSystemPrompt = `You are ${botName}, a helpful AI customer support assistant.\n\nBEHAVIOR RULES:\n- This is a voice call. Keep ALL responses to 1-2 sentences maximum.\n- Greet the user by saying: ${voiceGreeting}\n- When a customer asks a question about products, policies, pricing, or company information, ALWAYS call the search_knowledge_base function first before answering.\n- Use the function result to give accurate answers.\n- Do not guess or make up answers.\n- Only offer to connect with a specialist if the knowledge base has absolutely nothing relevant.`;
          }
        }
      } catch(e) {
        console.error('Voice config fetch error:', e);
      }

      // Fetch KB summary to inject into voice prompt
      let kbSummary = '';
      try {
        const kbRes = await fetch(`${this.backendUrl}/api/v1/kb/summary?client_id=${this.clientId}`);
        if (kbRes.ok) {
          const kbData = await kbRes.json();
          kbSummary = kbData.summary || '';
        }
      } catch(e) {
        console.error('KB summary fetch error:', e);
      }

      // Add KB content to voice system prompt
      if (kbSummary) {
        voiceSystemPrompt = voiceSystemPrompt + `\n\nKNOWLEDGE BASE:\n${kbSummary}\n\nUse the above knowledge base to answer customer questions accurately.`;
      }

      await this.startVoiceMic();
      if (!this.state.micStream) { status.textContent = 'Microphone access needed.'; return; }
      const tokenRes = await fetch(`${this.backendUrl}/api/v1/voice/token`);
      const { token } = await tokenRes.json();
      if (!token) { status.textContent = 'Failed to get token.'; return; }
      status.textContent = 'Connecting...';
      const dgUrl = 'wss://agent.deepgram.com/v1/agent/converse';
      this.state.voiceSocket = new WebSocket(dgUrl, ['token', token]);
      this.state.voiceSocket.binaryType = 'arraybuffer';
      this.state.voiceSocket.onclose = (e) => {
        console.log('Voice closed:', e.code, e.reason);
        this.stopVoiceMic();
        if (this.state.voiceKeepAlive) { clearInterval(this.state.voiceKeepAlive); this.state.voiceKeepAlive = null; }
        const scrVoice = this.shadow.getElementById('scrVoice');
        if (scrVoice && scrVoice.classList.contains('on')) {
          this.shadow.getElementById('vStatus').textContent = 'Call ended.';
        }
      };
      this.state.voiceSocket.onerror = (e) => { console.error('Voice error:', e); };
      this.state.voiceSocket.onopen = () => {
        console.log('Deepgram connected');
        this.state.voiceSocket.send(JSON.stringify({
          type: 'Settings',
          audio: {
            input: { encoding: 'linear16', sample_rate: 16000 },
            output: { encoding: 'linear16', sample_rate: 16000 }
          },
          agent: {
            listen: { provider: { type: 'deepgram', model: 'nova-3', smart_format: true } },
            think: {
              provider: { type: 'open_ai', model: 'gpt-4o-mini' },
              prompt: voiceSystemPrompt,
              functions: [
                {
                  name: "search_knowledge_base",
                  description: "Search the knowledge base to answer customer questions about products, policies, pricing, and other company information.",
                  parameters: {
                    type: "object",
                    properties: {
                      query: {
                        type: "string",
                        description: "The customer's question to search for in the knowledge base"
                      }
                    },
                    required: ["query"]
                  }
                }
              ]
            },
            speak: { provider: { type: 'deepgram', model: voiceModel } }
          }
        }));
        this.state.voiceKeepAlive = setInterval(() => {
          if (this.state.voiceSocket && this.state.voiceSocket.readyState === WebSocket.OPEN) {
            this.state.voiceSocket.send(JSON.stringify({ type: 'KeepAlive' }));
          }
        }, 5000);
        if (this.state.recorder) {
          this.state.recorder.onaudioprocess = (e) => {
            if (!this.state.voiceSocket || this.state.voiceSocket.readyState !== WebSocket.OPEN) return;
            const f32 = e.inputBuffer.getChannelData(0);
            const i16 = new Int16Array(f32.length);
            for (let i = 0; i < f32.length; i++) {
              const s = Math.max(-1, Math.min(1, f32[i]));
              i16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            this.state.voiceSocket.send(i16.buffer);
          };
        }
        status.textContent = 'Listening...';
      };
      this.state.voiceSocket.onmessage = async (e) => {
        if (e.data instanceof ArrayBuffer) {
          await this.playVoiceAudio(e.data);
        } else {
          const data = JSON.parse(e.data);
          
          // Handle function calls from Deepgram
          if (data.type === 'FunctionCallRequest') {
            const funcName = data.function_name;
            const params = data.input || {};
            
            if (funcName === 'search_knowledge_base') {
              try {
                const searchRes = await fetch(`${this.backendUrl}/api/v1/voice-kb/search`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    client_id: this.clientId,
                    query: params.query || ''
                  })
                });
                const searchData = await searchRes.json();
                
                // Send function result back to Deepgram
                this.state.voiceSocket.send(JSON.stringify({
                  type: 'FunctionCallResponse',
                  function_call_id: data.function_call_id,
                  output: searchData.result || 'No information found.'
                }));
              } catch(e) {
                this.state.voiceSocket.send(JSON.stringify({
                  type: 'FunctionCallResponse',
                  function_call_id: data.function_call_id,
                  output: 'Unable to search knowledge base right now.'
                }));
              }
            }
          }
          if (data.type === 'ConversationText') {
            if (data.role !== 'assistant' && transcript) transcript.textContent = '🎤 ' + data.content;
            if (data.role === 'assistant' && botText) { 
              botText.textContent = data.content; 
              botText.classList.add('on');
              const escalationPhrases = ['connect you to a specialist', 'transfer you', 'human agent', 'book a call', 'schedule a call', 'specialist will', 'connecting you'];
              const shouldEscalate = escalationPhrases.some(p => data.content.toLowerCase().includes(p));
              if (shouldEscalate) {
                setTimeout(() => {
                  this.cleanupVoice();
                  this.goToCalendar();
                }, 3000);
              }
            }
          }
          if (data.type === 'AgentStartedSpeaking') status.textContent = 'Speaking...';
          if (data.type === 'AgentAudioDone') status.textContent = 'Listening...';
          if (data.type === 'UserStartedSpeaking') { status.textContent = 'Listening...'; this.stopVoicePlayback(); }
        }
      };
      this.shadow.getElementById('endVoiceBtn').onmousedown = () => { this.cleanupVoice(); this.goBack(); };
    } catch(e) {
      console.error('Voice error:', e);
      status.textContent = 'Failed to connect. Please try again.';
    }
  }

  async startVoiceMic() {
    try {
      this.state.micStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 16000, echoCancellation: true, noiseSuppression: true }, video: false });
      const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      await ctx.resume();
      const source = ctx.createMediaStreamSource(this.state.micStream);
      this.state.recorder = ctx.createScriptProcessor(4096, 1, 1);
      const muteNode = ctx.createGain();
      muteNode.gain.value = 0;
      this.state.recorder.onaudioprocess = null;
      source.connect(this.state.recorder);
      this.state.recorder.connect(muteNode);
      muteNode.connect(ctx.destination);
      this.state.voiceAudioCtx = ctx;
    } catch(e) {
      console.error('Mic error:', e);
      this.state.micStream = null;
    }
  }

  stopVoiceMic() {
    if (this.state.recorder) { this.state.recorder.disconnect(); this.state.recorder = null; }
    if (this.state.micStream) { this.state.micStream.getTracks().forEach(t => t.stop()); this.state.micStream = null; }
    if (this.state.voiceAudioCtx) { try { this.state.voiceAudioCtx.close(); } catch(e){} this.state.voiceAudioCtx = null; }
  }

  async playVoiceAudio(arrayBuffer) {
    try {
      const i16 = new Int16Array(arrayBuffer);
      if (!i16.length) return;
      if (!this.state.playCtx) this.state.playCtx = new AudioContext({ sampleRate: 16000 });
      if (this.state.playCtx.state === 'suspended') await this.state.playCtx.resume();
      const f32 = new Float32Array(i16.length);
      for (let i = 0; i < i16.length; i++) f32[i] = i16[i] / 32768.0;
      const buf = this.state.playCtx.createBuffer(1, f32.length, 16000);
      buf.copyToChannel(f32, 0);
      const src = this.state.playCtx.createBufferSource();
      src.buffer = buf;
      src.connect(this.state.playCtx.destination);
      const now = this.state.playCtx.currentTime;
      const startAt = Math.max(now + 0.04, this.state.nextVoiceTime);
      src.start(startAt);
      this.state.nextVoiceTime = startAt + buf.duration;
      this.state.activeVoiceSources.push(src);
      src.onended = () => { this.state.activeVoiceSources = this.state.activeVoiceSources.filter(s => s !== src); };
    } catch(e) { console.error('Audio playback error:', e); }
  }

  stopVoicePlayback() {
    this.state.activeVoiceSources.forEach(s => { try { s.stop(); s.disconnect(); } catch(e){} });
    this.state.activeVoiceSources = [];
    this.state.nextVoiceTime = 0;
  }

    async goToChat() {
      this.state.history.push('scrChannel');
      this.shadow.getElementById('backBtn').style.display = 'flex';
      this.shadow.getElementById('hdrName').textContent = this.botName || 'Live Chat';
      this.switchScreen('scrChat');
      this.state.startTime = new Date();
      
      this.shadow.getElementById('msgArea').innerHTML = '';
      this.shadow.getElementById('statusArea').innerHTML = '';
      
      // Fetch bot config and use dynamic greeting
      try {
        const configRes = await fetch(`${this.backendUrl}/api/v1/bot-config/public?client_id=${this.clientId}`);
        if (configRes.ok) {
          const configData = await configRes.json();
          const config = configData.config || {};
          this.botName = config.bot_name || 'Voicera AI';
          this.botGreeting = config.chat_greeting || config.default_greeting || 'Hi! How can I help you today?';
          this.escalationKeywords = (config.escalation_keywords || 'speak to human,agent,specialist').split(',').map(k => k.trim().toLowerCase());
          
          // Update header with bot name
          const hdrName = this.shadow.getElementById('hdrName');
          if (hdrName) hdrName.textContent = this.botName;
        } else {
          this.botGreeting = 'Hi! How can I help you today?';
          this.escalationKeywords = ['speak to human', 'agent', 'specialist'];
        }
      } catch(e) {
        this.botGreeting = 'Hi! How can I help you today?';
        this.escalationKeywords = ['speak to human', 'agent', 'specialist'];
      }
      
      this.addMsg(this.botGreeting, 'b');
      
      try {
        const loginRes = await fetch(`${this.backendUrl}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com', password: 'password123' })
        });
        const loginData = await loginRes.json();
        this.state.token = loginData.access_token;
      } catch (e) {
        console.error(e);
        this.addMsg("Something went wrong. Please try again.", 'b');
      }
    }

    async startSession(userName) {
      const res = await fetch(`${this.backendUrl}/api/v1/sessions/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.state.token}`
        },
        body: JSON.stringify({
          client_id: this.clientId,
          user_email: 'guest@voicera.ai',
          user_name: userName || 'Guest',
          channel: 'chat'
        })
      });
      const data = await res.json();
      this.state.sessionId = data.session_id;
    }

    async sendMsg() {
      const inp = this.shadow.getElementById('chatInp');
      const msg = inp.value.trim();
      if (!msg) return;

      if (this.state.awaitingEmail) {
        this.state.awaitingEmail = false;
        this.addMsg(msg, 'u');
        inp.value = '';
        
        const skipWords = ['skip','no','nope','dont','nah'];
        const hasEmail = msg.includes('@');
        
        if (hasEmail) {
          this.state.userEmail = msg.trim();
          setTimeout(() => {
            this.addMsg('Perfect! Summary will be sent to ' + this.state.userEmail + '. Here is your session summary.', 'b');
            setTimeout(() => this.resolveAndEnd(), 800);
          }, 400);
        } else if (skipWords.some(w => msg.toLowerCase().includes(w))) {
          setTimeout(() => {
            this.addMsg('No problem! Here is your session summary.', 'b');
            setTimeout(() => this.resolveAndEnd(), 800);
          }, 400);
        } else {
          setTimeout(() => {
            this.addMsg('That does not look like an email address. Type your email or type skip to continue.', 'b');
            this.state.awaitingEmail = true;
          }, 400);
        }
        return;
      }

      if (['close','bye','goodbye','exit','end chat','quit','stop'].some(w => msg.toLowerCase().includes(w))) {
        this.resolveAndEnd();
        return;
      }

      this.addMsg(msg, 'u');
      inp.value = '';
      inp.style.height = 'auto';

      if (this.state.sessionId === null) {
        await this.startSession('Guest');
      }

      if (!this.state.firstMessage) {
        this.state.firstMessage = msg;
      }

      this.state.conversationHistory.push({ role: 'user', content: msg });
      
      this.showTyping();
      
      try {
        const res = await fetch(`${this.backendUrl}/api/v1/chat/message`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + this.state.token
          },
          body: JSON.stringify({
            session_id: this.state.sessionId,
            client_id: this.clientId,
            message: msg,
            conversation_history: this.state.conversationHistory
          })
        });
        const data = await res.json();
        this.removeTyping();
        this.addMsg(data.response, 'b');
        this.state.conversationHistory.push({ role: 'assistant', content: data.response });
        
        const escalationKeywords = this.escalationKeywords || ['speak to human', 'agent', 'specialist', 'human', 'call me'];
        const userText = (msg || '').toLowerCase();
        const shouldShowBooking = escalationKeywords.some(kw => userText.includes(kw)) || data.should_escalate;
        
        if (shouldShowBooking && !this.shadow.getElementById('voicera-booking')) {
          setTimeout(() => showBookingUI(), 500);
        }

        if (data.confident) this.showHelpBtns();
        if (data.should_escalate) {
          this.showEscalation();
          this.showHelpBtns();
        }
      } catch (e) {
        this.removeTyping();
        this.addMsg('Something went wrong. Please try again.', 'b');
      }
    }

    addMsg(text, type) {
      const area = this.shadow.getElementById('msgArea');
      const div = document.createElement('div');
      div.className = `msg ${type}`;
      div.innerHTML = type === 'b' ? `
        <div class="av"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>
        <div class="bbl">${text}</div>
      ` : `<div class="bbl">${text}</div>`;
      area.appendChild(div);
      area.scrollTop = area.scrollHeight;
      this.shadow.getElementById('statusArea').innerHTML = '';
    }

    showTyping() {
      const area = this.shadow.getElementById('msgArea');
      const div = document.createElement('div');
      div.className = 'typing-wrap'; div.id = 'typing';
      div.innerHTML = `<div class="av"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div><div class="typing-bbl"><span></span><span></span><span></span></div>`;
      area.appendChild(div); area.scrollTop = area.scrollHeight;
    }
    removeTyping() { const t = this.shadow.getElementById('typing'); if (t) t.remove(); }
    showHelpBtns() {
      const area = this.shadow.getElementById('statusArea');
      area.innerHTML = `<div class="help-btns"><button class="help-btn yes" id="hYes">✓ That helped</button><button class="help-btn no" id="hNo">✗ Still need help</button></div>`;
      this.shadow.getElementById('hYes').onclick = () => {
        this.addMsg("Glad I could help! Would you like a summary sent to your email? Type your email or type skip to continue.", 'b');
        this.state.awaitingEmail = true;
      };
      this.shadow.getElementById('hNo').onclick = () => this.goToCalendar();
    }

    showEscalation() {
      const area = this.shadow.getElementById('statusArea');
      area.innerHTML = `
        <div class="esc-bar">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div>
            <strong>Let me connect you with a specialist.</strong><br>
            Our team has full context of this conversation. Use the button below to book a direct call.
          </div>
        </div>
      `;
    }

    async goToCalendar() {
      this.state.history.push('scrChat');
      this.shadow.getElementById('hdrName').textContent = 'Book a call';
      this.switchScreen('scrCalendar');
      await this.loadSpecialistsInWidget();
    }

    async loadSpecialistsInWidget() {
      const container = this.shadow.getElementById('voicera-specialists');
      if (!container) return;

      try {
        const res = await fetch(`${this.backendUrl}/api/v1/auth/team/public?client_id=${this.clientId}`);
        const data = await res.json();
        const members = data.members || [];

        if (!members.length) {
          container.innerHTML = '<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;text-align:center;">No specialists available right now.<br>We\'ll get back to you soon.</div>';
          return;
        }

        const colors = ['#6D28D9','#1D4ED8','#047857','#B45309','#9D174D'];
        container.innerHTML = members.map(m => {
          const initials = (m.full_name || m.email).charAt(0).toUpperCase();
          const color = colors[m.email.charCodeAt(0) % colors.length];
          return `
            <div data-spec-id="${m.id}" data-spec-name="${m.full_name || m.email}"
              style="display:flex;align-items:center;gap:10px;padding:12px;border:1px solid rgba(255,255,255,0.12);border-radius:10px;cursor:pointer;transition:all 0.2s;">
              <div style="width:36px;height:36px;border-radius:50%;background:${color};color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0;">${initials}</div>
              <div style="flex:1;">
                <div style="font-size:13px;font-weight:600;color:#fff;">${m.full_name || m.email}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.45);">${m.department || 'Support Specialist'}</div>
              </div>
              <div style="font-size:20px;color:rgba(255,255,255,0.3);">›</div>
            </div>
          `;
        }).join('');

        container.querySelectorAll('[data-spec-id]').forEach(el => {
          el.onclick = () => this.selectSpecialistInWidget(el.dataset.specId, el.dataset.specName, el);
        });

        // Wire cancel button
        const cancelBtn = this.shadow.getElementById('voicera-cancel-booking');
        if (cancelBtn) cancelBtn.onclick = () => this.switchScreen('scrChat');
      } catch(e) {
        container.innerHTML = '<div style="font-size:12px;color:rgba(255,255,255,0.5);">Failed to load specialists</div>';
      }
    }

    async selectSpecialistInWidget(specialistId, specialistName, el) {
      this._selectedSpecialistId = specialistId;
      this._selectedSpecialistName = specialistName;
      this._allSlots = [];

      // Highlight selected specialist
      this.shadow.querySelectorAll('[data-spec-id]').forEach(d => {
        d.style.borderColor = 'rgba(255,255,255,0.12)';
        d.style.background = 'transparent';
      });
      el.style.borderColor = '#6D28D9';
      el.style.background = 'rgba(109,40,217,0.15)';

      // Show step 2
      this.shadow.getElementById('voicera-step2').style.display = 'block';
      const calGrid = this.shadow.getElementById('voicera-calendar-grid');

      try {
        const res = await fetch(`${this.backendUrl}/api/v1/calendar/slots/${specialistId}`);
        const data = await res.json();
        const slots = data.slots || data || [];
        this._allSlots = slots;

        // Group slots by date
        const byDate = {};
        slots.forEach(slot => {
          const d = new Date(slot.start);
          const key = d.toISOString().split('T')[0];
          if (!byDate[key]) byDate[key] = [];
          byDate[key].push(slot);
        });

        // Build 7-day calendar starting from today
        const today = new Date();
        today.setHours(0,0,0,0);
        
        // Keep the day headers (first 7 children)
        const headers = Array.from(calGrid.children).slice(0, 7);
        calGrid.innerHTML = '';
        headers.forEach(h => calGrid.appendChild(h));

        // Find the Monday of current week
        const dayOfWeek = today.getDay(); // 0=Sun
        const monday = new Date(today);
        monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));

        for (let i = 0; i < 14; i++) {
          const date = new Date(monday);
          date.setDate(monday.getDate() + i);
          const key = date.toISOString().split('T')[0];
          const hasSlots = byDate[key] && byDate[key].length > 0;
          const isToday = date.toDateString() === new Date().toDateString();
          const isPast = date < today;

          const dayEl = document.createElement('div');
          dayEl.style.cssText = `
            text-align:center;padding:6px 2px;border-radius:6px;font-size:12px;cursor:${hasSlots && !isPast ? 'pointer' : 'default'};
            background:${isToday ? 'rgba(109,40,217,0.3)' : 'transparent'};
            color:${isPast ? 'rgba(255,255,255,0.2)' : hasSlots ? '#fff' : 'rgba(255,255,255,0.3)'};
            border:1px solid ${hasSlots && !isPast ? 'rgba(109,40,217,0.4)' : 'transparent'};
            font-weight:${hasSlots && !isPast ? '600' : '400'};
          `;
          dayEl.textContent = date.getDate();
          
          if (hasSlots && !isPast) {
            dayEl.dataset.dateKey = key;
            dayEl.dataset.dateSlots = JSON.stringify(byDate[key]);
            dayEl.onclick = () => this.showSlotsForDate(key, byDate[key], dayEl, date);
          }
          calGrid.appendChild(dayEl);
        }

      } catch(e) {
        calGrid.innerHTML += '<div style="font-size:11px;color:rgba(255,255,255,0.4);grid-column:1/-1;padding:8px;">Failed to load calendar</div>';
      }
    }

    showSlotsForDate(dateKey, slots, clickedEl, dateObj) {
      this._selectedDate = dateKey;

      // Highlight selected date
      this.shadow.querySelectorAll('[data-date-key]').forEach(d => {
        d.style.background = 'transparent';
        d.style.borderColor = 'rgba(109,40,217,0.4)';
      });
      clickedEl.style.background = 'rgba(109,40,217,0.5)';

      const label = this.shadow.getElementById('voicera-selected-date-label');
      const timeSlots = this.shadow.getElementById('voicera-time-slots');
      const slotsDiv = this.shadow.getElementById('voicera-slots-for-date');

      const formatted = dateObj.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' });
      if (label) label.textContent = formatted;
      if (slotsDiv) slotsDiv.style.display = 'block';

      if (timeSlots) {
        timeSlots.innerHTML = slots.map(slot => {
          const t = new Date(slot.start);
          const timeStr = t.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
          return `
            <div data-start="${slot.start}" data-end="${slot.end}"
              style="padding:8px 4px;border:1px solid rgba(255,255,255,0.15);border-radius:6px;font-size:11px;color:rgba(255,255,255,0.8);cursor:pointer;text-align:center;transition:all 0.15s;">
              ${timeStr}
            </div>
          `;
        }).join('');

        timeSlots.querySelectorAll('[data-start]').forEach(el => {
          el.onclick = () => this.selectSlotInWidget(el.dataset.start, el.dataset.end, el);
        });
      }
    }

    selectSlotInWidget(start, end, el) {
      this._selectedSlot = { start, end };

      this.shadow.querySelectorAll('[data-start]').forEach(d => {
        d.style.borderColor = 'rgba(255,255,255,0.15)';
        d.style.background = 'transparent';
        d.style.color = 'rgba(255,255,255,0.8)';
      });
      el.style.borderColor = '#6D28D9';
      el.style.background = 'rgba(109,40,217,0.3)';
      el.style.color = '#fff';

      // Show step 3
      const step3 = this.shadow.getElementById('voicera-step3');
      if (step3) step3.style.display = 'block';

      // Show summary
      const summary = this.shadow.getElementById('voicera-booking-summary');
      if (summary) {
        const date = new Date(start);
        const formatted = date.toLocaleString('en-IN', {
          weekday: 'short', day: 'numeric', month: 'short',
          hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata'
        });
        summary.innerHTML = `📅 <strong>${this._selectedSpecialistName}</strong> · ${formatted}`;
      }

      const confirmBtn = this.shadow.getElementById('voicera-confirm-btn');
      if (confirmBtn) confirmBtn.onclick = () => this.confirmBookingInWidget();

      // Scroll to step 3
      step3.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async confirmBookingInWidget() {
      const name = this.shadow.getElementById('voicera-book-name')?.value?.trim();
      const email = this.shadow.getElementById('voicera-book-email')?.value?.trim();

      if (!name || !email) { alert('Please enter your name and email'); return; }
      if (!this._selectedSpecialistId || !this._selectedSlot) { alert('Please select a specialist and time'); return; }

      const btn = this.shadow.getElementById('voicera-confirm-btn');
      if (btn) { btn.textContent = 'Booking...'; btn.disabled = true; }

      try {
        const res = await fetch(`${this.backendUrl}/api/v1/calendar/book`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            specialist_id: this._selectedSpecialistId,
            slot_start: this._selectedSlot.start,
            slot_end: this._selectedSlot.end,
            user_name: name,
            user_email: email,
            issue_summary: 'Customer requested support call via widget'
          })
        });
        const data = await res.json();
        if (data.success) {
          const s1 = this.shadow.getElementById('voicera-step1'); if (s1) s1.style.display = 'none';
          const s2 = this.shadow.getElementById('voicera-step2'); if (s2) s2.style.display = 'none';
          const s3 = this.shadow.getElementById('voicera-step3'); if (s3) s3.style.display = 'none';
          const cb = this.shadow.getElementById('voicera-cancel-booking'); if (cb) cb.style.display = 'none';
          const succ = this.shadow.getElementById('voicera-booking-success'); if (succ) succ.style.display = 'block';
        } else {
          if (btn) { btn.textContent = 'Confirm Booking'; btn.disabled = false; }
          alert('Booking failed. Please check details and try again.');
        }
      } catch(e) {
        if (btn) { btn.textContent = 'Confirm Booking'; btn.disabled = false; }
        alert('Booking error occurred. Please try again.');
      }
    }

    async resolveAndEnd() {
      try {
        await fetch(`${this.backendUrl}/api/v1/sessions/${this.state.sessionId}/resolve`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.state.token}`
          },
          body: JSON.stringify({
            client_id: this.clientId,
            user_email: this.state.userEmail,
            user_name: this.state.userName,
            issue_summary: this.state.firstMessage
          })
        });
      } catch (e) {
        console.error("Resolve API error:", e);
      }
      this.goToEnd('resolved');
    }

    goToEnd(status) {
      this.state.status = status;
      const icon = this.shadow.getElementById('endIcon');
      const title = this.shadow.getElementById('endTitle');
      const sub = this.shadow.getElementById('endSub');
      const badge = this.shadow.getElementById('statusBadge');
      
      const duration = Math.floor((new Date() - this.state.startTime) / 1000);
      const min = Math.floor(duration / 60);
      const sec = duration % 60;

      if (status === 'resolved') {
        icon.className = 'end-icon resolved'; icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
        title.textContent = 'All done'; sub.textContent = 'Your issue has been resolved. Here\'s a summary of this session.';
        badge.className = 'status-badge resolved'; badge.innerHTML = `<span>Resolved</span>`;
      } else if (status === 'escalated') {
        icon.className = 'end-icon escalated'; icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`;
        title.textContent = 'Specialist booked'; sub.textContent = 'A calendar invite has been sent. Your specialist has full context.';
        badge.className = 'status-badge escalated'; badge.innerHTML = `<span>Escalated</span>`;
      } else {
        icon.className = 'end-icon timeout'; icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`;
        title.textContent = 'Session closed'; sub.textContent = 'This chat was closed due to inactivity. You can start a new one anytime.';
        badge.className = 'status-badge escalated'; badge.innerHTML = `<span>Timed out</span>`;
      }

      this.shadow.getElementById('endSummaryCard').innerHTML = `
        <div class="end-row"><span class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">Topic</span><span class="end-value" style="color:#eef0ff;font-size:13px;font-weight:500">${this.state.firstMessage ? this.state.firstMessage.slice(0, 40) + (this.state.firstMessage.length > 40 ? '...' : '') : 'Support Session'}</span></div>
        <div class="end-divider"></div>
        <div class="end-row"><span class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">Ticket ID</span><span class="end-value mono" style="color:#bd9dff;font-family:monospace;font-size:12px;font-weight:500">#${(this.state.ticketId || this.state.sessionId || '........').slice(0, 8)}</span></div>
        <div class="end-divider"></div>
        <div class="end-row"><span class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">Sentiment</span><div class="sentiment-bar"><div class="sent-dot ${status === 'resolved' ? 'positive' : 'neutral'}"></div><span class="sent-label" style="color:#4ADE80;font-size:12px;font-weight:500">${status === 'resolved' ? 'Positive' : 'Neutral'}</span></div></div>
        <div class="end-divider"></div>
        <div class="end-row"><span class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">Duration</span><span class="end-value" style="color:#eef0ff;font-size:13px;font-weight:500">${min}m ${sec}s</span></div>
        <div class="end-divider"></div>
        <div class="end-row"><span class="end-label" style="color:rgba(238,240,255,0.28);font-size:10.5px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">Channel</span><span class="end-value" style="color:#eef0ff;font-size:13px;font-weight:500">Live Chat</span></div>
      `;
      this.switchScreen('scrEnd');
    }


    rate(n) {
      this.shadow.querySelectorAll('.star').forEach((s, i) => s.classList.toggle('active', i < n));
    }

    reset() {
      this.state = { ...this.state, sessionId: null, token: null, history: [], conversationHistory: [], startTime: null, firstMessage: '', ticketId: null, status: 'resolved', nameCollected: false, userName: '', awaitingEmail: false, userEmail: null };
      this.shadow.getElementById('msgArea').innerHTML = '';
      this.shadow.getElementById('statusArea').innerHTML = '';
      this.switchScreen('scrChannel');
      this.toggle();
    }
  }

  async function showBookingUI() {
    const bookingHTML = `
      <div id="voicera-booking" style="padding:16px;display:flex;flex-direction:column;gap:12px;">
        <div style="font-size:13px;font-weight:600;color:#1a1a2e;">Schedule a Support Call</div>
        <div style="font-size:12px;color:#666;">Choose a specialist and available time slot</div>
        
        <div id="voicera-specialists" style="display:flex;flex-direction:column;gap:8px;">
          <div style="font-size:12px;color:#888;">Loading specialists...</div>
        </div>
        
        <div id="voicera-slots" style="display:none;flex-direction:column;gap:6px;">
          <div style="font-size:12px;font-weight:600;color:#1a1a2e;margin-bottom:4px;">Available Times</div>
          <div id="voicera-slots-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:6px;max-height:200px;overflow-y:auto;"></div>
        </div>
        
        <div id="voicera-booking-form" style="display:none;flex-direction:column;gap:8px;">
          <input id="voicera-book-name" placeholder="Your name" style="padding:8px 12px;border:1px solid #e5e7eb;border-radius:8px;font-size:12px;outline:none;">
          <input id="voicera-book-email" placeholder="Your email" type="email" style="padding:8px 12px;border:1px solid #e5e7eb;border-radius:8px;font-size:12px;outline:none;">
          <button id="voicera-confirm-btn" onclick="confirmBooking()" style="padding:10px;background:linear-gradient(135deg,#6D28D9,#4F46E5);color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;">
            Confirm Booking
          </button>
        </div>
        
        <div id="voicera-booking-success" style="display:none;text-align:center;padding:20px;">
          <div style="font-size:24px;margin-bottom:8px;">✓</div>
          <div style="font-size:13px;font-weight:600;color:#059669;">Call Scheduled!</div>
          <div style="font-size:11px;color:#666;margin-top:4px;">Check your email for the Google Meet link</div>
        </div>
        
        <button onclick="cancelBooking()" style="padding:8px;background:transparent;border:1px solid #e5e7eb;border-radius:8px;font-size:12px;color:#666;cursor:pointer;">
          Continue chatting instead
        </button>
      </div>
    `;
    
    const msgArea = window._voiceraInstance.shadow.getElementById('msgArea');
    if (msgArea) {
      const bookingEl = document.createElement('div');
      bookingEl.innerHTML = bookingHTML;
      msgArea.appendChild(bookingEl);
      msgArea.scrollTop = msgArea.scrollHeight;
    }
    
    await loadSpecialists();
  }

  let selectedSpecialistId = null;
  let selectedSlot = null;

  async function loadSpecialists() {
    try {
      const backendUrl = window._voiceraInstance.backendUrl;
      const clientId = window._voiceraInstance.clientId;
      const res = await fetch(`${backendUrl}/api/v1/auth/team/public?client_id=${clientId}`, {
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      const members = data.members || [];
      
      const container = window._voiceraInstance.shadow.getElementById('voicera-specialists');
      if (!container) return;
      
      if (!members.length) {
        container.innerHTML = '<div style="font-size:12px;color:#666;padding:12px;background:#f9fafb;border-radius:8px;text-align:center;">No specialists available right now. We\'ll get back to you soon.</div>';
        return;
      }
      
      container.innerHTML = members.map(m => {
        const initials = (m.full_name || m.email).charAt(0).toUpperCase();
        const colors = ['#6D28D9','#1D4ED8','#047857','#B45309'];
        const color = colors[m.email.charCodeAt(0) % colors.length];
        return `
          <div onclick="selectSpecialist('${m.id}', '${m.full_name || m.email}')" 
            style="display:flex;align-items:center;gap:10px;padding:10px;border:1px solid #e5e7eb;border-radius:8px;cursor:pointer;transition:all 0.2s;"
            id="spec-${m.id}"
            onmouseover="this.style.borderColor='#6D28D9';this.style.background='#f8f4ff'"
            onmouseout="this.style.borderColor='#e5e7eb';this.style.background='#fff'">
            <div style="width:32px;height:32px;border-radius:50%;background:${color};color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;flex-shrink:0;">${initials}</div>
            <div>
              <div style="font-size:12px;font-weight:600;color:#1a1a2e;">${m.full_name || m.email}</div>
              <div style="font-size:11px;color:#888;">${m.department || 'Support Specialist'}</div>
            </div>
            <div style="margin-left:auto;font-size:11px;color:#6D28D9;">Select →</div>
          </div>
        `;
      }).join('');
    } catch(e) {
      console.error('Load specialists error:', e);
    }
  }

  async function selectSpecialist(specialistId, specialistName) {
    selectedSpecialistId = specialistId;
    const backendUrl = window._voiceraInstance.backendUrl;
    
    // Highlight selected
    window._voiceraInstance.shadow.querySelectorAll('[id^="spec-"]').forEach(el => {
      el.style.borderColor = '#e5e7eb';
      el.style.background = '#fff';
    });
    const selected = window._voiceraInstance.shadow.getElementById(`spec-${specialistId}`);
    if (selected) {
      selected.style.borderColor = '#6D28D9';
      selected.style.background = '#f8f4ff';
    }
    
    // Load slots
    const slotsDiv = window._voiceraInstance.shadow.getElementById('voicera-slots');
    const slotsGrid = window._voiceraInstance.shadow.getElementById('voicera-slots-grid');
    if (slotsDiv) slotsDiv.style.display = 'flex';
    if (slotsGrid) slotsGrid.innerHTML = '<div style="font-size:11px;color:#888;">Loading available times...</div>';
    
    try {
      const res = await fetch(`${backendUrl}/api/v1/calendar/slots/${specialistId}`);
      const data = await res.json();
      const slots = data.slots || data || [];
      
      if (!slots.length) {
        slotsGrid.innerHTML = '<div style="font-size:11px;color:#888;grid-column:1/-1;">No available slots this week</div>';
        return;
      }
      
      slotsGrid.innerHTML = slots.slice(0, 12).map((slot, i) => {
        const date = new Date(slot.start);
        const timeStr = date.toLocaleString('en-IN', {
          weekday: 'short', month: 'short', day: 'numeric',
          hour: '2-digit', minute: '2-digit', hour12: true,
          timeZone: 'Asia/Kolkata'
        });
        return `
          <div onclick="selectSlot('${slot.start}', '${slot.end}', this)"
            style="padding:8px;border:1px solid #e5e7eb;border-radius:6px;font-size:11px;color:#374151;cursor:pointer;text-align:center;transition:all 0.2s;"
            onmouseover="this.style.borderColor='#6D28D9';this.style.background='#f8f4ff'"
            onmouseout="if(!this.classList.contains('selected')){this.style.borderColor='#e5e7eb';this.style.background='#fff'}">
            ${timeStr}
          </div>
        `;
      }).join('');
    } catch(e) {
      if (slotsGrid) slotsGrid.innerHTML = '<div style="font-size:11px;color:#888;grid-column:1/-1;">Could not load slots</div>';
    }
  }

  function selectSlot(start, end, el) {
    selectedSlot = { start, end };
    window._voiceraInstance.shadow.querySelectorAll('#voicera-slots-grid > div').forEach(d => {
      d.classList.remove('selected');
      d.style.borderColor = '#e5e7eb';
      d.style.background = '#fff';
    });
    el.classList.add('selected');
    el.style.borderColor = '#6D28D9';
    el.style.background = '#f8f4ff';
    
    const formDiv = window._voiceraInstance.shadow.getElementById('voicera-booking-form');
    if (formDiv) formDiv.style.display = 'flex';
  }

  async function confirmBooking() {
    const name = window._voiceraInstance.shadow.getElementById('voicera-book-name')?.value?.trim();
    const email = window._voiceraInstance.shadow.getElementById('voicera-book-email')?.value?.trim();
    const backendUrl = window._voiceraInstance.backendUrl;
    
    if (!name || !email) {
      alert('Please enter your name and email');
      return;
    }
    if (!selectedSpecialistId || !selectedSlot) {
      alert('Please select a specialist and time slot');
      return;
    }
    
    const btn = window._voiceraInstance.shadow.getElementById('voicera-confirm-btn');
    if (btn) { btn.textContent = 'Booking...'; btn.disabled = true; }
    
    try {
      const res = await fetch(`${backendUrl}/api/v1/calendar/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          specialist_id: selectedSpecialistId,
          slot_start: selectedSlot.start,
          slot_end: selectedSlot.end,
          user_name: name,
          user_email: email,
          issue_summary: 'Customer requested support call via widget'
        })
      });
      
      const data = await res.json();
      if (data.success) {
        const formDiv = window._voiceraInstance.shadow.getElementById('voicera-booking-form');
        const successDiv = window._voiceraInstance.shadow.getElementById('voicera-booking-success');
        const slotsDiv = window._voiceraInstance.shadow.getElementById('voicera-slots');
        const specsDiv = window._voiceraInstance.shadow.getElementById('voicera-specialists');
        if (formDiv) formDiv.style.display = 'none';
        if (slotsDiv) slotsDiv.style.display = 'none';
        if (specsDiv) specsDiv.style.display = 'none';
        if (successDiv) successDiv.style.display = 'block';
      } else {
        if (btn) { btn.textContent = 'Confirm Booking'; btn.disabled = false; }
        alert('Booking failed. Please try again.');
      }
    } catch(e) {
      if (btn) { btn.textContent = 'Confirm Booking'; btn.disabled = false; }
      alert('Booking failed. Please try again.');
    }
  }

  function cancelBooking() {
    const bookingDiv = window._voiceraInstance.shadow.getElementById('voicera-booking');
    if (bookingDiv) bookingDiv.closest('div').remove();
  }

  window.showBookingUI = showBookingUI;
  window.loadSpecialists = loadSpecialists;
  window.selectSpecialist = selectSpecialist;
  window.selectSlot = selectSlot;
  window.confirmBooking = confirmBooking;
  window.cancelBooking = cancelBooking;

  window.VoiceraWidget = VoiceraWidget;
})();
