#!/usr/bin/env python3
"""Registri della documentazione esplorativa: ID, citazioni e controlli di coerenza.

Legge `.research-flow.json` nella radice del repo (vedi templates/research-flow.json) e lavora
sui registri che elenca. Non modifica mai un file: dice cosa c'è e cosa non torna, le skill
decidono cosa scrivere.

    registri.py next IP           l'ID successivo di un registro (per prefisso o per tipo)
    registri.py find IP-003       dove è definita una voce e chi la cita
    registri.py riepilogo         le voci per registro e per stato, in JSON
    registri.py check [--json]    i controlli di coerenza; exit 1 se c'è almeno un errore
    registri.py stale             i documenti cambiati dopo l'ultimo aggiornamento di graphify

Opzione comune: --root <dir> (default: la radice git della cartella corrente).
Solo libreria standard, Python 3.9+.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

CONFIG_NAME = ".research-flow.json"

DEFAULT_CONFIG = {
    "dir": "research",
    "registri": {
        "dubbi": {"file": "dubbi_implementazione.md", "prefisso": "DUB"},
        "ipotesi": {"file": "ipotesi_da_verificare.md", "prefisso": "IP"},
        "verificato": {"file": "verificato.md", "prefisso": "VER"},
        "esperimenti": {"file": "esperimenti.md", "prefisso": "ESP"},
        "da_fare": {"file": "da_fare.md", "prefisso": "TODO"},
    },
    "ufficiale": "stato_progetto.md",
    # i campi obbligatori delle voci scritte come intestazione (### ID · titolo)
    "campi": {
        "dubbi": ["Dove", "Stato"],
        "ipotesi": ["Come si verifica", "Impatto", "Stato"],
        "esperimenti": ["Domanda", "Metodo", "Stato"],
    },
    # dove si cercano le citazioni: glob relativi alla radice del repo
    "scansione": ["**/*.md", "**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.sql", "**/*.yml"],
    "escludi": [
        ".git/**", "**/node_modules/**", "graphify-out/**", "**/dist/**", "**/build/**",
        "**/.venv/**", "**/venv/**", "**/__pycache__/**",
    ],
    # prefissi citati come ID ma definiti altrove (issue, sistemi esterni): non sono errori
    "prefissi_esterni": [],
    # cartelle di `dir` che si tengono aggiornate (i percorsi citati devono esistere);
    # brainstorm, ricerche iniziali e storico citano file proposti o spariti, e non si controllano
    "vivi": ["fonti/**/*.md", "misure/**/*.md"],
    # percorsi citati che non devono esistere: file proposti, file di altri repo (glob)
    "percorsi_ignora": [],
}

TEXT_EXT = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".yml", ".yaml", ".txt", ".json", ".toml"}
FILE_LIKE = re.compile(
    r"`([^`\s]+?\.(?:md|py|csv|txt|json|ts|tsx|js|jpg|jpeg|png|sql|yml|yaml|ipynb|html))(?:[:§#][^`]*)?`"
)
DATE_RE = re.compile(r"(\d{1,2})-(\d{1,2})-(\d{4})")


# ---------------------------------------------------------------------------- configurazione


def git_root(start: Path) -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=start, capture_output=True, text=True, check=True
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return start


def load_config(root: Path, path: Path | None = None) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    path = path or root / CONFIG_NAME
    if path.exists():
        user = json.loads(path.read_text(encoding="utf-8"))
        for key, value in user.items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict) and key != "registri":
                cfg[key].update(value)
            else:
                cfg[key] = value
    cfg["_trovata"] = path.exists()
    return cfg


# ---------------------------------------------------------------------------- lettura delle voci


@dataclass
class Voce:
    id: str
    tipo: str
    file: str
    riga: int
    titolo: str
    sezione: str
    forma: str  # "intestazione" o "tabella"
    stato: str | None = None
    campi: set[str] = field(default_factory=set)
    testo: str = ""


def id_pattern(prefissi: list[str]) -> re.Pattern:
    alt = "|".join(sorted((re.escape(p) for p in prefissi), key=len, reverse=True))
    return re.compile(rf"(?<![\w-])((?:{alt})-[A-Z]?\d+)(?![\w])")


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_registro(path: Path, tipo: str, prefisso: str, rel: str) -> list[Voce]:
    lines = path.read_text(encoding="utf-8").splitlines()
    head_re = re.compile(rf"^(#{{2,4}})\s+\**({re.escape(prefisso)}-[A-Z]?\d+)\**\s*(?:[·:—–-]\s*)?(.*)$")
    row_re = re.compile(rf"^\|\s*\**({re.escape(prefisso)}-[A-Z]?\d+)\**\s*\|")
    campo_re = re.compile(r"^\s*[-*]\s+\*\*([^*:]+?):?\*\*:?")
    voci: list[Voce] = []
    sezione = ""
    header: list[str] | None = None
    corrente: Voce | None = None
    livello_corrente = 0

    for n, line in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            livello = len(m.group(1))
            hm = head_re.match(line)
            if hm:
                corrente = Voce(hm.group(2), tipo, rel, n, hm.group(3).strip(), sezione, "intestazione")
                livello_corrente = livello
                voci.append(corrente)
            else:
                if corrente is None or livello <= livello_corrente:
                    corrente = None
                if livello == 2:
                    sezione = m.group(2).strip()
            header = None
            continue

        if line.startswith("|"):
            cells = split_row(line)
            if header is None:
                header = [c.strip("* ").lower() for c in cells]
                continue
            if all(set(c) <= set("-: ") for c in cells):
                continue
            rm = row_re.match(line)
            if rm:
                stato = None
                if "stato" in header:
                    i = header.index("stato")
                    stato = cells[i] if i < len(cells) else None
                titolo = cells[1] if len(cells) > 1 else ""
                voci.append(Voce(rm.group(1), tipo, rel, n, titolo, sezione, "tabella", stato, testo=line))
            continue
        header = None

        if corrente is not None:
            corrente.testo += line + "\n"
            cm = campo_re.match(line)
            if cm:
                nome = cm.group(1).strip()
                corrente.campi.add(nome.lower())
                if nome.lower() == "stato":
                    corrente.stato = line.split(":**", 1)[-1].strip() if ":**" in line else line
    return voci


def carica_voci(root: Path, cfg: dict) -> tuple[list[Voce], list[str]]:
    base = root / cfg["dir"]
    voci: list[Voce] = []
    mancanti: list[str] = []
    for tipo, reg in cfg["registri"].items():
        path = base / reg["file"]
        rel = str(path.relative_to(root))
        if not path.exists():
            mancanti.append(rel)
            continue
        voci.extend(parse_registro(path, tipo, reg["prefisso"], rel))
    return voci, mancanti


def file_scansionati(root: Path, cfg: dict) -> list[Path]:
    esclusi = cfg["escludi"]
    visti: set[Path] = set()
    out: list[Path] = []
    for pattern in cfg["scansione"]:
        for p in root.glob(pattern):
            if not p.is_file() or p.suffix not in TEXT_EXT or p in visti:
                continue
            rel = str(p.relative_to(root))
            if any(fnmatch.fnmatch(rel, e) or fnmatch.fnmatch("/" + rel, "*/" + e) for e in esclusi):
                continue
            if p.stat().st_size > 2_000_000:
                continue
            visti.add(p)
            out.append(p)
    return sorted(out)


def citazioni(root: Path, cfg: dict, pattern: re.Pattern) -> dict[str, list[tuple[str, int]]]:
    out: dict[str, list[tuple[str, int]]] = {}
    for p in file_scansionati(root, cfg):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(p.relative_to(root))
        for n, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                out.setdefault(m.group(1), []).append((rel, n))
    return out


def numero(id_: str) -> int | None:
    m = re.search(r"-(\d+)$", id_)
    return int(m.group(1)) if m else None


def prefisso_di(cfg: dict, chiave: str) -> str:
    chiave_u = chiave.upper()
    for tipo, reg in cfg["registri"].items():
        if chiave.lower() == tipo or chiave_u == reg["prefisso"].upper():
            return reg["prefisso"]
    raise SystemExit(f"registro sconosciuto: {chiave} (tipi: {', '.join(cfg['registri'])})")


# ---------------------------------------------------------------------------- comandi


def cmd_next(root: Path, cfg: dict, chiave: str) -> int:
    prefisso = prefisso_di(cfg, chiave)
    voci, _ = carica_voci(root, cfg)
    # anche le citazioni: un ID citato e mai definito è comunque «usato»
    cit = citazioni(root, cfg, id_pattern([prefisso]))
    nums = [numero(v.id) for v in voci if v.id.startswith(prefisso + "-")]
    nums += [numero(i) for i in cit]
    massimo = max((n for n in nums if n is not None), default=0)
    print(f"{prefisso}-{massimo + 1:03d}")
    return 0


def cmd_find(root: Path, cfg: dict, id_: str) -> int:
    id_ = id_.upper()
    prefissi = [r["prefisso"] for r in cfg["registri"].values()]
    voci, _ = carica_voci(root, cfg)
    definizioni = [v for v in voci if v.id == id_]
    cit = citazioni(root, cfg, id_pattern(prefissi)).get(id_, [])
    if not definizioni and not cit:
        print(f"{id_}: nessuna definizione e nessuna citazione")
        return 1
    for v in definizioni:
        print(f"definita  {v.file}:{v.riga}  [{v.sezione}]  {v.titolo[:90]}")
        if v.stato:
            print(f"  stato   {v.stato}")
    if not definizioni:
        print(f"{id_}: citata ma mai definita")
    for f, n in cit:
        if any(v.file == f and v.riga == n for v in definizioni):
            continue
        print(f"citata    {f}:{n}")
    return 0


def cmd_riepilogo(root: Path, cfg: dict) -> int:
    voci, mancanti = carica_voci(root, cfg)
    out: dict = {"registri": {}, "mancanti": mancanti}
    for tipo, reg in cfg["registri"].items():
        vs = [v for v in voci if v.tipo == tipo]
        per_stato: dict[str, int] = {}
        per_sezione: dict[str, int] = {}
        for v in vs:
            chiave = norm_stato(v.stato) if v.stato else "—"
            per_stato[chiave] = per_stato.get(chiave, 0) + 1
            per_sezione[v.sezione or "—"] = per_sezione.get(v.sezione or "—", 0) + 1
        nums = [numero(v.id) for v in vs if numero(v.id) is not None]
        out["registri"][tipo] = {
            "file": f"{cfg['dir']}/{reg['file']}",
            "prefisso": reg["prefisso"],
            "voci": len(vs),
            "ultimo": f"{reg['prefisso']}-{max(nums):03d}" if nums else None,
            "per_stato": per_stato,
            "per_sezione": per_sezione,
        }
    esp = [v for v in voci if v.tipo == "esperimenti"]
    out["esiti"] = {}
    for v in esp:
        e = esito(v)
        if e:
            out["esiti"].setdefault(e, []).append(v.id)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def norm_stato(stato: str) -> str:
    s = stato.strip().strip("`*").lower()
    if "→" in s and "ver-" in s:
        return "→ VER"
    s = re.split(r"[\s(,;]", s, maxsplit=1)[0] if not s.startswith("da ") and not s.startswith("in ") else " ".join(s.split()[:2])
    return s.strip("`*.,;:")


ESITI = ("positivo", "negativo", "inconcludente", "abbandonato")


def esito(v: Voce) -> str | None:
    m = re.search(r"\*\*Esito:?\*\*:?\s*`?([a-zà]+)", v.testo, re.I)
    if m and m.group(1).lower() in ESITI:
        return m.group(1).lower()
    return None


@dataclass
class Problema:
    livello: str  # "errore" o "avviso"
    codice: str
    dove: str
    messaggio: str


def git_date(root: Path, rel: str) -> date | None:
    """Data dell'ultima modifica: oggi se il file ha modifiche non committate."""
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", rel], cwd=root, capture_output=True, text=True
        ).stdout.strip()
        if dirty:
            return date.today()
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel], cwd=root, capture_output=True, text=True
        ).stdout.strip()
        return date.fromisoformat(out) if out else None
    except (FileNotFoundError, ValueError):
        return None


