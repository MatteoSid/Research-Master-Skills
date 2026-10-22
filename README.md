# Research Flow

Documentazione esplorativa per i progetti che non sanno ancora dove andranno a finire: quelli in
cui si fanno ipotesi, si provano strade, se ne scartano, e quello che si impara conta quanto il
codice.

Il principio: **un esperimento fallito documentato vale quanto uno riuscito.** Il successo resta
nel codice. Il fallimento invece si toglie dal codice, e se nessuno lo scrive qualcuno prima o poi
lo rifarà. Per questo ogni affermazione del progetto ha uno stato (fatto, ipotesi, dubbio,
esperimento, lavoro da fare), una fonte che si può ricontrollare e un ID con cui le altre voci la
citano. Niente si cancella: una voce chiusa resta con il suo esito.

## I documenti

Sei documenti al primo livello di una cartella (di solito `research/`), e sottocartelle per ruolo
(`fonti/`, `misure/`, `storico/`…):

| documento | prefisso | cosa ci va |
|---|---|---|
| `dubbi_implementazione.md` | `DUB` | dubbi sul nostro codice |
| `ipotesi_da_verificare.md` | `IP` | quello che assumiamo, con come si verifica e l'impatto se è sbagliato |
| `verificato.md` | `VER` | quello che sappiamo: fatti da una fonte, misure nostre, con la fonte |
| `esperimenti.md` | `ESP` | ogni esperimento con il suo esito: positivo, negativo, inconcludente, abbandonato |
| `da_fare.md` | `TODO` | il lavoro che manca, per fase e priorità, e le domande aperte alle fonti |
| `stato_progetto.md` | — | la versione ufficiale, breve (un tetto di parole): l'obiettivo, le scelte in vigore, cosa abbiamo imparato, dove potremmo sbagliare, i prossimi passi |

Nei registri entra quello che può cambiare una decisione; le cose piccole trovate lavorando si
sistemano subito o vanno in una issue. Il codice si cita con file e simbolo, mai con il numero di
riga, tranne nei report, che dicono in testa il commit su cui hanno misurato.

Il regolamento completo, con il ciclo di vita delle voci e la tabella di propagazione, è in
[`METODO.md`](METODO.md): lo leggono tutte le skill prima di scrivere.

## Le skill

