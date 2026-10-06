#!/usr/bin/env python3
"""La pagina dei registri: lo stato della documentazione esplorativa a colpo d'occhio.

Legge i registri con il parser di `registri.py` (gli stessi conteggi di `registri.py riepilogo`)
e fa una pagina HTML senza dipendenze: quante voci sono aperte e chiuse per registro, gli esiti
degli esperimenti, il lavoro per fase, le ipotesi aperte per impatto, e ogni voce con la sua
descrizione completa. Ogni ID è un link alla sua voce, e ogni voce dice chi la cita.

    overview.py                              scrive research-flow.html nella radice del repo
    overview.py --out <file>                 scrive la pagina altrove
    overview.py --serve                      http://localhost:8099, rifatta dai registri a ogni ricarica
    overview.py --serve --host 0.0.0.0       raggiungibile dalla rete (senza password)
    overview.py --serve --port 9000

Opzione comune: --root <dir> (default: la radice git della cartella corrente).
Solo libreria standard, Python 3.9+.
"""

from __future__ import annotations

import argparse
import html
import http.server
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registri as rf  # noqa: E402

ROOT = Path.cwd()  # la radice del repo, fissata da main()
OUT_DEFAULT = "research-flow.html"
PORTA_DEFAULT = 8099


# --- testo ---------------------------------------------------------------------------------

def corto(testo: str, n: int = 150) -> str:
    testo = testo.strip()
    m = re.match(r"^\*\*(.+?)\*\*", testo)
    if m and len(m.group(1)) <= n:
        return m.group(1)
    if len(testo) <= n:
        return testo
    taglio = testo[:n].rsplit(" ", 1)[0]
    if taglio.count("`") % 2:
        taglio = taglio.rsplit("`", 1)[0]
    if taglio.count("**") % 2:
        taglio = taglio.rsplit("**", 1)[0]
    return taglio.rstrip(",;:.(") + "…"


def celle(v) -> list[str]:
    return rf.split_row(v.testo) if v.forma == "tabella" else []


PUNTO = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


class Testo:
    """Il markdown dei registri in HTML, con ogni ID (`ESP-001`, `TODO-F01`…) cliccabile.

    I registri usano liste annidate, grassetto, codice (anche su più righe) e qualche corsivo:
    niente tabelle dentro le voci, niente link.
    """

    def __init__(self, prefissi: list[str], noti: set[str]):
        self.id_re = rf.id_pattern(prefissi)
        self.noti = noti

    def rimandi(self, s: str) -> str:
        def a(m):
            i = m.group(1)
            if i in self.noti:
                return f'<a class="ref" href="#{i}">{i}</a>'
            return f'<span class="ref-x" title="voce non trovata nei registri">{i}</span>'
        return self.id_re.sub(a, s)

    def ids(self, s: str) -> list[str]:
        return list(dict.fromkeys(self.id_re.findall(s)))

    def inline(self, s: str) -> str:
        codici: list[str] = []

        def salva(m):
            codici.append(m.group(1))
            return f"\x00{len(codici) - 1}\x00"

        s = re.sub(r"`([^`]+)`", salva, s)
        s = self.rimandi(html.escape(s, quote=False))
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", s)
        return re.sub(r"\x00(\d+)\x00", lambda m: "<code>" + self.rimandi(
            html.escape(codici[int(m.group(1))], quote=False)) + "</code>", s)

    def blocchi(self, righe: list[str]) -> str:
        out: list[str] = []
        para: list[str] = []
        punti: list[list] = []  # [rientro, numerata, testo]

        def chiudi_para():
            if para:
                out.append(f"<p>{self.inline(' '.join(para))}</p>")
                para.clear()

        def chiudi_lista():
            if punti:
                out.append(self.lista(punti))
                punti.clear()

        vuota = False
        for riga in righe:
            r = riga.rstrip()
            if not r.strip():
                chiudi_para()
                vuota = True
                continue
            if r.strip() == "---":
                chiudi_para()
                chiudi_lista()
                continue
            m = PUNTO.match(r)
            if m:
                chiudi_para()
                punti.append([len(m.group(1).expandtabs()), m.group(2)[0].isdigit(), m.group(3).strip()])
            elif punti and (r.startswith(" ") or not vuota):
                punti[-1][2] += " " + r.strip()
            else:
                chiudi_lista()
                para.append(r.strip())
            vuota = False
        chiudi_para()
        chiudi_lista()
        return "".join(out)

    def lista(self, punti: list[list]) -> str:
        h: list[str] = []
        pila: list[tuple[int, str]] = []
        for rientro, numerata, testo in punti:
            tag = "ol" if numerata else "ul"
            if not pila or rientro > pila[-1][0]:
                h.append(f"<{tag}>")
                pila.append((rientro, tag))
            else:
                while len(pila) > 1 and rientro < pila[-1][0]:
                    h.append(f"</li></{pila.pop()[1]}>")
                h.append("</li>")
            h.append(f"<li>{self.inline(testo)}")
        while pila:
            h.append(f"</li></{pila.pop()[1]}>")
        return "".join(h)


