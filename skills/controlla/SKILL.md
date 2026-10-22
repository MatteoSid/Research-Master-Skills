---
name: controlla
description: "Controlla la coerenza della documentazione esplorativa e corregge quello che è meccanico: ID doppi o citati senza definizione, ipotesi chiuse verso un VER che non esiste, esperimenti conclusi senza esito o senza report, voci nella sezione sbagliata, percorsi citati che non esistono, documento ufficiale più vecchio dei registri o oltre il tetto di parole, voci oltre il tetto di parole (le chiuse si accorciano, i diari vanno nei report, gli elenchi nelle issue), numeri di riga citati dove il testo si tiene aggiornato, grafo graphify non aggiornato. Da lanciare prima di una PR verso il branch principale che tocca la ricerca, non a ogni commit né alla chiusura di ogni issue figlia. Trigger: /research-flow:controlla, «controlla i registri», «la documentazione è coerente?», «prima della PR controlla la ricerca»."
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
| `decaduta-senza-motivo` | avviso | un'ipotesi `decaduta` non dice perché | il motivo dopo la data, con le voci da cui dipende: `decaduta (GG-MM-AAAA): motivo`; se non si sa, chiedi all'utente |
| `esito-mancante` | errore | esperimento concluso senza esito | **non inventarlo**: rileggi il report e il criterio; se non si può decidere, chiedi all'utente |
| `report-mancante` | avviso | esperimento concluso senza report | cerca il report in `misure/`; se non esiste, dillo all'utente |
| `campo-mancante` | avviso | a una voce manca un campo obbligatorio | completala se l'informazione si trova (graphify, report, codice), altrimenti segnalala |
| `id-mancante` | avviso | numeri saltati in un registro | di solito una voce cancellata: cerca in `git log -S '<ID>'` e ripristinala con il suo stato |
| `sezione` | avviso | una voce chiusa (anche un dubbio `accettato`) sta fra le aperte | spostala nella sezione dei chiusi |
| `voce-lunga` | avviso | voci sopra il tetto di parole (`voce_parole_max`, `riga_parole_max`), le più lunghe in testa | METODO.md, «Quanto è lunga una voce»: una voce chiusa si accorcia nella forma chiusa, dopo aver controllato che il dettaglio stia nel report o nell'issue; le note di un esperimento in corso vanno nel «Diario» del report; un elenco di cose piccole va in una issue |
| `percorso` | avviso | un file citato non esiste | file spostato: aggiorna la citazione. File proposto da una voce aperta o di un altro repo: aggiungilo a `percorsi_ignora` nella configurazione |
| `ufficiale-vecchio`, `ufficiale-data` | avviso | i registri sono cambiati dopo l'ultimo aggiornamento dell'ufficiale | `/research-flow:stato` |
| `ufficiale-lungo` | avviso | l'ufficiale supera il tetto di parole (`ufficiale_parole_max`) | `/research-flow:stato`: si sceglie, non si comprime; il dettaglio resta nei registri |
| `riga-citata` | avviso | una voce aperta, l'ufficiale, il `README.md` o il `CLAUDE.md` citano il codice con il numero di riga | `file` + simbolo, trovato leggendo il file alla riga citata nel commit in cui la citazione è stata scritta (`git blame` sulla riga del registro) |
| `righe-senza-commit` | avviso | un report o una fonte cita righe senza dire su quale commit valgono | `**Commit:** `<hash>`` in testa: il commit su cui si è misurato o, se non si sa, l'ultimo che ha toccato il documento. Le righe non si riallineano |
| `graphify` | avviso | documenti cambiati dopo l'ultimo aggiornamento del grafo | la skill graphify con `--update` |

## 2. Correggi

Con `--solo-report` ti fermi al resoconto. Altrimenti:

- **correggi da solo** quello che è meccanico e ha una sola soluzione: citazioni di file spostati,
  voci nella sezione sbagliata, stati `→ VER-NNN` mancanti, righe mancanti in «Smentite o
  confermate», ID doppi;
- **chiedi** prima di tutto ciò che richiede giudizio: l'esito di un esperimento, una voce
  cancellata da ripristinare, una citazione che potrebbe puntare a due voci diverse;
- per le **voci lunghe** (`voce-lunga`) proponi all'utente cosa accorciare, con il risparmio:
  accorciare una voce chiusa il cui dettaglio sta già nel report è sicuro, spostare un elenco in
  una issue o un diario in un report si fa con il suo sì. Non accorciare mai «Cosa ne abbiamo
  tratto» né i numeri dell'esito;
- **non toccare** i documenti fuori da `vivi` (brainstorm, storico, ricerche iniziali): sono
  fotografie, i percorsi vecchi lì dentro sono giusti.

Poi rilancia `check` finché gli errori sono zero.

## 3. Controlli che lo script non fa

Leggili a occhio sulle voci cambiate di recente (`git diff` e `git log -p --since=<ultima
modifica dell'ufficiale> -- <dir>/`):

- un'ipotesi `decaduta` non è citata come un fatto nell'ufficiale né in una voce aperta: non
  sappiamo se era vera;
- gli esperimenti negativi o abbandonati e le ipotesi smentite citati nell'ufficiale stanno
  **nella sezione giusta**: un'alternativa bocciata in «Cosa abbiamo imparato», una scelta in
  vigore messa in dubbio in «Dove potremmo sbagliare»;
- la domanda di ogni esperimento concluso di recente è scritta dalla parte dell'idea, così che
  `positivo` voglia dire «regge»;
- i rischi più gravi (ipotesi con impatto alto, scelte messe in dubbio) sono in «Dove potremmo
  sbagliare»;
- le voci aperte citano il codice con file e simbolo che esistono ancora: un simbolo rinominato o
  tolto si aggiorna. Le voci chiuse e i report non si riallineano;
- le voci nuove passano il test di METODO.md, «Cosa entra nei registri»: una cosa piccola che non
  cambia una decisione si sistema o va in una issue, e la voce si toglie solo se è nata in questo
  lavoro e nessuno la cita (se ha già un ID, resta con lo stato `accettato` o `fatto`, nella
  forma chiusa, e la issue la cita);
- se la configurazione ha `specchi`, e l'ufficiale è cambiato, gli specchi sono allineati.

## 4. Il grafo

Se lo script dà avvisi `graphify`, aggiorna il grafo con la skill graphify e `--update`, una
volta sola, poi rilancia `registri.py stale`: deve essere vuoto. I documenti esclusi da
`.graphifyignore` (di solito i sei documenti e `storico/`) non danno avvisi e non si estraggono.

## 5. Resoconto

All'utente: errori e avvisi trovati, cosa hai corretto, cosa resta e perché (con la domanda, se
serve una decisione). Non committare.