def controlla(root: Path, cfg: dict) -> list[Problema]:
    P: list[Problema] = []
    base = root / cfg["dir"]
    if not cfg["_trovata"]:
        P.append(Problema("avviso", "config", CONFIG_NAME, "configurazione assente: uso i default (lancia /research-flow:init)"))
    voci, mancanti = carica_voci(root, cfg)
    for m in mancanti:
        P.append(Problema("errore", "registro-mancante", m, "il registro non esiste"))

    prefissi = [r["prefisso"] for r in cfg["registri"].values()]
    per_id: dict[str, list[Voce]] = {}
    for v in voci:
        per_id.setdefault(v.id, []).append(v)

    # 1. ID definiti due volte
    for id_, vs in per_id.items():
        if len(vs) > 1:
            dove = ", ".join(f"{v.file}:{v.riga}" for v in vs)
            P.append(Problema("errore", "id-doppio", dove, f"{id_} è definito {len(vs)} volte"))

    # 2. citazioni di ID mai definiti
    cit = citazioni(root, cfg, id_pattern(prefissi + list(cfg.get("prefissi_esterni", []))))
    for id_, luoghi in sorted(cit.items()):
        pref = id_.split("-")[0]
        if pref in cfg.get("prefissi_esterni", []) or id_ in per_id:
            continue
        f, n = luoghi[0]
        altri = f" (e altre {len(luoghi) - 1})" if len(luoghi) > 1 else ""
        P.append(Problema("errore", "id-inesistente", f"{f}:{n}", f"{id_} è citato ma non è definito{altri}"))

    # 3. buchi nella numerazione (un ID non si cancella: resta con il suo stato)
    for tipo, reg in cfg["registri"].items():
        nums = sorted({numero(v.id) for v in voci if v.tipo == tipo and re.fullmatch(rf"{reg['prefisso']}-\d+", v.id)})
        if nums:
            buchi = sorted(set(range(1, nums[-1] + 1)) - set(nums))
            if buchi:
                elenco = ", ".join(f"{reg['prefisso']}-{b:03d}" for b in buchi[:8]) + ("…" if len(buchi) > 8 else "")
                P.append(Problema("avviso", "id-mancante", f"{cfg['dir']}/{reg['file']}", f"numeri saltati: {elenco}"))

    # 4. campi obbligatori delle voci a intestazione
    for v in voci:
        if v.forma != "intestazione":
            continue
        for campo in cfg["campi"].get(v.tipo, []):
            if campo.lower() not in v.campi:
                P.append(Problema("avviso", "campo-mancante", f"{v.file}:{v.riga}", f"{v.id} senza «{campo}»"))

    # 5. ipotesi chiuse: il VER di destinazione esiste e la richiama
    pref_ip = cfg["registri"].get("ipotesi", {}).get("prefisso")
    pref_ver = cfg["registri"].get("verificato", {}).get("prefisso")
    if pref_ip and pref_ver:
        ver_re = re.compile(rf"→\s*`?({re.escape(pref_ver)}-\d+)")
        for v in voci:
            if v.tipo != "ipotesi" or not v.stato:
                continue
            m = ver_re.search(v.stato)
            if not m:
                continue
            dest = per_id.get(m.group(1))
            if not dest:
                P.append(Problema("errore", "ipotesi-chiusa", f"{v.file}:{v.riga}", f"{v.id} rimanda a {m.group(1)}, che non esiste"))
            elif v.id not in dest[0].testo:
                P.append(Problema("avviso", "ipotesi-chiusa", f"{dest[0].file}:{dest[0].riga}", f"{m.group(1)} non cita {v.id} («era {v.id}»)"))
        # e al contrario: un VER che dice «era IP-NNN» ha l'ipotesi chiusa verso di sé
        era_re = re.compile(rf"era\s+({re.escape(pref_ip)}-\d+)")
        for v in voci:
            if v.tipo != "verificato":
                continue
            for m in era_re.finditer(v.testo):
                ip = per_id.get(m.group(1))
                if ip and not (ip[0].stato and v.id in ip[0].stato):
                    P.append(Problema("avviso", "ipotesi-aperta", f"{ip[0].file}:{ip[0].riga}", f"{ip[0].id} è verificata da {v.id} ma il suo stato non è «→ {v.id}»"))

    # 6. esperimenti conclusi: esito dichiarato e report citato
    for v in voci:
        if v.tipo != "esperimenti" or not v.stato:
            continue
        if norm_stato(v.stato).startswith("concluso"):
            if not esito(v):
                P.append(Problema("errore", "esito-mancante", f"{v.file}:{v.riga}", f"{v.id} è concluso senza «Esito:» ({'/'.join(ESITI)})"))
            if "report" not in v.campi:
                P.append(Problema("avviso", "report-mancante", f"{v.file}:{v.riga}", f"{v.id} è concluso senza «Report:»"))

    # 7. stato e sezione coerenti (una voce chiusa sta nella sezione dei chiusi)
    for v in voci:
        if not v.stato:
            continue
        s = norm_stato(v.stato)
        sez = v.sezione.lower()
        if s.startswith("risolto") and "risolt" not in sez:
            P.append(Problema("avviso", "sezione", f"{v.file}:{v.riga}", f"{v.id} è risolto ma sta in «{v.sezione}»"))
        if s.startswith("fatto") and "fatt" not in sez:
            P.append(Problema("avviso", "sezione", f"{v.file}:{v.riga}", f"{v.id} è fatto ma sta in «{v.sezione}»"))
        if s.startswith("concluso") and "conclus" not in sez:
            P.append(Problema("avviso", "sezione", f"{v.file}:{v.riga}", f"{v.id} è concluso ma sta in «{v.sezione}»"))

    # 8. percorsi citati fra backtick che non esistono, solo nei documenti vivi
    # il registro delle modifiche dell'ufficiale cita di proposito nomi che non esistono più
    uff_path = base / cfg["ufficiale"]
    for doc in documenti_vivi(root, cfg):
        rel_doc = str(doc.relative_to(root))
        storico = False
        for n, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            if doc == uff_path and re.match(r"^#{1,3}\s", line):
                storico = bool(re.search(r"registro delle modifiche", line, re.I))
            if storico:
                continue
            for m in FILE_LIKE.finditer(line):
                cand = m.group(1).rstrip(".,;")
                if cand.startswith(("http", "~", "$", "/", "..")) or "<" in cand or "{" in cand:
                    continue
                if any(fnmatch.fnmatch(cand, g) for g in cfg.get("percorsi_ignora", [])):
                    continue
                if not esiste(cand, [doc.parent, base, root], root):
                    P.append(Problema("avviso", "percorso", f"{rel_doc}:{n}", f"`{cand}` non esiste"))

    # 9. il documento ufficiale è più vecchio dei registri
    uff = base / cfg["ufficiale"]
    if not uff.exists():
        P.append(Problema("errore", "ufficiale-mancante", str(uff.relative_to(root)), "il documento ufficiale non esiste"))
    else:
        testa = "\n".join(uff.read_text(encoding="utf-8").splitlines()[:12])
        m = re.search(r"[Aa]ggiornat[oa] al\**\s*(\d{1,2}-\d{1,2}-\d{4})", testa)
        if not m:
            P.append(Problema("avviso", "ufficiale-data", str(uff.relative_to(root)), "manca «Aggiornato al GG-MM-AAAA» in testa"))
        else:
            d = datetime.strptime(m.group(1), "%d-%m-%Y").date()
            dopo = []
            for reg in cfg["registri"].values():
                gd = git_date(root, f"{cfg['dir']}/{reg['file']}")
                if gd and gd > d:
                    dopo.append(f"{reg['file']} ({gd:%d-%m-%Y})")
            if dopo:
                P.append(Problema("avviso", "ufficiale-vecchio", str(uff.relative_to(root)), f"aggiornato al {d:%d-%m-%Y}, ma dopo sono cambiati {', '.join(dopo)}: /research-flow:stato"))

    # 10. le strade scartate e le cose non capite arrivano nell'ufficiale
    if uff.exists():
        testo_uff = uff.read_text(encoding="utf-8")
        citati = set(id_pattern(prefissi).findall(testo_uff))
        for v in voci:
            if v.tipo == "esperimenti" and esito(v) in ("negativo", "abbandonato", "inconcludente") and v.id not in citati:
                P.append(Problema("avviso", "esito-non-citato", f"{v.file}:{v.riga}", f"{v.id} ({esito(v)}) non compare in {cfg['ufficiale']}: va in «Strade scartate», «Dove potremmo sbagliare» o «Cosa non abbiamo capito»"))
        if pref_ip and pref_ver:
            for v in voci:
                if v.tipo != "verificato" or not re.search(r"smentit", v.testo, re.I):
                    continue
                ips = re.findall(rf"era\s+({re.escape(pref_ip)}-\d+)", v.testo)
                if ips and v.id not in citati and not any(i in citati for i in ips):
                    P.append(Problema("avviso", "esito-non-citato", f"{v.file}:{v.riga}", f"{v.id} smentisce {', '.join(ips)} ma non compare in {cfg['ufficiale']} («Strade scartate»)"))

    # 11. grafo vecchio
    for rel in stale(root, cfg):
        P.append(Problema("avviso", "graphify", rel, "cambiato dopo l'ultimo aggiornamento del grafo"))
    return P


