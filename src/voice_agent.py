"""Voice agent — native st.audio_input + Groq Whisper STT.

Uses Streamlit's built-in `st.audio_input` (no iframe) to capture audio,
transcribes via Groq `whisper-large-v3`, parses the transcript for nav
commands or treats it as a dictated question, and returns a command dict
that the main app maps to session_state mutations.

Earlier attempts used a components.html iframe (blocked from redirecting
the parent) and then `streamlit_mic_recorder` (styled from inside its own
iframe, couldn't match the dark theme). The native widget sidesteps both
issues — it sits in the host page's DOM, so our CSS actually reaches it.
"""

import json
import logging
import os
import re
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)


NAV_MAP = {
    "dashboard": "dashboard", "home": "dashboard", "main": "dashboard",
    "hr": "hr", "human": "hr", "onboarding": "hr", "people": "hr", "benefits": "hr",
    "qa": "qa", "quality": "qa", "automation": "qa", "testing": "qa",
    "security": "security", "guardrail": "security",
    "history": "history", "past": "history", "previous": "history",
    "new chat": "new_chat", "fresh chat": "new_chat",
    "log out": "logout", "logout": "logout", "sign out": "logout", "signout": "logout",
}

NAV_VERB_PREFIXES = (
    "open ", "go to ", "goto ", "navigate to ", "take me to ",
    "show me ", "show ", "switch to ",
)

BARE_NAV = {
    "dashboard", "home", "history", "log out", "logout",
    "sign out", "signout", "new chat", "exit",
}


def _parse_nav(text: str) -> Optional[str]:
    """Return a nav action code if the text looks like a navigation command."""
    lower = text.lower().strip().rstrip(".!?,")
    target = None
    for prefix in NAV_VERB_PREFIXES:
        if lower.startswith(prefix):
            target = lower[len(prefix):].strip()
            break
    if target is None and lower in BARE_NAV:
        target = lower
    if target is None:
        return None
    for key in sorted(NAV_MAP.keys(), key=len, reverse=True):
        if key in target:
            return NAV_MAP[key]
    return None


def _transcribe_groq(audio_bytes: bytes, filename: str = "voice.wav") -> Optional[str]:
    """Transcribe audio via Groq Whisper. Returns None on failure."""
    try:
        from groq import Groq
    except ImportError:
        logger.warning("[Voice] groq SDK not installed")
        return None

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("GROQ_API_KEY")
        except ImportError:
            pass
    if not api_key:
        logger.warning("[Voice] GROQ_API_KEY not set in environment")
        return None

    try:
        client = Groq(api_key=api_key)
        result = client.audio.transcriptions.create(
            file=(filename, audio_bytes, "audio/wav"),
            model="whisper-large-v3",
            language="en",
            response_format="text",
        )
        text = result if isinstance(result, str) else getattr(result, "text", "")
        return (text or "").strip() or None
    except Exception as e:
        logger.exception("[Voice] Groq transcription failed: %s", e)
        return None


_MIC_CSS = """
<style>
/* Target the audio_input widget, hide label, make it compact and dark */
div[data-testid="stAudioInput"] {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stAudioInput"] label {
    display: none !important;
}
div[data-testid="stAudioInput"] > div,
div[data-testid="stAudioInput"] section {
    background: rgba(10, 22, 40, 0.85) !important;
    border: 1px solid rgba(113, 197, 232, 0.45) !important;
    border-radius: 22px !important;
    padding: 4px 8px !important;
    min-height: 44px !important;
    backdrop-filter: blur(6px);
}
/* Kill every inner background so nothing shows a light box */
div[data-testid="stAudioInput"] *,
div[data-testid="stAudioInput"] *::before,
div[data-testid="stAudioInput"] *::after {
    background: transparent !important;
    background-color: transparent !important;
    color: #e0eaf4 !important;
    box-shadow: none !important;
}
/* Restore the outer pill background we set above (the selector above
   also matched the pill itself and wiped it) */
div[data-testid="stAudioInput"] > div,
div[data-testid="stAudioInput"] section {
    background: rgba(10, 22, 40, 0.85) !important;
}
div[data-testid="stAudioInput"] button {
    border: none !important;
}
div[data-testid="stAudioInput"] button:hover {
    color: #71C5E8 !important;
}
div[data-testid="stAudioInput"] svg {
    fill: #e0eaf4 !important;
    color: #e0eaf4 !important;
}
/* Digital timer often uses a code/time element with a distinct font bg */
div[data-testid="stAudioInput"] time,
div[data-testid="stAudioInput"] code,
div[data-testid="stAudioInput"] [class*="time"],
div[data-testid="stAudioInput"] [class*="Time"],
div[data-testid="stAudioInput"] [class*="duration"],
div[data-testid="stAudioInput"] [class*="Duration"] {
    background: transparent !important;
    background-color: transparent !important;
    color: #e0eaf4 !important;
    font-family: 'EB Garamond', Georgia, serif !important;
    font-variant-numeric: tabular-nums;
}
</style>
"""


