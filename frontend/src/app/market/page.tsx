"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FARMERS = [
  { phone: "+258840000001", label: "Dona Maria" },
  { phone: "+258840000002", label: "Tio Armando" },
  { phone: "+258840000003", label: "Mana Celeste" },
];

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
  return v === null ? "—" : `${v.toFixed(0)}`;
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

  // edit-mode per crop
  const [editing, setEditing] = useState<string | null>(null);
  const [wsInput, setWsInput] = useState("");
  const [rsInput, setRsInput] = useState("");

  // add-new state
  const [addingNew, setAddingNew] = useState(false);
  const [newCrop, setNewCrop] = useState("");
  const [newWs, setNewWs] = useState("");
  const [newRs, setNewRs] = useState("");

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/market-prices`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSnaps(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro a carregar.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function post(crop: string, ws: number | null, rs: number | null) {
    if (ws === null && rs === null) {
      setError("Indica pelo menos um preço.");
      return;
    }
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/market-prices`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          contributor_phone: phone,
          crop,
          price_wholesale: ws,
          price_retail: rs,
          market: "Zimpeto",
          observed_at: new Date().toISOString(),
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro a contribuir.");
    }
  }

  async function confirm(s: Snapshot) {
    await post(s.crop, s.latest_wholesale, s.latest_retail);
  }

  function startEdit(s: Snapshot) {
    setEditing(s.crop);
    setWsInput(s.latest_wholesale?.toString() ?? "");
    setRsInput(s.latest_retail?.toString() ?? "");
  }

  async function saveEdit(crop: string) {
    const ws = wsInput ? parseFloat(wsInput) : null;
    const rs = rsInput ? parseFloat(rsInput) : null;
    await post(crop, ws, rs);
    setEditing(null);
  }

  async function saveNew() {
    const crop = newCrop.toLowerCase().trim();
    if (!crop) {
      setError("Indica o nome do produto.");
      return;
    }
    const ws = newWs ? parseFloat(newWs) : null;
    const rs = newRs ? parseFloat(newRs) : null;
    await post(crop, ws, rs);
    setNewCrop("");
    setNewWs("");
    setNewRs("");
    setAddingNew(false);
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
        <div className="mt-3">
          <label className="block text-[10px] uppercase tracking-widest text-preto-terra/50">
            Quem está a contribuir
          </label>
          <select
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="mt-1 w-full rounded-md border border-preto-terra/20 bg-white/60 px-2 py-2 text-sm"
          >
            {FARMERS.map((f) => (
              <option key={f.phone} value={f.phone}>
                {f.label}
              </option>
            ))}
          </select>
        </div>
      </header>

      <section className="flex-1 overflow-y-auto px-5 py-3">
        {error && <p className="mb-3 text-xs text-terracota">{error}</p>}
        {loading && snaps.length === 0 && (
          <p className="text-sm italic text-preto-terra/50">A carregar…</p>
        )}

        <ul className="space-y-2">
          {snaps.map((s) => {
            const isEditing = editing === s.crop;
            return (
              <li key={s.crop} className="rounded-2xl bg-white px-4 py-3 shadow-sm">
                <div className="flex items-baseline justify-between">
                  <span className="font-display text-lg capitalize">{s.crop}</span>
                  <span className="text-[10px] uppercase tracking-widest text-preto-terra/50">
                    {timeAgo(s.last_observed_at)}
                  </span>
                </div>

                {!isEditing && (
                  <>
                    <div className="mt-1 flex items-baseline gap-4 text-sm">
                      <span>
                        <span className="text-[10px] uppercase tracking-widest text-preto-terra/50">grossista </span>
                        <span className="font-medium">{fmt(s.latest_wholesale)} MZN/kg</span>
                      </span>
                      <span>
                        <span className="text-[10px] uppercase tracking-widest text-preto-terra/50">retalho </span>
                        <span className="font-medium">{fmt(s.latest_retail)} MZN/kg</span>
                      </span>
                    </div>
                    <div className="mt-2 flex gap-2">
                      <button
                        type="button"
                        onClick={() => confirm(s)}
                        className="flex-1 rounded-md bg-verde-capim px-3 py-2 text-[11px] uppercase tracking-widest text-sisal"
                      >
                        Continua igual
                      </button>
                      <button
                        type="button"
                        onClick={() => startEdit(s)}
                        className="flex-1 rounded-md border border-preto-terra/20 px-3 py-2 text-[11px] uppercase tracking-widest"
                      >
                        Actualizar
                      </button>
                    </div>
                  </>
                )}

                {isEditing && (
                  <div className="mt-2 space-y-2">
                    <div className="grid grid-cols-2 gap-2">
                      <label className="text-[10px] uppercase tracking-widest text-preto-terra/60">
                        Grossista MZN/kg
                        <input
                          type="number"
                          inputMode="decimal"
                          value={wsInput}
                          onChange={(e) => setWsInput(e.target.value)}
                          className="mt-1 w-full rounded-md border border-preto-terra/20 bg-white px-2 py-2 text-sm"
                        />
                      </label>
                      <label className="text-[10px] uppercase tracking-widest text-preto-terra/60">
                        Retalho MZN/kg
                        <input
                          type="number"
                          inputMode="decimal"
                          value={rsInput}
                          onChange={(e) => setRsInput(e.target.value)}
                          className="mt-1 w-full rounded-md border border-preto-terra/20 bg-white px-2 py-2 text-sm"
                        />
                      </label>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => saveEdit(s.crop)}
                        className="flex-1 rounded-md bg-preto-terra px-3 py-2 text-[11px] uppercase tracking-widest text-sisal"
                      >
                        Guardar
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditing(null)}
                        className="rounded-md border border-preto-terra/20 px-3 py-2 text-[11px] uppercase tracking-widest"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>

        {!addingNew && (
          <button
            type="button"
            onClick={() => setAddingNew(true)}
            className="mt-3 w-full rounded-md border border-dashed border-preto-terra/30 px-3 py-3 text-[11px] uppercase tracking-widest text-preto-terra/60"
          >
            + Adicionar produto
          </button>
        )}

        {addingNew && (
          <div className="mt-3 space-y-2 rounded-2xl bg-white px-4 py-3 shadow-sm">
            <input
              type="text"
              placeholder="ex: couve, mandioca, abóbora"
              value={newCrop}
              onChange={(e) => setNewCrop(e.target.value)}
              className="w-full rounded-md border border-preto-terra/20 bg-white px-2 py-2 text-sm"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                inputMode="decimal"
                placeholder="grossista MZN/kg"
                value={newWs}
                onChange={(e) => setNewWs(e.target.value)}
                className="rounded-md border border-preto-terra/20 bg-white px-2 py-2 text-sm"
              />
              <input
                type="number"
                inputMode="decimal"
                placeholder="retalho MZN/kg"
                value={newRs}
                onChange={(e) => setNewRs(e.target.value)}
                className="rounded-md border border-preto-terra/20 bg-white px-2 py-2 text-sm"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={saveNew}
                className="flex-1 rounded-md bg-preto-terra px-3 py-2 text-[11px] uppercase tracking-widest text-sisal"
              >
                Adicionar
              </button>
              <button
                type="button"
                onClick={() => setAddingNew(false)}
                className="rounded-md border border-preto-terra/20 px-3 py-2 text-[11px] uppercase tracking-widest"
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
