"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Snapshot = {
  crop: string;
  market: string;
  confirmed: boolean;
  median_wholesale: number | null;
  median_retail: number | null;
  min_wholesale: number | null;
  max_wholesale: number | null;
  min_retail: number | null;
  max_retail: number | null;
  contributors_24h: number;
  sample_size_24h: number;
  last_observed_at: string | null;
};

type Supplier = {
  name: string;
  location: string;
  phone: string;
  weeks: number; // estimated weeks to harvest window
  qualityFlags: number; // # disease flags this season
  estimatedKg: number; // available kg next 7 days
};

const CATALOG: Record<string, Supplier[]> = {
  pepino: [
    { name: "Dona Maria", location: "Maluana, Marracuene", phone: "+258840000001", weeks: 1, qualityFlags: 0, estimatedKg: 95 },
    { name: "Mana Celeste", location: "Bobole, Marracuene", phone: "+258840000003", weeks: 2, qualityFlags: 0, estimatedKg: 60 },
  ],
  pimento: [
    { name: "Dona Maria", location: "Maluana, Marracuene", phone: "+258840000001", weeks: 3, qualityFlags: 0, estimatedKg: 40 },
  ],
  tomate: [
    { name: "Mana Celeste", location: "Bobole, Marracuene", phone: "+258840000003", weeks: 2, qualityFlags: 1, estimatedKg: 80 },
  ],
  cebola: [
    { name: "Tio Armando", location: "Marracuene-sede", phone: "+258840000002", weeks: 4, qualityFlags: 0, estimatedKg: 120 },
  ],
  alho: [
    { name: "Tio Armando", location: "Marracuene-sede", phone: "+258840000002", weeks: 6, qualityFlags: 0, estimatedKg: 25 },
  ],
};

function range(min: number | null, max: number | null, median: number | null): string {
  if (median === null) return "—";
  if (min === null || max === null || min === max) return `${median.toFixed(0)}`;
  return `${min.toFixed(0)}–${max.toFixed(0)}`;
}

function qualityLabel(flags: number): { label: string; color: string } {
  if (flags === 0) return { label: "Sem alertas", color: "var(--color-verde-capim)" };
  if (flags === 1) return { label: "1 alerta", color: "var(--color-ocre)" };
  return { label: `${flags} alertas`, color: "var(--color-terracota)" };
}

export default function RetailPage() {
  const [snaps, setSnaps] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const [contacted, setContacted] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/market-prices`);
      if (res.ok) setSnaps(await res.json());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  function snapshotFor(crop: string): Snapshot | null {
    return snaps.find((s) => s.crop === crop) ?? null;
  }

  async function contact(supplier: Supplier, crop: string) {
    setContacted(`${supplier.name} · ${crop}`);
    try {
      await fetch(`${API_URL}/api/proactive`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ farmer_phone: supplier.phone, trigger: `retail_inquiry_${crop}` }),
      });
    } catch {
      /* swallow — UI still shows confirmation */
    }
    setTimeout(() => setContacted(null), 3500);
  }

  const totalKg = Object.values(CATALOG).flat().reduce((sum, s) => sum + s.estimatedKg, 0);
  const totalSuppliers = new Set(Object.values(CATALOG).flat().map((s) => s.phone)).size;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col">
      <header className="border-b border-preto-terra/20 px-5 py-5">
        <Link href="/" className="text-[11px] uppercase tracking-[0.25em] text-verde-capim">
          ← Tio Cumbana
        </Link>
        <h1 className="font-display mt-1 text-3xl leading-none tracking-tight">
          Tio <em className="italic font-normal text-terracota">Retail</em>
        </h1>
        <p className="mt-1 text-[11px] uppercase tracking-[0.25em] text-verde-capim">
          Visão para supermercados e compradores
        </p>
        <div className="mt-4 grid grid-cols-3 gap-4 border-t border-preto-terra/10 pt-4 text-sm">
          <div>
            <div className="text-[10px] uppercase tracking-widest text-preto-terra/50">Pipeline 7 dias</div>
            <div className="font-display text-xl">{totalKg} kg</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-preto-terra/50">Agricultores</div>
            <div className="font-display text-xl">{totalSuppliers}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-preto-terra/50">Origem</div>
            <div className="font-display text-xl">Maluana · Marracuene</div>
          </div>
        </div>
      </header>

      <section className="flex-1 overflow-y-auto px-5 py-4">
        {loading && snaps.length === 0 && <p className="text-sm italic text-preto-terra/50">A carregar…</p>}
        {contacted && (
          <div className="mb-3 rounded-md bg-verde-capim px-3 py-2 text-xs uppercase tracking-widest text-sisal">
            ✓ Pedido enviado a {contacted}
          </div>
        )}
        <ul className="space-y-3">
          {Object.entries(CATALOG).map(([crop, suppliers]) => {
            const snap = snapshotFor(crop);
            const cropTotalKg = suppliers.reduce((s, sup) => s + sup.estimatedKg, 0);
            return (
              <li key={crop} className="rounded-2xl bg-white px-4 py-3 shadow-sm">
                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="font-display text-xl capitalize">{crop}</span>
                    <span className="ml-3 text-[11px] uppercase tracking-widest text-preto-terra/60">
                      {cropTotalKg} kg disponíveis · {suppliers.length} agricultor{suppliers.length === 1 ? "" : "es"}
                    </span>
                  </div>
                  {snap && snap.median_wholesale !== null && (
                    <span className="text-[11px] uppercase tracking-widest text-terracota">
                      grossista {range(snap.min_wholesale, snap.max_wholesale, snap.median_wholesale)} MZN/kg
                    </span>
                  )}
                </div>
                <ul className="mt-2 divide-y divide-preto-terra/10">
                  {suppliers.map((sup) => {
                    const q = qualityLabel(sup.qualityFlags);
                    return (
                      <li key={sup.phone + crop} className="flex items-center justify-between gap-3 py-2">
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium">{sup.name}</div>
                          <div className="text-[11px] uppercase tracking-widest text-preto-terra/50">
                            {sup.location} · {sup.weeks} sem · {sup.estimatedKg} kg
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span
                            className="rounded-full px-2 py-1 text-[10px] uppercase tracking-widest text-sisal"
                            style={{ background: q.color }}
                          >
                            {q.label}
                          </span>
                          <button
                            type="button"
                            onClick={() => contact(sup, crop)}
                            className="rounded-md bg-preto-terra px-3 py-2 text-[10px] uppercase tracking-widest text-sisal"
                          >
                            Contactar
                          </button>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              </li>
            );
          })}
        </ul>

        <p className="mt-4 text-center text-[10px] uppercase tracking-widest text-preto-terra/40">
          Pipeline based on Memory + Managed Agent vigilance · sample data for demo
        </p>
      </section>
    </main>
  );
}