def render_voice_mic(key: str = "voice_mic") -> Optional[dict]:
    """Render the mic widget and return a parsed command dict, or None.

    Return shapes:
      - None: nothing new was recorded
      - {"action": "nav", "target": "<hr|qa|dashboard|...>", "raw": "..."}
      - {"action": "query", "text": "<transcript>"}
    """
    st.markdown(_MIC_CSS, unsafe_allow_html=True)

    audio_file = st.audio_input(
        "Voice input",
        key=key,
        label_visibility="collapsed",
    )

    if audio_file is None:
        return None

    # De-dupe: st.audio_input returns the same UploadedFile on reruns until
    # the user records a new clip or clears it. Track the file id.
    fid = getattr(audio_file, "file_id", None) or getattr(audio_file, "id", None)
    last_key = f"_voice_last_id__{key}"
    if fid is not None and st.session_state.get(last_key) == fid:
        return None
    if fid is not None:
        st.session_state[last_key] = fid

    try:
        audio_bytes = audio_file.getvalue()
    except Exception:
        audio_bytes = audio_file.read() if hasattr(audio_file, "read") else None
    if not audio_bytes:
        return None

    text = _transcribe_groq(audio_bytes)
    if not text:
        logger.warning("[Voice] Empty transcript")
        return None

    logger.info("[Voice] Transcribed: %r", text)

    action = _parse_nav(text)
    if action:
        return {"action": "nav", "target": action, "raw": text}
    return {"action": "query", "text": text}


# ── Text-to-speech ────────────────────────────────────────────────────
# Uses the browser's built-in SpeechSynthesis API (no API key, no audio
# upload). Works in Chrome, Edge, Safari, and Firefox. We strip markdown
# and code fences before speaking so the TTS engine doesn't read out
# "asterisk asterisk hello asterisk asterisk" etc.

_MD_STRIP_PATTERNS = [
    (re.compile(r"```.*?```", re.DOTALL), " "),       # fenced code blocks
    (re.compile(r"`([^`]*)`"), r"\1"),                 # inline code
    (re.compile(r"!\[[^\]]*\]\([^\)]*\)"), " "),      # images
    (re.compile(r"\[([^\]]+)\]\([^\)]+\)"), r"\1"),   # links → label only
    (re.compile(r"[*_]{1,3}([^*_]+)[*_]{1,3}"), r"\1"),  # bold/italic
    (re.compile(r"^#{1,6}\s+", re.MULTILINE), ""),    # headings
    (re.compile(r"^>\s?", re.MULTILINE), ""),          # blockquotes
    (re.compile(r"^[-*+]\s+", re.MULTILINE), ""),     # bullets
    (re.compile(r"\|"), " "),                           # table pipes
    (re.compile(r"<[^>]+>"), " "),                     # stray html
    (re.compile(r"\s+"), " "),                          # collapse whitespace
]

_MAX_TTS_CHARS = 1200  # cap so long answers don't monopolize the speaker


def _strip_markdown(text: str) -> str:
    s = text or ""
    for pat, repl in _MD_STRIP_PATTERNS:
        s = pat.sub(repl, s)
    return s.strip()


def speak_text(text: str, key: str = "tts") -> None:
    """Speak the given text via the browser's SpeechSynthesis API.

    Rendered as a tiny components.html block whose <script> runs once the
    iframe mounts. We deliberately use `window.parent.speechSynthesis` /
    `window.parent.SpeechSynthesisUtterance` so the utterance is created
    in the Streamlit top-frame realm — this carries the user activation
    from the mic click and sidesteps autoplay policy issues that prevent
    iframe-scoped speech from playing.
    """
    clean = _strip_markdown(text)
    if not clean:
        return
    if len(clean) > _MAX_TTS_CHARS:
        clean = clean[:_MAX_TTS_CHARS].rsplit(" ", 1)[0] + "…"
    payload = json.dumps(clean)
    html = f"""
    <div id="tts-status" style="font-family:'EB Garamond',Georgia,serif;font-size:12px;color:#7da3c0;padding:2px 4px;">speaking…</div>
    <script>
    (function() {{
        const status = document.getElementById('tts-status');
        const setStatus = (t) => {{ if (status) status.textContent = t; }};
        const TEXT = {payload};

        // Pick the synth from the parent (Streamlit top frame) if same-origin,
        // otherwise fall back to this iframe's own synth.
        let synth, Utterance;
        try {{
            synth = window.parent.speechSynthesis;
            Utterance = window.parent.SpeechSynthesisUtterance;
            // Touch to confirm same-origin access
            void synth.speaking;
        }} catch (e) {{
            synth = window.speechSynthesis;
            Utterance = window.SpeechSynthesisUtterance;
        }}
        if (!synth || !Utterance) {{
            setStatus('TTS not available in this browser');
            return;
        }}

        const speakNow = () => {{
            try {{
                synth.cancel();
                const u = new Utterance(TEXT);
                u.rate = 1.0;
                u.pitch = 1.05;
                u.volume = 1.0;
                const voices = synth.getVoices();
                const pref = voices.find(v => v.name && (v.name.includes('Samantha') || v.name.includes('Google US English')))
                    || voices.find(v => v.lang && v.lang.startsWith('en'))
                    || voices[0];
                if (pref) u.voice = pref;
                u.onstart = () => setStatus('🔊 speaking');
                u.onend   = () => setStatus('');
                u.onerror = (e) => setStatus('TTS error: ' + (e.error || 'unknown'));
                synth.speak(u);
            }} catch (err) {{
                console.warn('TTS speak failed:', err);
                setStatus('TTS failed: ' + err.message);
            }}
        }};

        if (synth.getVoices().length === 0) {{
            // Voices load asynchronously on first use in some browsers
            const onVoices = () => {{
                synth.removeEventListener && synth.removeEventListener('voiceschanged', onVoices);
                speakNow();
            }};
            synth.addEventListener && synth.addEventListener('voiceschanged', onVoices);
            // Also try after a short delay in case the event doesn't fire
            setTimeout(speakNow, 250);
        }} else {{
            speakNow();
        }}
    }})();
    </script>
    """
    components.html(html, height=24)