def documenti_vivi(root: Path, cfg: dict) -> list[Path]:
    """I documenti che si tengono aggiornati: registri, ufficiale e le cartelle in `vivi`."""
    base = root / cfg["dir"]
    docs = [base / r["file"] for r in cfg["registri"].values()] + [base / cfg["ufficiale"]]
    for pattern in cfg.get("vivi", []):
        docs += sorted(base.glob(pattern))
    docs += [root / "README.md", root / "CLAUDE.md"]
    visti: list[Path] = []
    for d in docs:
        if d.exists() and d.is_file() and d not in visti:
            visti.append(d)
    return visti


def esiste(cand: str, bases: list[Path], root: Path) -> bool:
    """Un percorso esiste se si risolve da una delle basi, o come suffisso di un file del repo."""
    if "*" in cand:
        if any(any(True for _ in b.glob(cand)) for b in bases):
            return True
    elif any((b / cand).exists() for b in bases):
        return True
    for hit in root.glob(f"**/{cand}"):
        if ".git" not in hit.parts and "node_modules" not in hit.parts:
            return True
    return False


def graphify_ignora(root: Path) -> list[str]:
    """I pattern di `.graphifyignore` nella radice: i file che il grafo esclude apposta."""
    f = root / ".graphifyignore"
    if not f.exists():
        return []
    righe = (r.strip() for r in f.read_text(encoding="utf-8").splitlines())
    return [r for r in righe if r and not r.startswith("#")]