_righe_file: dict[str, list[str]] = {}


def righe_di(rel: str) -> list[str]:
    if rel not in _righe_file:
        _righe_file[rel] = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    return _righe_file[rel]


def sorgente(v) -> tuple[list[str], list[str]]:
    """Il testo completo di una voce: per la forma a intestazione le righe sotto il titolo fino
    al titolo successivo dello stesso livello; per la tabella (intestazione, celle)."""
    righe = righe_di(v.file)
    if v.forma == "tabella":
        i = v.riga - 1
        inizio = i
        while inizio > 0 and righe[inizio - 1].startswith("|"):
            inizio -= 1
        return rf.split_row(righe[inizio]), rf.split_row(righe[i])
    livello = len(righe[v.riga - 1]) - len(righe[v.riga - 1].lstrip("#"))
    fine = v.riga
    while fine < len(righe) and not re.match(rf"^#{{1,{livello}}}\s", righe[fine]):
        fine += 1
    corpo = righe[v.riga:fine]
    while corpo and corpo[-1].strip() in ("", "---"):
        corpo.pop()
    return [], corpo


# --- lettura -------------------------------------------------------------------------------

def stato_di(v) -> str:
    return rf.norm_stato(v.stato) if v.stato else "—"


def impatto(v) -> str | None:
    m = re.search(r"\*\*Impatto:\*\*\s*(alto|medio|basso)", v.testo, re.I)
    return m.group(1).lower() if m else None


def fatto(v) -> bool:
    return v.sezione == "Fatto" or stato_di(v).startswith("fatto")


def todo_info(v) -> dict:
    """Priorità, titolo e fase di una voce di da fare: le righe delle fasi hanno la colonna
    «Pri.», quelle fatte possono cominciare con «Fase N, P0.»."""
    c = celle(v)
    if fatto(v):
        cosa = c[1] if len(c) > 1 else v.titolo
        m = re.match(r"^Fase (\d)[,.]\s*(P\d)?\.?\s*", cosa)
        fase = f"Fase {m.group(1)}" if m else "Fatti senza fase"
        return {"pri": m.group(2) if m and m.group(2) else None,
                "cosa": cosa[m.end():] if m else cosa, "fase": fase,
                "nota": c[2] if len(c) > 2 else ""}
    if len(c) > 2 and re.fullmatch(r"P\d", c[1]):
        pri, cosa = c[1], c[2]
    else:
        pri, cosa = None, c[1] if len(c) > 1 else v.titolo
    m = re.match(r"^(Fase \d)", v.sezione)
    return {"pri": pri, "cosa": cosa, "fase": m.group(1) if m else v.sezione,
            "nota": v.stato or ""}


def domande(cfg: dict) -> list[tuple[str, list[str]]]:
    """Le sezioni «Da chiedere…» del registro da fare (alle fonti, a una persona): titolo e righe."""
    reg = cfg["registri"].get("da_fare")
    path = ROOT / cfg["dir"] / reg["file"] if reg else None
    if not path or not path.exists():
        return []
    testo = path.read_text(encoding="utf-8")
    return [(m.group(1).strip(), m.group(2).splitlines())
            for m in re.finditer(r"^## (Da chiedere[^\n]*)\n(.*?)(?=^## |\Z)", testo, re.M | re.S)]


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


# --- pezzi di pagina -----------------------------------------------------------------------

def barra(segmenti: list[tuple[str, int, str]], titolo: str = "") -> str:
    """Barra impilata: (etichetta, valore, classe di colore)."""
    tot = sum(n for _, n, _ in segmenti) or 1
    parti = "".join(
        f'<span class="seg {cls}" style="flex-grow:{n}" title="{html.escape(et)}: {n}"></span>'
        for et, n, cls in segmenti if n
    )
    return f'<div class="bar" role="img" aria-label="{html.escape(titolo)}">{parti}</div>' if tot else ""


