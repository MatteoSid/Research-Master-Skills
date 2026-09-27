---
name: fonte
description: "Registra un'informazione nuova arrivata da una fonte esterna — una persona che risponde alle nostre domande, un messaggio, uno screenshot, un documento — e la propaga ai registri: le parole originali in fonti/, i fatti in verificato, le ipotesi confermate, smentite o indebolite, le domande tolte da da_fare, il documento ufficiale se cambia una scelta. Tiene separate le parole della fonte dalle nostre deduzioni. Trigger: /research-flow:fonte, «Davide ha risposto…», «è arrivata un'informazione nuova», «mi ha detto che…», «registra questa risposta», «ecco lo screenshot che mi ha mandato»."
argument-hint: "[nome della fonte] <il testo, il file o l'immagine>"
---

# /research-flow:fonte

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md` («Due livelli di fiducia» e «La propagazione») e
`.research-flow.json`: la lista `fonti` dice chi sono le fonti del progetto e come si chiamano i
loro file. Se la fonte non è nella lista, chiedi all'utente chi è e aggiungila.

Lo script è `${CLAUDE_PLUGIN_ROOT}/scripts/registri.py` (`registri.py` qui sotto).

## Il principio

**Le parole della fonte e le nostre deduzioni non si mescolano mai.** Una fonte di seconda mano
che dice «il bot rimette l'ordine circa ogni minuto» è un fatto *riferito*; «quindi usa il
last» è una nostra deduzione, cioè un'ipotesi. Chi rilegge fra sei mesi deve poter distinguere
cosa ha detto la fonte da cosa abbiamo capito noi, e ricontrollare le parole esatte.

## 1. Raccogli il materiale

- testo incollato o dettato: tienilo **com'è**, senza riassumere;
- immagini e screenshot: leggile, trascrivi i dati in `data/` (CSV o testo) se sono tabelle, e
  cita il file dell'immagine;
- una conversazione: separa le domande nostre dalle risposte.

Se ci sono domande in sospeso in da_fare («Da chiedere a…»), abbina ogni risposta alla sua
domanda. Una risposta che non corrisponde a nessuna domanda è una dichiarazione spontanea.

## 2. Scrivi il file della fonte

In `fonti/`, con il nome dalla configurazione (di default `info_<nome>_<GG-MM-AAAA>.md`, dal
modello `${CLAUDE_PLUGIN_ROOT}/templates/fonte.md`). Se c'è già un file della stessa fonte dello
stesso giorno, o se la risposta chiude domande di un file precedente, **aggiungi una sezione
datata a quel file** invece di crearne uno nuovo: le risposte stanno vicino alle domande.

Ogni risposta ha un **codice** che continua la numerazione della fonte (R1, R2… per le risposte,
D1, D2… per le dichiarazioni; guarda i codici già usati con `grep -n '| R[0-9]' fonti/`). I
registri citeranno la fonte come «Davide, R12, 27-09-2026».

## 3. Propaga

Per ogni risposta, nell'ordine:

1. **È un fatto detto esplicitamente?** Una voce `VER-NNN` (`registri.py next verificato`) nella
   sezione delle fonti esterne: fatto, fonte con codice e data, cosa cambia.
2. **Tocca un'ipotesi?** Cerca con `graphify query` e `grep` nel registro ipotesi.
   - la conferma o la smentisce esplicitamente → la voce VER dice «Confermata/Smentita (era
     IP-NNN)», l'ipotesi va a `→ VER-NNN`, riga in «Smentite o confermate»;
   - la rende più o meno probabile senza chiuderla → una riga nell'ipotesi («R12 del 27-09: …»)
     e resta aperta;
   - apre una possibilità nuova → un'ipotesi nuova, «Da dove: <fonte>, R12».
3. **Contraddice un fatto già verificato?** Non sovrascrivere: scrivi la contraddizione in
   tutte e due le voci e segnalala all'utente. Due fonti che non concordano sono
   un'informazione, e di solito una domanda nuova.
4. **Chiude una domanda?** Toglila da «Da chiedere a…» in da_fare. Se la risposta è parziale,
   riscrivi la domanda con quello che manca.
5. **Fa nascere domande nuove?** Aggiungile in fondo a «Da chiedere a…», con gli ID che
   chiuderebbero.
6. **Cambia una scelta, o un'ipotesi con impatto alto?** Il documento ufficiale: la riga nel
   registro delle modifiche con la fonte, e le sezioni toccate. Se cambia più di una sezione,
   passa a `/research-flow:stato`.
7. **Invalida un esperimento o un report?** Una nota nell'esperimento («da rileggere alla luce di
   R12»), e se serve un TODO per rifarlo.

In fondo al file della fonte, sezione «Cosa cambia nei registri», elenca gli ID creati e
aggiornati.

## 4. Controlla e aggiorna il grafo

```bash
python3 registri.py check
```

Nessun errore prima di chiudere; poi il grafo, se c'è: la skill graphify con `--update` (sono
cambiati documenti e forse immagini).

## 5. Resoconto

All'utente: le risposte registrate con il loro codice, le voci create e aggiornate, le
contraddizioni trovate, le domande nuove. Non committare.
