import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from "react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

type SpeechRecognitionCtor = new () => SpeechRecognition;

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  isFinal: boolean;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  const w = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export function ChatComposer({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const [micSupported, setMicSupported] = useState(true);

  const taRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const baselineRef = useRef("");

  useEffect(() => {
    setMicSupported(getSpeechRecognition() !== null);
  }, []);

  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
    };
  }, []);

  const submit = (e?: FormEvent) => {
    e?.preventDefault();
    const v = text.trim();
    if (!v || disabled) return;
    onSend(v);
    setText("");
    taRef.current?.focus();
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
  };

  const startListening = () => {
    const Ctor = getSpeechRecognition();
    if (!Ctor) {
      setMicError("Voice input isn't supported in this browser. Try Chrome or Edge.");
      setMicSupported(false);
      return;
    }

    setMicError(null);
    const rec = new Ctor();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    baselineRef.current = text ? text.replace(/\s+$/, "") + " " : "";

    rec.onstart = () => setListening(true);

    rec.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        if (result.isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }
      if (final) {
        baselineRef.current = (baselineRef.current + final).replace(/\s+/g, " ");
      }
      setText((baselineRef.current + interim).replace(/\s+/g, " ").trimStart());
    };

    rec.onerror = (event) => {
      const msg =
        event.error === "not-allowed" || event.error === "service-not-allowed"
          ? "Microphone access was blocked. Enable it in your browser permissions."
          : event.error === "no-speech"
            ? "I didn't catch that — try again."
            : `Voice input error: ${event.error}`;
      setMicError(msg);
      setListening(false);
    };

    rec.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = rec;
    try {
      rec.start();
    } catch (err) {
      setMicError("Couldn't start voice input. Try again.");
      setListening(false);
    }
  };

  const toggleMic = () => {
    if (listening) {
      stopListening();
    } else {
      startListening();
      taRef.current?.focus();
    }
  };

  const micTitle = !micSupported
    ? "Voice input not supported in this browser"
    : listening
      ? "Stop listening"
      : "Start voice input";

  return (
    <div className="composer-wrap">
      <form className="composer" onSubmit={submit}>
        <button
          type="button"
          className={`composer__mic ${listening ? "is-listening" : ""}`.trim()}
          onClick={toggleMic}
          disabled={!micSupported || disabled}
          aria-label={micTitle}
          aria-pressed={listening}
          title={micTitle}
        >
          {listening ? (
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <rect x="7" y="7" width="10" height="10" rx="1.5" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
              <path
                d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"
                stroke="currentColor"
                strokeWidth="1.8"
              />
              <path
                d="M5 11a7 7 0 0 0 14 0M12 18v3"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          )}
        </button>

        <textarea
          ref={taRef}
          className="composer__input"
          placeholder={
            listening
              ? "Listening… speak now"
              : "Ask anything — press Enter to send, Shift+Enter for a new line"
          }
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
          disabled={disabled}
        />

        <button
          type="submit"
          className="composer__send"
          disabled={disabled || !text.trim()}
          aria-label="Send message"
        >
          <span>Send</span>
          <span aria-hidden="true">→</span>
        </button>
      </form>

      {(micError || listening) && (
        <div
          className={`composer__status ${
            micError ? "composer__status--error" : "composer__status--live"
          }`}
          role="status"
          aria-live="polite"
        >
          {listening && !micError && (
            <>
              <span className="composer__status-dot" aria-hidden="true" />
              Listening… click the mic again to stop.
            </>
          )}
          {micError}
        </div>
      )}
    </div>
  );
}
