"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FARMERS = [
  { phone: "+258840000001", label: "Dona Maria" },
  { phone: "+258840000002", label: "Tio Armando" },
  { phone: "+258840000003", label: "Mana Celeste" },
];

const CROPS = ["pepino", "tomate", "pimento", "cebola", "alho", "couve", "feijão-nhemba"];

type Snapshot = {
  crop: string;
  market: string;
  latest_wholesale: number | null;
  latest_retail: number | null;
  median_wholesale_7d: number | null;
  median_retail_7d: number | null;
  sample_size_7d: number;
  last_observed_at: string | null;
  contributors_7d: number;
};

function fmt(v: number | null): string {
  return v === null ? "—" : `${v.toFixed(0)} MZN/kg`;
}

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const d = (Date.now() - new Date(iso).getTime()) / 1000 / 60 / 60;
  if (d < 1) return `há ${Math.round(d * 60)} min`;
  if (d < 24) return `há ${Math.round(d)} h`;
  return `há ${Math.round(d / 24)} d`;
}

export default function MarketPage() {
  const [snaps, setSnaps] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [phone, setPhone] = useState(FARMERS[0].phone);
  const [crop, setCrop] = useState("pepino");
  const [wholesale, setWholesale] = useState("");
  const [retail, setRetail] = useState("");
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/market-prices`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSnaps(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro a carregar preços.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function contribute(e: React.FormEvent) {
    e.preventDefault();
    if (!wholesale && !retail) {
      setError("Pelo menos um preço (grossista ou retalho).");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/market-prices`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          contributor_phone: phone,
          crop,
          price_wholesale: wholesale ? parseFloat(wholesale) : null,
          price_retail: retail ? parseFloat(retail) : null,
          market: "Zimpeto",
          observed_at: new Date().toISOString(),
          note: note || null,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setWholesale("");
      setRetail("");
      setNote("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro a contribuir.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col">
      <header className="border-b border-preto-terra/20 px-5 py-5">
        <Link href="/" className="text-[11px] uppercase tracking-[0.25em] text-verde-capim">
          ← Tio Cumbana
        </Link>
        <h1 className="font-display mt-1 text-3xl leading-none tracking-tight">
          Mercado <em className="italic font-normal text-terracota">Zimpeto</em>
        </h1>
        <p className="mt-1 text-[11px] uppercase tracking-[0.25em] text-verde-capim">
          Preços contribuídos pelos agricultores
        </p>
      </header>

      <section className="flex-1 overflow-y-auto px-5 py-4">
        {loading && <p className="text-sm italic text-preto-terra/50">A carregar…</p>}
        {!loading && snaps.length === 0 && (
          <p className="text-sm italic text-preto-terra/50">Pool vazia. Sê o primeiro a contribuir.</p>
        )}
        <ul className="space-y-2">
          {snaps.map((s) => (
            <li key={s.crop} className="rounded-2xl bg-white px-4 py-3 shadow-sm">
              <div className="flex items-baseline justify-between">
                <span className="font-display text-lg capitalize">{s.crop}</span>
                <span className="text-[10px] uppercase tracking-widest text-preto-terra/50">
                  {s.contributors_7d} contribuidor{s.contributors_7d === 1 ? "" : "es"} · {timeAgo(s.last_observed_at)}
                </span>
              </div>
              <div className="mt-1 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-preto-terra/50">Grossista</div>
                  <div className="font-medium">{fmt(s.latest_wholesale)}</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-preto-terra/50">Retalho</div>
                  <div className="font-medium">{fmt(s.latest_retail)}</div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <footer className="border-t border-preto-terra/20 bg-sisal/80 px-5 py-3 backdrop-blur">
        {error && <p className="mb-2 text-xs text-terracota">{error}</p>}
        <form onSubmit={contribute} className="space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <select
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-xs"
            >
              {FARMERS.map((f) => (
                <option key={f.phone} value={f.phone}>{f.label}</option>
              ))}
            </select>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-xs capitalize"
            >
              {CROPS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              inputMode="decimal"
              placeholder="grossista MZN/kg"
              value={wholesale}
              onChange={(e) => setWholesale(e.target.value)}
              className="rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-xs"
            />
            <input
              type="number"
              inputMode="decimal"
              placeholder="retalho MZN/kg"
              value={retail}
              onChange={(e) => setRetail(e.target.value)}
              className="rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-xs"
            />
          </div>
          <input
            type="text"
            placeholder="nota (opcional, ex: pouco stock)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-xs"
          />
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-preto-terra px-3 py-2 text-xs uppercase tracking-widest text-sisal disabled:opacity-40"
          >
            {submitting ? "A contribuir…" : "Contribuir preço"}
          </button>
        </form>
      </footer>
    </main>
  );
}
