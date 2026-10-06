---
name: overview
description: "Fa la pagina dei registri: una pagina HTML locale con lo stato della documentazione esplorativa a colpo d'occhio — voci aperte e chiuse per registro, esiti degli esperimenti, lavoro per fase e priorità, ipotesi aperte per impatto, domande aperte alle fonti — e ogni voce con la sua descrizione completa, dove ogni ID (`ESP-001`, `TODO-F01`…) è un link alla sua voce e ogni voce dice chi la cita. Scrive un file, oppure tiene acceso un piccolo server che la rifà dai registri a ogni ricarica. Trigger: /research-flow:overview, «fammi l'overview dei registri», «fammi la pagina dei registri», «voglio vedere i registri nel browser», «avvia la pagina della ricerca», «metti la pagina in rete», «ferma la pagina dei registri»."
argument-hint: "[serve [--rete] [--port N] | ferma [--port N] | --out <file>]"
---

# /research-flow:overview

La pagina la fa uno script deterministico, `${CLAUDE_PLUGIN_ROOT}/scripts/overview.py`, che legge i
registri con lo stesso parser di `registri.py` (i conteggi sono quelli di `registri.py
riepilogo`) e non scrive mai nei registri. Tu scegli il modo, lo lanci e dici all'utente dove
guardare. Non serve leggere METODO.md: la skill non scrive nei registri.

La pagina è **locale**: un file o un server su questa macchina. Non pubblicarla altrove (artifact,
gist, servizi esterni) se l'utente non lo chiede esplicitamente.

## 1. Il repo

Dalla radice del repo (`git rev-parse --show-toplevel`). Serve `.research-flow.json` o almeno la
cartella `research/`: se mancano, lo script esce con un errore e la strada è `/research-flow:init`.

## 2. Il modo

Dagli argomenti, o dalla richiesta:

| Richiesta | Modo |
|---|---|
| nessun argomento, «fammi la pagina» | **file** |
| `serve`, «avviala», «tienila accesa», «voglio aprirla nel browser» | **server** in locale |
| `serve --rete`, «raggiungibile dalla rete», «dagli altri computer» | **server** in rete |
| `ferma` | **ferma** il server |

### File

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/overview.py            # <radice>/research-flow.html
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/overview.py --out <file>
```

È una fotografia: per aggiornarla si rilancia. Se il file di default non è in `.gitignore`,
aggiungi la riga `research-flow.html` e dillo: è un file generato.

### Server

Il server rifà la pagina dai registri a ogni ricarica del browser, quindi resta sempre aggiornato
senza rilanciarlo. Va avviato **staccato dalla sessione**, così sopravvive alla chiusura di Claude
Code; non lanciarlo in primo piano e non suggerire all'utente di farlo con `!`, che blocca la
sessione e lo ferma quando si interrompe.

Prima controlla la porta (default `8099`, o `--port N`):

```bash
ss -ltnpH "sport = :8099"
```

- **libera:** avvia;
- **occupata da `overview.py`** (il processo lo dice `ps -o args= -p <pid>`): c'è già. Se l'utente
  ha chiesto un host diverso, o se il plugin è stato aggiornato dopo l'avvio (il server tiene il
  codice con cui è partito), fermalo e riavvialo; altrimenti dai l'indirizzo e basta;
- **occupata da altro:** non toccarla, proponi un'altra porta.

```bash
setsid nohup python3 ${CLAUDE_PLUGIN_ROOT}/scripts/overview.py --serve \
  --root "$(git rev-parse --show-toplevel)" --host 127.0.0.1 --port 8099 \
  > /tmp/research-flow-overview-8099.log 2>&1 < /dev/null &
```

Poi verifica che risponda (`curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8099/` dà
`200`); se no leggi il log.

**In rete** (`--host 0.0.0.0`) solo se l'utente lo chiede: la pagina non ha password e chiunque
sia nella stessa rete legge i registri. Diglielo, e dagli l'indirizzo con l'IP della macchina
(`hostname -I`, quello della rete da cui si collega: con SSH è l'indirizzo di destinazione in
`$SSH_CONNECTION`). Se l'ambiente blocca l'esposizione, non aggirarlo: dai all'utente il comando
da lanciare lui.

**In SSH** (`$SSH_CONNECTION` non vuota) con il server in locale, `localhost` è quello di questa
macchina, non del computer dell'utente: proponi il tunnel
`ssh -L 8099:localhost:8099 <utente>@<host>` e `http://localhost:8099` sul suo computer, oppure
la rete.

### Ferma

Trova il PID dalla porta e controlla che sia `overview.py` prima di fermarlo:

```bash
pid=$(ss -ltnpH "sport = :8099" | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
ps -o args= -p "$pid"   # deve contenere overview.py --serve
kill "$pid"
```

Non usare `pkill -f` con il nome dello script: il modello cerca anche nella riga di comando della
shell che lo lancia, e la shell si uccide da sola.

## 3. Resoconto

All'utente, in breve:

- dove guardare: il percorso del file o l'indirizzo, e se è in locale, in SSH o in rete;
- per il server: che si aggiorna da solo ricaricando, che resta acceso finché non lo si ferma o
  si riavvia la macchina, e come fermarlo (`/research-flow:overview ferma`);
- cosa c'è in alto: i numeri di `registri.py riepilogo` (voci aperte e chiuse) in una riga.

Non committare.