def ignorato(rel: str, patterns: list[str]) -> bool:
    """Sintassi .gitignore ridotta: `dir/` esclude la cartella, con `/` il pattern parte dalla radice."""
    for pat in patterns:
        if pat.endswith("/"):
            d = pat.strip("/")
            if rel.startswith(d + "/") if "/" in d else d in rel.split("/")[:-1]:
                return True
        elif fnmatch.fnmatch(rel, pat.lstrip("/")) or ("/" not in pat and fnmatch.fnmatch(rel.rsplit("/", 1)[-1], pat)):
            return True
    return False


def stale(root: Path, cfg: dict) -> list[str]:
    man = root / "graphify-out" / "manifest.json"
    if not cfg.get("graphify", True) or not man.exists():
        return []
    manifest = json.loads(man.read_text(encoding="utf-8"))
    base = root / cfg["dir"]
    docs = [p for p in base.rglob("*.md")] + [root / "README.md", root / "CLAUDE.md"]
    esclusi = graphify_ignora(root)
    out = []
    for p in docs:
        if not p.exists():
            continue
        rel = str(p.relative_to(root))
        if ignorato(rel, esclusi):
            continue
        entry = manifest.get(rel)
        if entry is None or p.stat().st_mtime > entry.get("mtime", 0) + 1:
            out.append(rel)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--config", type=Path, default=None, help=f"default: <root>/{CONFIG_NAME}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("next"); s.add_argument("registro")
    s = sub.add_parser("find"); s.add_argument("id")
    sub.add_parser("riepilogo")
    s = sub.add_parser("check"); s.add_argument("--json", action="store_true")
    sub.add_parser("stale")
    args = ap.parse_args()

    root = (args.root or git_root(Path.cwd())).resolve()
    cfg = load_config(root, args.config)

    if args.cmd == "next":
        return cmd_next(root, cfg, args.registro)
    if args.cmd == "find":
        return cmd_find(root, cfg, args.id)
    if args.cmd == "riepilogo":
        return cmd_riepilogo(root, cfg)
    if args.cmd == "stale":
        for rel in stale(root, cfg):
            print(rel)
        return 0

    problemi = controlla(root, cfg)
    if args.json:
        print(json.dumps([p.__dict__ for p in problemi], ensure_ascii=False, indent=2))
    else:
        errori = [p for p in problemi if p.livello == "errore"]
        avvisi = [p for p in problemi if p.livello == "avviso"]
        for titolo, gruppo in (("ERRORI", errori), ("AVVISI", avvisi)):
            if not gruppo:
                continue
            print(f"{titolo} ({len(gruppo)})")
            for p in sorted(gruppo, key=lambda p: (p.codice, p.dove)):
                print(f"  [{p.codice}] {p.dove}  {p.messaggio}")
        if not problemi:
            print("registri coerenti")
        else:
            print(f"\n{len(errori)} errori, {len(avvisi)} avvisi")
    return 1 if any(p.livello == "errore" for p in problemi) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