def legenda(segmenti: list[tuple[str, int, str]]) -> str:
    return '<ul class="legend">' + "".join(
        f'<li><span class="dot {cls}"></span><b>{n}</b> {html.escape(et)}</li>'
        for et, n, cls in segmenti if n
    ) + "</ul>"


def chip(testo: str, cls: str) -> str:
    return f'<span class="chip {cls}">{html.escape(testo)}</span>'


def chip_ref(i: str, cls: str, testo: str | None = None) -> str:
    return f'<a class="chip ref {cls}" href="#{i}">{html.escape(testo or i)}</a>'


def dettagli(titolo: str, n: int, corpo: str, id_: str) -> str:
    return (f'<details class="reg" id="{id_}"><summary>{html.escape(titolo)} '
            f'<span class="count">{n}</span></summary>{corpo}</details>')


JS = """
(function () {
  const lento = !matchMedia('(prefers-reduced-motion: reduce)').matches;
  function apriAntenati(el) {
    for (let p = el; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true;
  }
  function vai(id) {
    const el = document.getElementById(id);
    if (!el) return;
    apriAntenati(el);
    el.scrollIntoView({ block: 'start', behavior: lento ? 'smooth' : 'auto' });
    el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
  }
  document.addEventListener('click', function (e) {
    const a = e.target.closest('a.ref');
    if (!a) return;
    e.preventDefault(); e.stopPropagation();
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) apriAntenati(el);
    if (location.hash === '#' + id) vai(id); else location.hash = id;
  });
  window.addEventListener('hashchange', function () { vai(decodeURIComponent(location.hash.slice(1))); });
  if (location.hash) vai(decodeURIComponent(location.hash.slice(1)));
  document.querySelectorAll('[data-tutte]').forEach(function (b) {
    b.addEventListener('click', function () {
      const apri = b.dataset.tutte === 'apri';
      document.querySelectorAll('details.reg, details.voce').forEach(function (d) { d.open = apri; });
    });
  });
})();
"""


