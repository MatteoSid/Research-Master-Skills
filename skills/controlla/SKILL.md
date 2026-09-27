---
name: controlla
description: "Controlla la coerenza della documentazione esplorativa e corregge quello che è meccanico: ID doppi o citati senza definizione, ipotesi chiuse verso un VER che non esiste, esperimenti conclusi senza esito o senza report, voci nella sezione sbagliata, percorsi citati che non esistono, documento ufficiale più vecchio dei registri, grafo graphify non aggiornato. Da lanciare prima di un commit che tocca la ricerca e alla chiusura di una issue. Trigger: /research-flow:controlla, «controlla i registri», «la documentazione è coerente?», «prima di committare controlla la ricerca»."
argument-hint: "[--solo-report]"
---

# /research-flow:controlla

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md` e `.research-flow.json`. Il controllo lo fa uno
script deterministico, `${CLAUDE_PLUGIN_ROOT}/scripts/registri.py`: tu interpreti il risultato e
correggi.

## 1. Lancia il controllo

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registri.py check
```

Exit 1 se c'è almeno un errore. I codici:

| Codice | Livello | Cosa vuol dire | Come si corregge |
|---|---|---|---|
| `registro-mancante`, `ufficiale-mancante` | errore | un documento della configurazione non esiste | `/research-flow:init`, o la configurazione punta al file sbagliato |
| `id-doppio` | errore | lo stesso ID è definito due volte | la seconda prende `registri.py next`, e le citazioni che parlavano di lei si aggiornano (leggi il contesto di ognuna con `registri.py find`) |
| `id-inesistente` | errore | un ID è citato ma non definito | refuso (correggi la citazione) o voce mai scritta (scrivila con `/research-flow:annota`); se il prefisso è di un sistema esterno, va in `prefissi_esterni` |
| `ipotesi-chiusa` | errore/avviso | un'ipotesi rimanda a un VER che non esiste, o il VER non la cita | il VER dice «era IP-NNN» |
| `ipotesi-aperta` | avviso | un VER dice «era IP-NNN» ma l'ipotesi ha ancora lo stato aperto | lo stato dell'ipotesi diventa `→ VER-NNN`, riga in «Smentite o confermate» |
| `esito-mancante` | errore | esperimento concluso senza esito | **non inventarlo**: rileggi il report e il criterio; se non si può decidere, chiedi all'utente |
| `report-mancante` | avviso | esperimento concluso senza report | cerca il report in `misure/`; se non esiste, dillo all'utente |
| `campo-mancante` | avviso | a una voce manca un campo obbligatorio | completala se l'informazione si trova (graphify, report, codice), altrimenti segnalala |
| `id-mancante` | avviso | numeri saltati in un registro | di solito una voce cancellata: cerca in `git log -S '<ID>'` e ripristinala con il suo stato |
| `sezione` | avviso | una voce chiusa sta fra le aperte | spostala nella sezione dei chiusi |
| `percorso` | avviso | un file citato non esiste | file spostato: aggiorna la citazione. File proposto da una voce aperta o di un altro repo: aggiungilo a `percorsi_ignora` nella configurazione |
| `esito-non-citato` | avviso | un esperimento negativo, abbandonato o inconcludente, o un'ipotesi smentita, non compare nell'ufficiale | una riga in «Strade scartate», «Dove potremmo sbagliare» o «Cosa non abbiamo capito» secondo METODO.md, «Cosa vuol dire l'esito» |
| `ufficiale-vecchio`, `ufficiale-data` | avviso | i registri sono cambiati dopo l'ultimo aggiornamento dell'ufficiale | `/research-flow:stato` |
| `graphify` | avviso | documenti cambiati dopo l'ultimo aggiornamento del grafo | la skill graphify con `--update` |

## 2. Correggi

Con `--solo-report` ti fermi al resoconto. Altrimenti:

- **correggi da solo** quello che è meccanico e ha una sola soluzione: citazioni di file spostati,
  voci nella sezione sbagliata, stati `→ VER-NNN` mancanti, righe mancanti in «Smentite o
  confermate», ID doppi;
- **chiedi** prima di tutto ciò che richiede giudizio: l'esito di un esperimento, una voce
  cancellata da ripristinare, una citazione che potrebbe puntare a due voci diverse;
- **non toccare** i documenti fuori da `vivi` (brainstorm, storico, ricerche iniziali): sono
  fotografie, i percorsi vecchi lì dentro sono giusti.

Poi rilancia `check` finché gli errori sono zero.

## 3. Controlli che lo script non fa

Leggili a occhio sulle voci cambiate di recente (`git diff` e `git log -p --since=<ultima
modifica dell'ufficiale> -- <dir>/`):

- ogni esperimento negativo o abbandonato e ogni ipotesi smentita citati nell'ufficiale (lo
  controlla lo script) stanno **nella sezione giusta**: un'alternativa bocciata in «Strade
  scartate», una scelta in vigore messa in dubbio in «Dove potremmo sbagliare»;
- la domanda di ogni esperimento concluso di recente è scritta dalla parte dell'idea, così che
  `positivo` voglia dire «regge»;
- le ipotesi con impatto alto sono in «Dove potremmo sbagliare»;
- le voci citano il codice con file e riga che esistono ancora (per le voci aperte: una riga
  spostata va aggiornata);
- se la configurazione ha `specchi`, e l'ufficiale è cambiato, gli specchi sono allineati.

## 4. Il grafo

Se lo script dà avvisi `graphify`, aggiorna il grafo con la skill graphify e `--update`, poi
rilancia `registri.py stale`: deve essere vuoto.

## 5. Resoconto

All'utente: errori e avvisi trovati, cosa hai corretto, cosa resta e perché (con la domanda, se
serve una decisione). Non committare.
