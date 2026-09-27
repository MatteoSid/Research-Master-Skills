---
name: init
description: "Prepara un repo alla documentazione esplorativa di research-flow: la configurazione .research-flow.json, i sei documenti (dubbi, ipotesi, verificato, esperimenti, da fare, stato del progetto), le cartelle per ruolo e la sezione del CLAUDE.md. Su un repo che ha già dei registri li adotta senza perdere niente: mappa quelli che ci sono, crea quelli che mancano e propone la migrazione dei contenuti. Trigger: /research-flow:init, «prepara la documentazione della ricerca», «adotta research-flow in questo repo», «imposta i registri»."
argument-hint: "[cartella, default research]"
---

# /research-flow:init

Prima di tutto leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md`, il regolamento del plugin: dice cosa va in
ogni documento, e questa skill lo applica al repo. I modelli dei documenti stanno in
`${CLAUDE_PLUGIN_ROOT}/templates/`, lo script dei controlli in
`${CLAUDE_PLUGIN_ROOT}/scripts/registri.py`.

L'obiettivo: alla fine `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registri.py check` non dà errori, e
un'altra sessione che apre il repo trova nel `CLAUDE.md` quello che le serve per usare i registri.

## 1. Ricognizione

Prima di scrivere qualunque cosa guarda cosa c'è:

```bash
ls .research-flow.json 2>/dev/null; git rev-parse --show-toplevel
ls <dir>/ 2>/dev/null; ls graphify-out/graph.json 2>/dev/null
grep -rlE '\b(DUB|IP|VER|ESP|TODO|ADR|EXP)-[0-9]+' --include='*.md' . 2>/dev/null | grep -v node_modules | head -30
```

e leggi il `CLAUDE.md` e il `README.md` del progetto. Cerchi tre cose:

- **registri esistenti** con altri nomi o altri prefissi (un `decisions.md` con `ADR-NNN`, un
  `TODO.md`, un `strategia_corrente.md` che fa da documento ufficiale…);
- **esperimenti già fatti ma non registrati**: report di misura, notebook, sezioni «abbiamo
  provato», voci del registro verificato che dicono «smentita», elenchi di esperimenti proposti
  in brainstorm (E1, E2…);
- **regole sulla documentazione già scritte** nel `CLAUDE.md`: vanno allineate, non duplicate.

Se esiste già `.research-flow.json`, questa è una ri-esecuzione: controlla con `registri.py check`
e completa solo quello che manca.

## 2. Decidi con l'utente

Mostra all'utente quello che hai trovato e **chiedi** (con AskUserQuestion) solo i bivi veri:

- **repo nuovo:** la cartella (`$ARGUMENTS`, default `research`) e i documenti specchio da
  tenere allineati (pagine di documentazione nell'app, un README pubblico). **Le fonti non si
  chiedono**: non si decidono all'inizio, si aggiungono quando arrivano (METODO.md, «Le fonti»);
- **repo con registri:** la mappatura da registri esistenti a tipi del metodo. Proponi di
  **tenere i nomi dei file e i prefissi esistenti** (la configurazione li mappa): rinominare
  rompe le citazioni per niente. Per il documento ufficiale proponi invece di migrare verso le
  dieci sezioni del metodo, perché è la parte che cambia davvero.

Non chiedere quello che si deduce dal repo.

## 3. Scrivi la configurazione

`.research-flow.json` nella radice del repo, partendo da `templates/research-flow.json`:

```json
{
  "dir": "research",
  "registri": { "dubbi": {"file": "...", "prefisso": "DUB"}, "...": {} },
  "ufficiale": "stato_progetto.md",
  "specchi": [{"path": "frontend/src/docs/", "quando": "cambia una scelta o una soglia"}],
  "vivi": ["fonti/**/*.md", "misure/**/*.md"],
  "percorsi_ignora": [],
  "prefissi_esterni": [],
  "graphify": true
}
```

- `specchi`: i documenti fuori da `dir` che ripetono il contenuto dell'ufficiale e vanno
  aggiornati con lui.
- `vivi`: le sottocartelle di `dir` i cui percorsi citati devono esistere; brainstorm e storico
  non ci vanno, perché citano file proposti o spariti.
- `prefissi_esterni`: prefissi che si citano come ID ma sono definiti altrove (`JIRA`, `ADR` di
  un altro repo), così `check` non li segnala.
- `percorsi_ignora`: glob di percorsi che le voci citano ma che non devono esistere, cioè i file
  proposti da un dubbio («spostarla in `backend/app/quotes.py`») e i file di altri repo. Li trovi
  al passo 7: sono gli avvisi `percorso` che restano dopo aver corretto quelli veri.

## 4. Crea quello che manca

- le cartelle `fonti/`, `misure/`, `storico/` (con un `.gitkeep` se vuote);
- l'indice delle fonti `fonti/README.md`, dal modello `templates/fonti_indice.md`. In un repo
  nuovo resta vuoto. In un repo che ha già file in `fonti/`, ogni fonte che c'è prende la sua
  riga: che cos'è e l'affidabilità le ricavi dai suoi file e dal `CLAUDE.md` (nel dubbio
  chiedi); come data metti quella del primo file, con «adozione» al posto di chi l'ha decisa;
- i documenti che mancano, dai modelli, **senza toccare quelli che esistono**. Nei modelli
  adatta il testo al progetto: le fasi di da_fare (dalla roadmap del `CLAUDE.md` o del
  `README.md`, se c'è), l'obiettivo nell'ufficiale;
- se un registro esistente non ha in testa la spiegazione del suo formato, aggiungila dal
  modello.

## 5. Migra (solo se il repo aveva già dei contenuti)

La migrazione è la parte che richiede giudizio; falla con cura, un documento alla volta.

**Esperimenti.** Rileggi prima «Cosa vuol dire l'esito» ed «Esperimenti ricostruiti» in
METODO.md. Per ogni esperimento trovato in ricognizione crea una voce `ESP-NNN`, i conclusi in
ordine cronologico e poi i proposti:

- già fatto, con un report → `concluso (data)`, con esito, report e «cosa ne abbiamo tratto»
  presi dal report e dalla voce verificato che lo cita. **L'esito lo decidi dal report, non lo
  inventi:** se il report non permette di dire positivo o negativo, è `inconcludente`;
- già fatto, **senza un report in `misure/`** (una tabella in una fonte, un numero nel
  `README.md`, uno script di verifica) → `concluso` come sopra, e nel campo Report dove sta il
  risultato;
- proposto in un brainstorm o implicito in un TODO, e mai fatto → `proposto`, con domanda e
  metodo dal brainstorm e il campo **Origine** («era E7 in `brainstorm_…/2_esperimenti.md`»).
  Prima di metterlo `proposto` controlla che nel frattempo non sia stato fatto, anche in parte:
  il grafo non lo sa, lo dicono i report, i registri e `git log`;
- lasciato a metà, o superato perché una fonte ha risposto prima → `concluso`, esito
  `abbandonato`, con il motivo.

Scrivi la domanda dalla parte dell'idea messa alla prova, così che `positivo` voglia dire «regge»
(METODO.md, «Cosa vuol dire l'esito»): se il documento di partenza la formulava al contrario,
riformulala. Metti la corrispondenza anche nel documento di partenza (una riga in testa: «gli
esperimenti di questo file sono registrati in `esperimenti.md`: E1 = ESP-00x …»), così chi arriva
dal vecchio nome trova il nuovo; e le citazioni `ESP-NNN` nelle voci che l'esperimento tocca (il
«Come si verifica» delle ipotesi, il «Perché» dei TODO, la «Fonte» dei VER).

**Documento ufficiale.** Se ne esiste uno con un'altra forma:

1. copialo in `storico/<nome>_<data>.md` così com'è, con in testa solo l'avviso di fotografia e
   la mappa delle sezioni vecchie e nuove (METODO.md, «Le fotografie»);
2. scrivi `stato_progetto.md` con le dieci sezioni del metodo, **portando tutto il contenuto**:
   le sezioni di dominio del vecchio documento diventano sottosezioni di «Le scelte in vigore»,
   «Dove potremmo sbagliare» e il registro delle modifiche passano interi. Le sezioni nuove
   («Cosa funziona», «Strade scartate», «Cosa non abbiamo capito») le riempi dai registri.
   Se il vecchio documento aveva un pubblico dichiarato (nel `CLAUDE.md`, per esempio «serve a
   chi decide per capire se stiamo seguendo la strada giusta»), la testa del nuovo lo ripete;
3. nel registro delle modifiche i riferimenti a paragrafi (§3.4) puntavano al vecchio documento:
   rinumerali sui paragrafi nuovi e metti sotto il titolo una nota con la corrispondenza. Poi
   aggiungi in alto la riga della migrazione;
4. aggiorna **tutte** le citazioni del vecchio nome (`grep -rn '<vecchio nome>'` su tutto il
   repo, compresi codice, `README.md`, `CLAUDE.md`, e i documenti specchio), **tranne** dentro
   `storico/`: le fotografie non si toccano, salvo l'avviso in testa, che deve puntare al
   documento nuovo;
5. controlla di non aver perso niente: confronta sezione per sezione il vecchio documento (dalla
   fotografia) con il nuovo, per esempio con `diff` sulle sezioni estratte. Le sole differenze
   ammesse sono la numerazione e le citazioni aggiunte.

## 6. Il CLAUDE.md

Aggiungi al `CLAUDE.md` del progetto la sezione di `templates/claude_md_sezione.md`, con i
segnaposto sostituiti (`{extra}` è per le regole specifiche del progetto: le fonti che ha già,
gli specchi). Se il `CLAUDE.md`
ha già delle regole sulla documentazione, **non duplicarle**: riscrivi quella parte in modo che
rimandi al plugin e tenga solo quello che è specifico del progetto (la tabella delle cartelle,
le fonti che ci sono già, quali documenti specchio aggiornare).

**La tabella «Quando usare le skill» non si toglie**, anche se METODO.md dice le stesse cose:
METODO.md entra nel contesto solo quando si invoca una skill, il `CLAUDE.md` c'è sempre. È la
tabella che fa ricordare a una sessione che sta chiudendo una issue, o che ha appena scoperto un
dubbio nel codice, che c'è da scrivere nei registri. Se il `CLAUDE.md` aveva un suo elenco di
«quando aggiornare», fondilo con la tabella invece di cancellarlo.

## 7. Controlla e aggiorna il grafo

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registri.py check
```

Correggi gli errori; gli avvisi li riporti all'utente. Poi, se c'è un grafo, aggiornalo: la skill
graphify con `--update`, perché sono cambiati documenti.

## 8. Resoconto

All'utente, in breve: cosa hai creato, cosa hai migrato (quanti esperimenti, con che esiti), cosa
hai lasciato com'era, gli avvisi rimasti. Non committare: lo decide l'utente.