CSS = """
:root {
  /* Layout: intestazione, cinque registri in griglia, due pannelli (esperimenti, fasi), elenchi a scomparsa. */
  --bg: #f6f7f9; --surface: #ffffff; --border: #d9dde4; --text: #16191f; --muted: #5b6472;
  --accent: #2856d6; --accent-soft: rgba(40, 86, 214, 0.12);
  --pos: #16803c; --neg: #c62828; --warn: #9a6200; --idle: #a9b0bb; --track: #e3e6ec;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f1216; --surface: #171b21; --border: #2c333d; --text: #e6e9ee; --muted: #9aa3b0;
  --accent: #7ea2ff; --accent-soft: rgba(126, 162, 255, 0.16);
  --pos: #4cc27a; --neg: #ff6b6b; --warn: #e0a640; --idle: #5d6673; --track: #262c35;
  color-scheme: dark;
} }
:root[data-theme="dark"] {
  --bg: #0f1216; --surface: #171b21; --border: #2c333d; --text: #e6e9ee; --muted: #9aa3b0;
  --accent: #7ea2ff; --accent-soft: rgba(126, 162, 255, 0.16);
  --pos: #4cc27a; --neg: #ff6b6b; --warn: #e0a640; --idle: #5d6673; --track: #262c35;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font: 14px/1.5 var(--font); margin: 0; }
.wrap { max-width: 1120px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 56px;
  display: grid; gap: 28px; }
header { display: grid; gap: 6px; }
h1 { font-size: 24px; margin: 0; letter-spacing: -0.01em; text-wrap: balance; }
h2 { font-size: 13px; margin: 0; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 600; }
.meta { color: var(--muted); font-size: 13px; }
.meta code, .id, .count, .num { font-family: var(--mono); font-variant-numeric: tabular-nums; }
.totals { display: flex; flex-wrap: wrap; gap: 8px 28px; font-size: 15px; }
.totals b { font-size: 22px; font-family: var(--mono); margin-right: 4px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 14px 16px; display: grid; gap: 10px; align-content: start; min-width: 0; }
.card .big { display: flex; align-items: baseline; gap: 8px; }
.card .big .num { font-size: 34px; font-weight: 600; line-height: 1; }
.card .big .of { color: var(--muted); font-size: 13px; }
.card .what { font-size: 13px; color: var(--muted); }
.bar { display: flex; height: 10px; border-radius: 5px; overflow: hidden; background: var(--track); gap: 2px; }
.bar.tall { height: 16px; }
.seg { display: block; min-width: 3px; }
.legend { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 13px; }
.legend li { display: flex; align-items: center; gap: 6px; }
.legend b { font-family: var(--mono); font-weight: 600; }
.dot { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
.c-open { background: var(--warn); } .c-run { background: var(--accent); } .c-done { background: var(--pos); }
.c-neg { background: var(--neg); } .c-idle { background: var(--idle); } .c-p2 { background: var(--idle); }
.panels { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px; display: grid; gap: 14px; align-content: start; min-width: 0; }
.rows { display: grid; gap: 10px; }
.row { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 10px; align-items: center; font-size: 13px; }
.row > .bar, .row > .chips { grid-column: 1 / -1; }
.row .lab { min-width: 0; }
.row .val { font-family: var(--mono); color: var(--muted); white-space: nowrap; }
.chips { display: flex; flex-wrap: wrap; gap: 4px; }
.chip { font: 12px/1.6 var(--mono); padding: 0 6px; border-radius: 4px; border: 1px solid var(--border); white-space: nowrap; }
.chip.k-pos { color: var(--pos); } .chip.k-neg { color: var(--neg); } .chip.k-warn { color: var(--warn); }
.chip.k-idle { color: var(--muted); } .chip.k-run { color: var(--accent); background: var(--accent-soft); border-color: transparent; }
a.chip { text-decoration: none; }
a.chip:hover, a.chip:focus-visible { border-color: currentColor; }
a.ref:not(.chip) { color: var(--accent); text-decoration: none; font-family: var(--mono); font-size: 0.92em; white-space: nowrap; }
a.ref:not(.chip):hover { text-decoration: underline; }
a.ref:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; border-radius: 3px; }
a.plain { color: inherit; text-decoration: none; }
a.plain:hover { text-decoration: underline; }
.ref-x { font-family: var(--mono); font-size: 0.92em; color: var(--muted); text-decoration: line-through dotted; }
.lists { display: grid; gap: 8px; }
.lists-head { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between; }
.btns { display: flex; gap: 6px; }
button { font: 13px var(--font); color: var(--text); background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 10px; cursor: pointer; }
button:hover { border-color: var(--accent); }
button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
details.reg { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0 16px; min-width: 0; scroll-margin-top: 12px; }
details.reg > summary { cursor: pointer; padding: 12px 0; font-weight: 600; display: flex; gap: 8px; align-items: center; }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
.count { color: var(--muted); font-weight: 400; }
details.reg > div { padding-bottom: 12px; display: grid; }
details.reg h3 { font-size: 12px; margin: 14px 0 4px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
details.voce { border-top: 1px solid var(--track); scroll-margin-top: 12px; min-width: 0; }
details.voce > summary { list-style: none; cursor: pointer; display: grid;
  grid-template-columns: 0.9em 6.5em minmax(0, 1fr) auto; gap: 4px 10px; padding: 7px 0; align-items: baseline; }
details.voce > summary::-webkit-details-marker { display: none; }
details.voce > summary::before { content: "▸"; color: var(--muted); font-size: 11px; transition: transform .15s; }
details.voce[open] > summary::before { transform: rotate(90deg); }
details.voce > summary:hover .t { color: var(--accent); }
.voce .id { color: var(--muted); font-size: 12.5px; }
.voce .t { min-width: 0; overflow-wrap: anywhere; }
.voce .tail { display: flex; flex-wrap: wrap; gap: 4px; justify-content: flex-end; }
.voce.flash > summary { animation: flash 1.8s ease-out; }
@keyframes flash { from { background: var(--accent-soft); } to { background: transparent; } }
@media (prefers-reduced-motion: reduce) { .voce.flash > summary { animation: none; background: var(--accent-soft); } }
.desc { margin: 0 0 12px calc(0.9em + 10px); padding: 10px 14px; border-left: 2px solid var(--track);
  max-width: 88ch; display: grid; gap: 8px; min-width: 0; overflow-wrap: anywhere; }
.desc p, .desc ul, .desc ol, .desc dl { margin: 0; }
.desc ul, .desc ol { padding-left: 1.3em; display: grid; gap: 4px; }
.desc li > ul, .desc li > ol { margin-top: 4px; }
.desc code, details.reg code { font-family: var(--mono); font-size: 0.88em; background: var(--track); padding: 0 3px; border-radius: 3px; }
.desc dt { font-weight: 600; font-size: 13px; color: var(--muted); }
.desc dd { margin: 0 0 6px; }
.desc .piede { font-size: 12.5px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: baseline; }
.desc .piede code { background: none; padding: 0; }
.empty { color: var(--muted); margin: 0 0 8px; }
@media (max-width: 560px) {
  details.voce > summary { grid-template-columns: 0.9em minmax(0, 1fr) auto; }
  .voce .t { grid-column: 2 / -1; grid-row: 2; }
  .desc { margin-left: 0; }
}
"""