| skill | cosa fa |
|---|---|
| `/research-flow:init` | prepara il repo: configurazione, documenti, cartelle, sezione del `CLAUDE.md`. Su un repo con registri già esistenti li adotta e migra i contenuti (esperimenti sparsi, documento ufficiale di un'altra forma) senza perdere niente |
| `/research-flow:annota` | aggiunge una voce o ne cambia lo stato, dopo aver cercato nei registri e con graphify se c'è già. Chiude gli esperimenti con il loro esito, sposta le ipotesi confermate o smentite in verificato, segna decadute quelle che non servono più (con il motivo), e propaga il cambiamento |
| `/research-flow:fonte` | registra un'informazione esterna (una persona, un documento, una documentazione, un articolo, una pagina, un messaggio, un dataset), tenendo separato quello che dice la fonte da quello che ne deduciamo, e la propaga a fatti, ipotesi, domande aperte e documento ufficiale. Se aggiungere una fonte lo decide l'utente, o Claude di sua iniziativa dicendolo; le fonti stanno nell'indice `fonti/README.md` con la loro affidabilità |
| `/research-flow:stato` | riscrive la versione ufficiale dai registri, con la fotografia della versione vecchia in `storico/`, e allinea i documenti specchio. Con `leggi` risponde «a che punto siamo?» senza scrivere |
| `/research-flow:controlla` | controllo di coerenza, prima di una PR verso il branch principale: ID doppi o inesistenti, ipotesi chiuse male, esperimenti senza esito, percorsi rotti, ufficiale vecchio o troppo lungo, numeri di riga citati, grafo vecchio. Corregge quello che è meccanico |
| `/research-flow:overview` | la pagina dei registri nel browser: voci aperte e chiuse, esiti degli esperimenti, lavoro per fase, ipotesi per impatto, domande alle fonti, e ogni voce con la descrizione completa, dove ogni ID è un link alla sua voce: fra le voci la nota citata si apre in una card sopra la pagina, che segue i collegamenti con un tasto «Indietro». Scrive un file, o con `serve` tiene acceso un server locale (anche in rete con `--rete`) che la rifà a ogni ricarica |

## Gli script

`scripts/registri.py` (solo libreria standard, Python 3.9+) non scrive mai: le skill lo usano
per non contare gli ID a mano e per i controlli. Si può lanciare anche da solo, per esempio in
un hook di pre-commit o in CI:

```
python3 scripts/registri.py next ipotesi      # IP-027
python3 scripts/registri.py find IP-003       # dove è definita e chi la cita, codice compreso
python3 scripts/registri.py riepilogo         # voci per registro e stato, esiti degli esperimenti (JSON)
python3 scripts/registri.py scartate          # le strade scartate (anche le ipotesi decadute), con cosa ne abbiamo tratto
python3 scripts/registri.py check             # controlli di coerenza, exit 1 se ci sono errori
python3 scripts/registri.py stale             # documenti che graphify non ha ancora visto
```

`scripts/overview.py` (stessa libreria, stesse regole) fa la pagina dei registri di
`/research-flow:overview`:

```
python3 scripts/overview.py                          # research-flow.html nella radice del repo
python3 scripts/overview.py --serve                  # http://localhost:8099, rifatta a ogni ricarica
python3 scripts/overview.py --serve --host 0.0.0.0   # raggiungibile dalla rete, senza password
```

## Configurazione

Per progetto, in `.research-flow.json` nella radice del repo (la scrive `/research-flow:init`,
il modello è `templates/research-flow.json`). Tutte le chiavi sono facoltative:

| chiave | default | a cosa serve |
|---|---|---|
| `dir` | `research` | la cartella dei documenti |
| `registri` | i cinque qui sopra | file e prefisso di ogni registro: un repo che ha già i suoi nomi li tiene |
| `ufficiale` | `stato_progetto.md` | la versione ufficiale |
| `ufficiale_parole_max` | `1500` | il tetto di parole dell'ufficiale, senza il registro delle modifiche (`0` = nessun tetto) |
| `voce_parole_max` | `400` | il tetto di parole di una voce a intestazione (`0` = nessun tetto): oltre, `check` avvisa (`voce-lunga`) |
| `riga_parole_max` | `250` | il tetto di parole di una riga di tabella (verificato, da_fare) |
| `specchi` | `[]` | documenti fuori da `dir` che ripetono l'ufficiale e vanno allineati (`path`, `quando`) |
| `vivi` | `fonti/**`, `misure/**` | sottocartelle in cui i percorsi citati devono esistere |
| `percorsi_ignora` | `[]` | glob di percorsi citati che non devono esistere: file proposti, file di altri repo |
| `prefissi_esterni` | `[]` | prefissi di ID definiti altrove, che `check` non segnala |
| `campi` | vedi script | campi obbligatori delle voci a intestazione |
| `graphify` | `true` | controlla che il grafo sia aggiornato |

La configurazione sta nel repo e non in `userConfig` perché cambia da progetto a progetto.

## Graphify

Se il repo ha un grafo [graphify](https://github.com/safishamsi/graphify) (`graphify-out/`), le
skill lo usano per trovare file e simboli da citare. I sei documenti conviene escluderli dal grafo
(`.graphifyignore`): cambiano a ogni lavoro, ogni estrazione semantica costa, e fra le voci si
naviga meglio con `registri.py find` e `scartate`. Il grafo resta per il codice e per i documenti
che cambiano di rado (report, fonti), con `graphify update .` per il codice e `/graphify .
--update` per i documenti, una volta alla fine del lavoro. `registri.py check` avvisa quando un
documento che il grafo legge è cambiato dopo l'ultimo aggiornamento. Senza grafo le skill
funzionano lo stesso, con `grep`.

## Con issue-flow

Si integrano senza configurazione: una issue di [issue-flow](https://github.com/MatteoSid/Issues-Master-Skills)
cita le voci che chiude (`TODO-015`, `IP-003`), e alla chiusura `/research-flow:annota fatto
TODO-015 #52` le sposta. Per farle rileggere a `/issue-flow:close`, metti la cartella dei
registri nel suo `docs_paths`.

## Installazione

```
/plugin marketplace add https://github.com/MatteoSid/Research-Master-Skills.git
/plugin install research-flow@research-flow
```

Il `marketplace add` clona con le credenziali git della macchina, quindi va bene anche l'SSH:
`git@github.com:MatteoSid/Research-Master-Skills.git`.

## Licenza

MIT.
