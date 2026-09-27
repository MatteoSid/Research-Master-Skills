---
name: fonte
description: "Registra un'informazione arrivata da fuori — una persona, un documento, una documentazione, un articolo, una pagina web, un messaggio, uno screenshot, un dataset — e la propaga ai registri: il testo originale in fonti/, i fatti in verificato, le ipotesi confermate, smentite o indebolite, le domande aperte chiuse, il documento ufficiale se cambia una scelta. Prima decide se è il momento di aggiungere una fonte: lo decide l'utente, oppure Claude di sua iniziativa quando nella conversazione arriva un'informazione esterna che tocca i registri. Tiene separato quello che dice la fonte da quello che ne deduciamo noi. Trigger: /research-flow:fonte, «aggiungi questa fonte», «registra questa risposta», «è arrivata un'informazione nuova», «mi hanno detto che…», «ecco la documentazione / l'articolo / lo screenshot»."
argument-hint: "[nome della fonte] <il testo, il file, il link o l'immagine>"
---

# /research-flow:fonte

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md` («Le fonti», «Due livelli di fiducia» e «La
propagazione») e `.research-flow.json`, che dice in che cartella stanno i documenti (`dir`). Lo
script è `${CLAUDE_PLUGIN_ROOT}/scripts/registri.py` (`registri.py` qui sotto).

## Il principio

**Quello che dice la fonte e quello che ne deduciamo noi non si mescolano mai.** Una fonte che
dice «il sistema rilancia il job circa ogni minuto» dà un fatto *riferito*; «quindi usa un cron» è
una nostra deduzione, cioè un'ipotesi. Chi rilegge fra sei mesi deve poter distinguere l'una
dall'altra, e ricontrollare il testo originale.

Una fonte è **qualunque informazione che non abbiamo prodotto noi**: una persona che risponde o
racconta, un documento, una documentazione tecnica, un articolo, una pagina web, un messaggio, uno
screenshot, un dataset di terzi. Quello che misuriamo noi non è una fonte: è un esperimento, e va
con `/research-flow:annota`.

## 0. È il momento di aggiungere una fonte?

La decisione la prende **l'utente**, quando invoca questa skill o dice di registrare qualcosa,
oppure **tu**, di tua iniziativa, quando nel lavoro arriva un'informazione esterna che merita di
restare. Se l'utente ha deciso, si registra; se pensi che non sia una fonte (per esempio è una
nostra misura), diglielo in una riga prima di scrivere. Se decidi tu, registra e dillo nel
resoconto, con il motivo.

Un'informazione si registra come fonte quando valgono tutte e tre:

1. **viene da fuori**: non l'abbiamo misurata né dedotta noi;
2. **tocca i registri**: conferma, smentisce o indebolisce un'ipotesi, risponde a una domanda
   aperta, contraddice un fatto verificato, motiva o cambia una scelta, oppure è un riferimento
   che citeremo;
3. **si può ricontrollare**: c'è il testo, il documento, il link o l'immagine, e una data.

Se manca la prima, è un lavoro per `/research-flow:annota`. Se manca la seconda, non si registra:
un'informazione che non tocca niente è rumore. Se manca la terza, chiedi all'utente da dove viene
prima di scriverla; se si registra lo stesso, l'affidabilità lo dice.

Nel dubbio (un commento detto di passaggio, un messaggio privato, un'origine poco chiara),
**chiedi in una riga** invece di registrare.

## 1. Nuova o già conosciuta?

L'indice delle fonti è `fonti/README.md` (modello `${CLAUDE_PLUGIN_ROOT}/templates/fonti_indice.md`):
una riga per fonte, con che cos'è, perché ne sa qualcosa, quanto ci fidiamo, i suoi file, e chi
l'ha aggiunta e quando.

- **Fonte già nell'indice** → usi i suoi file (passo 3).
- **Fonte nuova** → aggiungi la sua riga all'indice. L'**affidabilità** si scrive con il motivo:
  «alta: documentazione ufficiale del fornitore», «media: utente esperto, di seconda mano», «bassa:
  post anonimo, non verificabile». Se l'indice non esiste, crealo dal modello.

## 2. Raccogli il materiale

Tieni il testo **com'è**, senza riassumere. Secondo il tipo di fonte:

- **persona**: le sue parole, separate dalle nostre domande. Se ci sono domande in sospeso nella
  sezione delle domande aperte di da_fare («Da chiedere a…»), abbina ogni risposta alla sua
  domanda. Una risposta che non corrisponde a nessuna domanda è una dichiarazione spontanea;
- **documento, documentazione, articolo, pagina web**: gli estratti che contano, citati alla
  lettera, con pagina o sezione, il link e la data di consultazione (le pagine web cambiano). Per
  un documento lungo non si copia tutto: si cita quello che tocca i registri;
- **messaggio, screenshot, immagine**: leggila e trascrivi quello che mostra. Se è una tabella,
  metti i dati in `data/` (CSV o testo) e cita il file dell'immagine;
- **dataset di terzi**: in `data/`, con la provenienza (chi, dove, quando, con che licenza).

## 3. Scrivi il file della fonte

In `fonti/`, un file per fonte e per data, dal modello `${CLAUDE_PLUGIN_ROOT}/templates/fonte.md`:
per una fonte già nell'indice segui il nome dei suoi file, per una nuova
`<nome della fonte>_<GG-MM-AAAA>.md`. Se la fonte ha già un file dello stesso giorno, o se
questa informazione risponde a domande di un file precedente, **aggiungi una sezione datata a quel
file** invece di crearne uno nuovo: le risposte stanno vicino alle domande.

Ogni informazione ha un **codice** dentro la sua fonte, che i registri citano insieme al nome e
alla data («<fonte>, R12, GG-MM-AAAA»). Il codice continua la numerazione dei file precedenti
della stessa fonte:

- persona: R1, R2… per le risposte a una nostra domanda, D1, D2… per le dichiarazioni spontanee;
- documento o pagina: E1, E2… per gli estratti, ognuno con la pagina o la sezione da cui viene.

## 4. Propaga

Per ogni informazione, nell'ordine:

1. **È un fatto detto esplicitamente?** Una voce `VER-NNN` (`registri.py next verificato`) nella
   sezione delle fonti esterne: fatto, fonte con codice e data, cosa cambia. Se l'affidabilità
   della fonte è bassa, non è un fatto verificato: è un'ipotesi («Da dove: <fonte>, E3»).
2. **Tocca un'ipotesi?** Cerca con `graphify query` e `grep` nel registro ipotesi.
   - la conferma o la smentisce esplicitamente → la voce VER dice «Confermata/Smentita (era
     IP-NNN)», l'ipotesi va a `→ VER-NNN`, riga in «Smentite o confermate»;
   - la rende più o meno probabile senza chiuderla → una riga nell'ipotesi («<fonte>, R12, del
     GG-MM: …») e l'ipotesi resta aperta;
   - apre una possibilità nuova → un'ipotesi nuova, «Da dove: <fonte>, R12».
3. **Contraddice un fatto già verificato?** Non sovrascrivere: scrivi la contraddizione in tutte
   e due le voci e segnalala all'utente. Due fonti che non concordano sono un'informazione, e di
   solito una domanda nuova.
4. **Chiude una domanda aperta?** Toglila dalla sezione delle domande di da_fare. Se la risposta è
   parziale, riscrivi la domanda con quello che manca.
5. **Fa nascere domande nuove?** Aggiungile in fondo alla sezione delle domande, con gli ID che
   chiuderebbero e a chi o a cosa vanno fatte.
6. **Cambia una scelta, o un'ipotesi con impatto alto?** Il documento ufficiale: la riga nel
   registro delle modifiche con la fonte, e le sezioni toccate. Se cambia più di una sezione,
   passa a `/research-flow:stato`.
7. **Invalida un esperimento o un report?** Una nota nell'esperimento («da rileggere alla luce di
   <fonte>, R12»), e se serve un TODO per rifarlo.

In fondo al file della fonte, sezione «Cosa cambia nei registri», elenca gli ID creati e
aggiornati.

## 5. Controlla e aggiorna il grafo

```bash
python3 registri.py check
```

Nessun errore prima di chiudere; poi il grafo, se c'è: la skill graphify con `--update` (sono
cambiati documenti e forse immagini).

## 6. Resoconto

All'utente: se la fonte è nuova, chi l'ha decisa (tu o lui) e perché, con l'affidabilità
assegnata; le informazioni registrate con il loro codice; le voci create e aggiornate; le
contraddizioni trovate; le domande nuove. Non committare.