# --- pagina --------------------------------------------------------------------------------

def pagina() -> str:
    cfg = rf.load_config(ROOT)
    voci, _ = rf.carica_voci(ROOT, cfg)
    per = {t: [v for v in voci if v.tipo == t] for t in cfg["registri"]}

    dub, ip, ver, esp, todo = (per.get(t, []) for t in
                               ("dubbi", "ipotesi", "verificato", "esperimenti", "da_fare"))

    tx = Testo([r["prefisso"] for r in cfg["registri"].values()], {v.id for v in voci})
    testi = {v.id: sorgente(v) for v in voci}
    citata_da: dict[str, list[str]] = {}
    for v in voci:
        intest, corpo = testi[v.id]
        for i in tx.ids("\n".join(corpo)):
            if i != v.id:
                citata_da.setdefault(i, []).append(v.id)

    def descrizione(v) -> str:
        intest, corpo = testi[v.id]
        if v.forma == "tabella":
            h = "<dl>" + "".join(
                f"<dt>{html.escape(t)}</dt><dd>{tx.inline(c) or '—'}</dd>"
                for t, c in zip(intest[1:], corpo[1:])
            ) + "</dl>"
        else:
            h = f"<p><strong>{tx.inline(v.titolo)}</strong></p>{tx.blocchi(corpo)}"
        cit = citata_da.get(v.id, [])
        piede = f'<code>{html.escape(v.file)}:{v.riga}</code>'
        if cit:
            piede += " · citata da " + " ".join(tx.rimandi(i) for i in cit)
        return f'<div class="desc">{h}<div class="piede">{piede}</div></div>'

    def voce(v, titolo: str, coda: str = "") -> str:
        return (f'<details class="voce" id="{v.id}"><summary><span class="id">{v.id}</span>'
                f'<span class="t">{tx.inline(corto(titolo))}</span><span class="tail">{coda}</span>'
                f'</summary>{descrizione(v)}</details>')

    def elenco(righe: list[tuple], vuoto: str = "Nessuna voce.") -> str:
        """Righe (voce, titolo in markdown, coda in html)."""
        if not righe:
            return f'<p class="empty">{vuoto}</p>'
        return "".join(voce(*r) for r in righe)

    def conta(vs, *stati):
        return sum(1 for v in vs if stato_di(v) in stati)

    # uno stato che METODO.md non prevede conta fra gli aperti, per non sparire dalla pagina
    dub_aperti = [v for v in dub if stato_di(v) not in ("accettato", "risolto")]
    ip_aperte = [v for v in ip if stato_di(v) != "→ VER"]
    # dubbi
    dub_seg = [("aperti", len(dub_aperti) - conta(dub, "in lavorazione"), "c-open"),
               ("in lavorazione", conta(dub, "in lavorazione"), "c-run"),
               ("accettati così", conta(dub, "accettato"), "c-idle"),
               ("risolti", conta(dub, "risolto"), "c-done")]
    # ipotesi
    ip_seg = [("da verificare", len(ip_aperte) - conta(ip, "in verifica"), "c-open"),
              ("in verifica", conta(ip, "in verifica"), "c-run"),
              ("chiuse in verificato", conta(ip, "→ VER"), "c-done")]
    # esperimenti
    esp_seg = [("proposti", len(esp) - conta(esp, "in corso", "concluso"), "c-open"),
               ("in corso", conta(esp, "in corso"), "c-run"),
               ("conclusi", conta(esp, "concluso"), "c-done")]
    # da fare
    todo_inf = {v.id: todo_info(v) for v in todo}
    fatti = [v for v in todo if fatto(v)]
    aperti_todo = [v for v in todo if not fatto(v)]
    todo_seg = [("da fare", sum(1 for v in aperti_todo if stato_di(v) == "da fare"), "c-open"),
                ("in corso o in parte", sum(1 for v in aperti_todo if stato_di(v) != "da fare"), "c-run"),
                ("fatti", len(fatti), "c-done")]
    # verificato
    sez_ver: dict[str, int] = {}
    for v in ver:
        sez_ver[v.sezione] = sez_ver.get(v.sezione, 0) + 1
    ver_cls = ["c-run", "c-done", "c-idle", "c-open"]
    ver_seg = [(s, n, ver_cls[i % len(ver_cls)]) for i, (s, n) in enumerate(sez_ver.items())]

    sez_domande = [(t, r, sum(1 for x in r if PUNTO.match(x) and not x.startswith(" ")))
                   for t, r in domande(cfg)]
    n_domande = sum(n for _, _, n in sez_domande)

    def card(nome, aperti, cosa, seg, file, ancora):
        tot = sum(n for _, n, _ in seg)
        return (f'<section class="card" aria-label="{html.escape(nome)}">'
                f'<h2><a class="ref plain" href="#reg-{ancora}">{html.escape(nome)}</a></h2>'
                f'<div class="big"><span class="num">{aperti}</span><span class="of">su {tot}</span></div>'
                f'<div class="what">{cosa} · <code>{html.escape(file)}</code></div>'
                f'{barra(seg, nome)}{legenda(seg)}</section>')

    aperti_dub = dub_seg[0][1] + dub_seg[1][1]
    aperti_ip = ip_seg[0][1] + ip_seg[1][1]
    aperti_esp = esp_seg[0][1] + esp_seg[1][1]
    aperti_todo_n = todo_seg[0][1] + todo_seg[1][1]
    def file_di(tipo):
        return cfg["registri"].get(tipo, {}).get("file", "—")

    cards = "".join([
        card("Dubbi", aperti_dub, "dubbi sul codice aperti", dub_seg, file_di("dubbi"), "dubbi"),
        card("Ipotesi", aperti_ip, "ipotesi ancora da verificare", ip_seg, file_di("ipotesi"), "ipotesi"),
        card("Esperimenti", aperti_esp, "esperimenti da fare", esp_seg, file_di("esperimenti"), "esperimenti"),
        card("Da fare", aperti_todo_n, "lavori aperti", todo_seg, file_di("da_fare"), "da-fare"),
        card("Verificato", len(ver), "fatti verificati", ver_seg, file_di("verificato"), "verificato"),
    ])

    totali = (
        f'<div class="totals"><span><b>{aperti_dub + aperti_ip + aperti_esp + aperti_todo_n}</b>cose aperte</span>'
        f'<span><b>{dub_seg[3][1] + dub_seg[2][1] + ip_seg[2][1] + esp_seg[2][1] + len(fatti)}</b>chiuse</span>'
        f'<span><b>{len(ver)}</b>fatti verificati</span>'
        + (f'<span><a class="ref plain" href="#domande-1"><b>{n_domande}</b>domande aperte alle fonti</a></span>'
           if sez_domande else "")
        + '</div>'
    )

    # esiti degli esperimenti
    esiti_cls = {"positivo": ("c-done", "k-pos"), "negativo": ("c-neg", "k-neg"),
                 "inconcludente": ("c-open", "k-warn"), "abbandonato": ("c-idle", "k-idle")}
    per_esito: dict[str, list[str]] = {e: [] for e in esiti_cls}
    for v in esp:
        e = rf.esito(v)
        if e:
            per_esito[e].append(v.id)
    es_seg = [(e, len(ids), esiti_cls[e][0]) for e, ids in per_esito.items()]
    es_righe = "".join(
        f'<div class="row"><span class="lab">{e}</span><span class="val">{len(ids)}</span>'
        f'<div class="chips">{"".join(chip_ref(i, esiti_cls[e][1]) for i in sorted(ids))}</div></div>'
        for e, ids in per_esito.items() if ids
    )
    pannello_esiti = (
        f'<section class="panel"><h2>Esiti degli esperimenti conclusi</h2>'
        f'{barra(es_seg, "esiti")}{legenda(es_seg)}<div class="rows">{es_righe}</div></section>'
    ).replace('class="bar"', 'class="bar tall"', 1)

    # da fare per fase
    fasi: dict[str, dict[str, int]] = {}
    for v in todo:
        inf = todo_inf[v.id]
        f = fasi.setdefault(inf["fase"], {"P0": 0, "P1": 0, "P2": 0, "—": 0, "fatti": 0})
        if fatto(v):
            f["fatti"] += 1
        else:
            f[inf["pri"] or "—"] += 1
    nomi_fase = {re.match(r"^(Fase \d)", s).group(1): s
                 for s in (v.sezione for v in todo) if re.match(r"^Fase \d", s)}
    ordine = sorted(fasi, key=lambda f: (f != "In corso", not f.startswith("Fase"), f))
    righe_fase = ""
    for f in ordine:
        c = fasi[f]
        seg = [("P0 aperti", c["P0"], "c-neg"), ("P1 aperti", c["P1"], "c-open"),
               ("P2 aperti", c["P2"], "c-p2"), ("aperti", c["—"], "c-run"),
               ("fatti", c["fatti"], "c-done")]
        aperti = c["P0"] + c["P1"] + c["P2"] + c["—"]
        righe_fase += (f'<div class="row"><span class="lab">'
                       f'{html.escape(nomi_fase.get(f, f))}</span>'
                       f'<span class="val">{aperti} aperti · {c["fatti"]} fatti</span>{barra(seg, f)}</div>')
    pannello_fasi = (
        f'<section class="panel"><h2>Da fare per fase</h2><div class="rows">{righe_fase}</div>'
        f'{legenda([("P0 blocca le fasi dopo", sum(c["P0"] for c in fasi.values()), "c-neg"), ("P1 serve prima del traguardo", sum(c["P1"] for c in fasi.values()), "c-open"), ("P2 migliora", sum(c["P2"] for c in fasi.values()), "c-p2"), ("in corso", sum(c["—"] for c in fasi.values()), "c-run"), ("fatti", len(fatti), "c-done")])}'
        f'</section>'
    )

    # ipotesi aperte per impatto
    imp_cls = {"alto": "k-neg", "medio": "k-warn", "basso": "k-idle"}
    imp_cont = {k: sum(1 for v in ip_aperte if impatto(v) == k) for k in imp_cls}
    imp_seg = [("impatto alto", imp_cont["alto"], "c-neg"), ("medio", imp_cont["medio"], "c-open"),
               ("basso", imp_cont["basso"], "c-idle")]
    senza = len(ip_aperte) - sum(imp_cont.values())
    if senza:
        imp_seg.append(("impatto non scritto", senza, "c-run"))
    pannello_imp = (
        f'<section class="panel"><h2>Ipotesi aperte per impatto se sono sbagliate</h2>'
        f'{barra(imp_seg, "impatto")}{legenda(imp_seg)}'
        f'<div class="chips">{"".join(chip_ref(v.id, imp_cls.get(impatto(v) or "", "k-run")) for v in sorted(ip_aperte, key=lambda v: (["alto", "medio", "basso"].index(impatto(v)) if impatto(v) else 3, v.id)))}</div>'
        f'</section>'
    ).replace('class="bar"', 'class="bar tall"', 1)

    # elenchi
    def coda_stato(v, aperto_cls="k-warn"):
        s = stato_di(v)
        cls = {"aperto": aperto_cls, "da verificare": aperto_cls, "proposto": aperto_cls,
               "da fare": aperto_cls, "accettato": "k-idle", "risolto": "k-pos", "→ VER": "k-pos",
               "concluso": "k-pos"}.get(s, "k-run")
        if s == "→ VER":
            m = re.search(r"VER-\d+", v.stato or "")
            if m:
                return chip_ref(m.group(0), cls, f"→ {m.group(0)}")
        return chip(s, cls)

    def imp_chip(v):
        i = impatto(v)
        return chip(f"impatto {i}", imp_cls[i]) + " " if i else ""

    l_dub = (
        f'<div><h3>Aperti</h3>{elenco([(v, v.titolo, coda_stato(v)) for v in dub_aperti])}'
        f'<h3>Accettati così</h3>{elenco([(v, v.titolo, coda_stato(v)) for v in dub if stato_di(v) == "accettato"])}'
        f'<h3>Risolti</h3>{elenco([(v, v.titolo, coda_stato(v)) for v in dub if stato_di(v) == "risolto"])}</div>'
    )
    l_ip = (
        f'<div><h3>Da verificare</h3>{elenco([(v, v.titolo, imp_chip(v) + coda_stato(v)) for v in ip_aperte])}'
        f'<h3>Chiuse</h3>{elenco([(v, v.titolo, coda_stato(v)) for v in ip if stato_di(v) == "→ VER"])}</div>'
    )
    l_esp = (
        f'<div><h3>Da fare</h3>{elenco([(v, v.titolo, coda_stato(v)) for v in esp if stato_di(v) != "concluso"])}'
        f'<h3>Conclusi</h3>{elenco([(v, v.titolo, chip(rf.esito(v) or "senza esito", esiti_cls.get(rf.esito(v) or "", ("", "k-run"))[1])) for v in esp if stato_di(v) == "concluso"])}</div>'
    )

    def todo_riga(v):
        inf = todo_inf[v.id]
        pri = chip(inf["pri"], {"P0": "k-neg", "P1": "k-warn", "P2": "k-idle"}[inf["pri"]]) + " " if inf["pri"] else ""
        return (v, inf["cosa"], pri + (chip("fatto", "k-pos") if fatto(v) else coda_stato(v)))

    blocchi_todo = ""
    for f in ordine:
        vs = [v for v in aperti_todo if todo_inf[v.id]["fase"] == f]
        if vs:
            blocchi_todo += f'<h3>{html.escape(nomi_fase.get(f, f))}</h3>{elenco([todo_riga(v) for v in vs])}'
    blocchi_todo += f'<h3>Fatti</h3>{elenco([todo_riga(v) for v in fatti])}'

    l_ver = "".join(
        f'<h3>{html.escape(s)}</h3>{elenco([(v, v.titolo, "") for v in ver if v.sezione == s])}'
        for s in sez_ver
    )

    liste = "".join([
        dettagli("Dubbi", len(dub), l_dub, "reg-dubbi"),
        dettagli("Ipotesi", len(ip), l_ip, "reg-ipotesi"),
        dettagli("Esperimenti", len(esp), l_esp, "reg-esperimenti"),
        dettagli("Da fare", len(todo), f"<div>{blocchi_todo}</div>", "reg-da-fare"),
        dettagli("Verificato", len(ver), f"<div>{l_ver}</div>", "reg-verificato"),
    ] + [
        dettagli(t, n, f'<div class="desc">{tx.blocchi(r)}</div>', f"domande-{k}")
        for k, (t, r, n) in enumerate(sez_domande, 1)
    ])

    commit = git("log", "-1", "--format=%h")
    data_commit = git("log", "-1", "--date=format:%d-%m-%Y %H:%M", "--format=%cd")
    sporco = " · con modifiche non committate" if git("status", "--porcelain", "--", cfg["dir"]) else ""
    adesso = datetime.now().strftime("%d-%m-%Y %H:%M")
    nome = html.escape(ROOT.name)
    al_commit = f' al commit <code>{commit}</code> del {data_commit}' if commit else ""

    return f"""<!doctype html>
<html lang="it">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Registri {nome}</title>
<style>{CSS}</style>
<main class="wrap">
  <header>
    <h1>Stato della ricerca · {nome}</h1>
    <p class="meta" style="margin:0">Registri di <code>{html.escape(cfg["dir"])}/</code>{al_commit}{sporco} · pagina generata il {adesso}</p>
  </header>
  {totali}
  <div class="grid">{cards}</div>
  <div class="panels">{pannello_esiti}{pannello_fasi}{pannello_imp}</div>
  <section class="lists" aria-label="Elenchi">
    <div class="lists-head"><h2>Le voci</h2><div class="btns">
      <button type="button" id="apri-tutte" data-tutte="apri">Apri tutte</button>
      <button type="button" id="chiudi-tutte" data-tutte="chiudi">Chiudi tutte</button></div></div>
    {liste}
  </section>
</main>
<script>{JS}</script>
</html>
"""


