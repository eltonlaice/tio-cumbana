"use client";

import { useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FARMERS = [
  { phone: "+258840000001", label: "Dona Maria · Maluana · pepino + pimento" },
  { phone: "+258840000002", label: "Tio Armando · Marracuene · batata + couve" },
  { phone: "+258840000003", label: "Mana Celeste · Bobole · tomate + feijão" },
];

type Message = {
  role: "farmer" | "tio";
  text?: string;
  photoUrl?: string;
  audioUrl?: string;
};

type ConsultResponse = {
  text: string;
  audio_b64: string | null;
  audio_mime: string;
  farmer: { name: string };
};

function b64ToObjectUrl(b64: string, mime: string): string {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return URL.createObjectURL(new Blob([bytes], { type: mime }));
}

export default function Home() {
  const [phone, setPhone] = useState(FARMERS[0].phone);
  const [photo, setPhoto] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      chunksRef.current = [];
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: mr.mimeType || "audio/webm",
        });
        setAudioBlob(blob);
        stream.getTracks().forEach((t) => t.stop());
      };
      mr.start();
      mediaRef.current = mr;
      setRecording(true);
    } catch (e) {
      setError("Microfone não disponível.");
      console.error(e);
    }
  }

  function stopRecording() {
    mediaRef.current?.stop();
    setRecording(false);
  }

  async function send() {
    if (!photo || !audioBlob) {
      setError("Anexa uma foto e grava uma nota de voz primeiro.");
      return;
    }
    setError(null);
    setLoading(true);

    const photoUrl = URL.createObjectURL(photo);
    const audioUrl = URL.createObjectURL(audioBlob);
    setMessages((m) => [...m, { role: "farmer", photoUrl, audioUrl }]);

    const fd = new FormData();
    fd.append("photo", photo);
    fd.append("audio", audioBlob, "voice.webm");
    fd.append("farmer_phone", phone);

    try {
      const res = await fetch(`${API_URL}/api/consult`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ConsultResponse = await res.json();
      const tioAudio = data.audio_b64
        ? b64ToObjectUrl(data.audio_b64, data.audio_mime)
        : undefined;
      setMessages((m) => [
        ...m,
        { role: "tio", text: data.text, audioUrl: tioAudio },
      ]);
      setPhoto(null);
      setAudioBlob(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao contactar o Tio Cumbana.");
    } finally {
      setLoading(false);
    }
  }

  async function proactive() {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/proactive`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ farmer_phone: phone, trigger: "mildew_morning" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ConsultResponse = await res.json();
      const tioAudio = data.audio_b64
        ? b64ToObjectUrl(data.audio_b64, data.audio_mime)
        : undefined;
      setMessages((m) => [
        ...m,
        { role: "tio", text: data.text, audioUrl: tioAudio },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro no trigger.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col">
      <header className="border-b border-preto-terra/20 px-5 py-5">
        <h1 className="font-display text-4xl leading-none tracking-tight">
          Tio{" "}
          <em className="italic font-normal text-terracota">Cumbana</em>
        </h1>
        <p className="mt-1 text-[11px] uppercase tracking-[0.25em] text-verde-capim">
          Agronomia relacional
        </p>
      </header>

      <section className="px-5 py-4">
        <label className="mb-1 block text-xs uppercase tracking-widest text-preto-terra/60">
          Agricultor
        </label>
        <select
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          className="w-full rounded-md border border-preto-terra/20 bg-white/60 px-3 py-2 text-sm"
        >
          {FARMERS.map((f) => (
            <option key={f.phone} value={f.phone}>
              {f.label}
            </option>
          ))}
        </select>
      </section>

      <section className="flex-1 space-y-3 overflow-y-auto px-5 py-2">
        {messages.length === 0 && (
          <p className="pt-10 text-center text-sm italic text-preto-terra/50">
            Anexa uma foto da planta e grava uma nota de voz.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "farmer" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-3 py-2 shadow-sm ${
                m.role === "farmer"
                  ? "bg-verde-capim text-sisal"
                  : "bg-white text-preto-terra"
              }`}
            >
              {m.photoUrl && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={m.photoUrl}
                  alt="planta"
                  className="mb-2 max-h-48 rounded-lg"
                />
              )}
              {m.text && (
                <p className="whitespace-pre-wrap text-sm">{m.text}</p>
              )}
              {m.audioUrl && (
                <audio controls src={m.audioUrl} className="mt-2 w-full" />
              )}
            </div>
          </div>
        ))}
      </section>

      <footer className="border-t border-preto-terra/20 bg-sisal/80 px-5 py-3 backdrop-blur">
        {error && <p className="mb-2 text-xs text-terracota">{error}</p>}
        <div className="flex items-center gap-2">
          <label className="flex-1 cursor-pointer rounded-md border border-preto-terra/20 bg-white/60 px-3 py-2 text-center text-xs uppercase tracking-widest">
            {photo ? `📷 ${photo.name.slice(0, 18)}…` : "Anexar foto"}
            <input
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="button"
            onClick={recording ? stopRecording : startRecording}
            className={`rounded-md px-3 py-2 text-xs uppercase tracking-widest ${
              recording
                ? "bg-terracota text-sisal"
                : audioBlob
                  ? "bg-verde-capim text-sisal"
                  : "border border-preto-terra/20 bg-white/60"
            }`}
          >
            {recording ? "Parar" : audioBlob ? "🎙 gravado" : "🎙 Gravar"}
          </button>
        </div>
        <div className="mt-2 flex items-center gap-2">
          <button
            type="button"
            disabled={loading || !photo || !audioBlob}
            onClick={send}
            className="flex-1 rounded-md bg-preto-terra px-3 py-2 text-xs uppercase tracking-widest text-sisal disabled:opacity-40"
          >
            {loading ? "A consultar…" : "Enviar"}
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={proactive}
            title="Simular mensagem proactiva do Tio Cumbana"
            className="rounded-md border border-ocre bg-ocre/20 px-3 py-2 text-xs uppercase tracking-widest text-terracota-deep disabled:opacity-40"
          >
            Proactivo
          </button>
        </div>
      </footer>
    </main>
  );
}