class Pagina(http.server.BaseHTTPRequestHandler):
    """Rilegge i registri a ogni richiesta: basta ricaricare il browser."""

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        corpo = pagina().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass


def main() -> int:
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, help="default: la radice git della cartella corrente")
    ap.add_argument("--out", type=Path, help=f"default: <root>/{OUT_DEFAULT}")
    ap.add_argument("--serve", action="store_true", help="server locale invece del file")
    ap.add_argument("--port", type=int, default=PORTA_DEFAULT)
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 per la rete")
    a = ap.parse_args()
    ROOT = (a.root or rf.git_root(Path.cwd())).resolve()
    if not (ROOT / rf.CONFIG_NAME).exists() and not (ROOT / "research").is_dir():
        sys.exit(f"{ROOT}: né {rf.CONFIG_NAME} né research/. Lancia /research-flow:init o passa --root.")
    if a.serve:
        server = http.server.ThreadingHTTPServer((a.host, a.port), Pagina)
        dove = {"127.0.0.1": "localhost", "0.0.0.0": "<indirizzo della macchina>"}.get(a.host, a.host)
        print(f"Registri di {ROOT.name} su http://{dove}:{a.port} (Ctrl+C per fermare)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        return 0
    out = a.out or ROOT / OUT_DEFAULT
    out.write_text(pagina(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
