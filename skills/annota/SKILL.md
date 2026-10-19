---
name: annota
description: "Scrive nei registri della documentazione esplorativa: aggiunge una voce (dubbio sul codice, ipotesi, fatto verificato, esperimento, cosa da fare) o ne cambia lo stato — chiude un esperimento con il suo esito, anche e soprattutto se è fallito; sposta un'ipotesi confermata o smentita in verificato; segna un dubbio risolto o un TODO fatto — e propaga il cambiamento alle voci collegate. Cerca prima nei registri e con graphify se la cosa è già scritta. Trigger: /research-flow:annota, «annota che…», «segna questo dubbio», «registra l'esperimento», «l'esperimento X è fallito», «questa ipotesi è smentita», «chiudi TODO-N», «abbiamo provato e non funziona», «tieni traccia di…»."
argument-hint: "<cosa annotare, in parole> | esito ESP-N | risolto DUB-N | fatto TODO-N"
---

# /research-flow:annota

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md` (le sezioni «Dove va questa cosa?», «Le voci» e
«La propagazione») e `.research-flow.json` nella radice del repo, che dice dove stanno i registri
e con che prefissi. Se la configurazione non c'è, fermati e proponi `/research-flow:init`.

Lo script `${CLAUDE_PLUGIN_ROOT}/scripts/registri.py` (lo chiamiamo `registri.py`) non scrive
niente: ti dà l'ID successivo, ti dice dove una voce è definita e chi la cita, e controlla la
coerenza alla fine. **Gli ID non si contano mai a mano.**

## Usage

```
/research-flow:annota <cosa, in parole>        # una voce nuova: la skill decide il registro
/research-flow:annota esito ESP-012 <esito>    # chiude un esperimento e propaga
/research-flow:annota risolto DUB-004 <come>   # chiude un dubbio
/research-flow:annota fatto TODO-015 #52       # chiude un TODO
/research-flow:annota                          # annota quello che è emerso in questa conversazione
```

Senza argomenti, rileggi la conversazione e proponi all'utente l'elenco delle cose da annotare
(dubbi nati sul codice, parametri scelti da noi, esperimenti fatti, anche quelli andati male)
prima di scriverle.

## 1. Capisci cosa hai in mano

Usa la tabella «Dove va questa cosa?» di METODO.md. Una cosa sola può toccare più registri: un
esperimento concluso produce un `ESP` concluso, un `VER` e magari chiude un `IP`. Se il tipo
non si capisce dalla richiesta, chiedilo in una riga invece di indovinare.

**Prima chiediti se deve entrare** (METODO.md, «Cosa entra nei registri»): nei registri va quello
che può cambiare una decisione. Una cosa piccola trovata lavorando (un commento superato, un
numero vecchio in un documento, una differenza di forma) non diventa una voce: si sistema subito o
va in una issue del tracker. Se l'utente chiede esplicitamente di annotarla, la annoti.

## 2. Cerca se c'è già

Prima di scrivere una voce nuova, in quest'ordine:

```bash
python3 registri.py find <ID>                # per ogni ID che la richiesta nomina: definizione e chi la cita
grep -n -i '<parola chiave>' <dir>/*.md      # con le parole dei registri, e più di una
python3 registri.py scartate                 # se è un'idea da provare: è già stata scartata?
```

`registri.py find` dà la definizione e tutte le citazioni, nei registri, nei report e nel
codice, con file e riga: è quello che serve per passare da una voce ai report e al codice. Il
`grep` si fa con i termini dei registri, provando i sinonimi: chi cerca per parole trova una voce
solo se la descrive con le parole con cui è scritta (su 14 voci descritte con altre parole,
`graphify query` ne trovava 7). Il grafo graphify, se c'è, serve per il codice (`graphify explain
"<simbolo>"`); i registri di solito ne sono esclusi (METODO.md, «Graphify»).

- se la voce **esiste già**, la aggiorni: non ne crei una seconda;
- se esiste una voce **vicina**, la nuova la cita, e se serve la vicina cita la nuova;
- se tocca il codice, trova file e simbolo (`graphify explain`, `grep`) e **verificali leggendo
  il file**: una voce con un riferimento sbagliato è peggio di una senza. Si cita il simbolo, mai
  il numero di riga, che si sposta alla prima modifica (METODO.md, «Lo stile»).

## 3. Scrivi la voce

```bash
python3 registri.py next <tipo>              # es. next esperimenti → ESP-014
```

Segui il formato scritto in testa al registro (e i modelli in `${CLAUDE_PLUGIN_ROOT}/templates/`).
Metti la voce nella sezione giusta: le aperte in alto, le chiuse nella sezione dei chiusi, le più
recenti per prime. Rispetta lo stile di METODO.md: numeri misurati, date `GG-MM-AAAA`, e sempre
**perché conta**.

Per tipo, quello che non deve mancare:

- **dubbio:** `Dove` con file e simbolo verificati; come si risolve è una proposta, non una
  decisione. Un dubbio entra se può cambiare un risultato o una scelta.
- **ipotesi:** `Dove la usiamo` (se è un parametro nostro, il nome nel codice o nella
  configurazione) e `Come si verifica` concreto. Se l'impatto è alto e il rischio è fra i più
  gravi, va anche nell'ufficiale, «Dove potremmo sbagliare» (vedi passo 5).
- **fatto verificato:** la fonte ricontrollabile. Una misura dice script, dati e data. Un fatto
  da una fonte esterna passa di norma da `/research-flow:fonte`, che scrive anche le parole
  originali.
- **esperimento proposto:** domanda sì/no e **criterio di successo scritto adesso**. Se l'utente
  non lo dà, proponilo tu e faglielo confermare: è l'unico momento in cui si può scrivere onesto.
- **TODO:** fase, priorità, e il perché con gli ID che chiude.

## 4. Chiudere una voce

**`esito ESP-NNN`.** È il caso più importante, e il più facile da fare male.

1. L'esito è una delle quattro parole: `positivo`, `negativo`, `inconcludente`, `abbandonato`,
   con il significato di METODO.md, «Cosa vuol dire l'esito»: `positivo` vuol dire che l'idea
   messa alla prova regge. Si decide **confrontando il risultato con il criterio scritto quando
   l'esperimento è stato proposto**, non con quello che ci si aspettava dopo. Se il criterio non
   c'era, dillo nella voce.
2. Il report deve esistere in `misure/` (modello `templates/report.md`). Se non c'è, scrivilo, o
   chiedi all'utente dove sta il risultato e scrivilo nel campo Report: senza, `check` avvisa.
3. «Cosa ne abbiamo tratto»: cosa cambia, e per un esito negativo o abbandonato **cosa non
   rifare e a quali condizioni avrebbe senso riprovare**. Non addolcire un fallimento: «non
   funziona con questi dati per questo motivo» è l'informazione che serve.
4. Sposta la voce in «Conclusi», stato `concluso (GG-MM-AAAA)`.

**Ipotesi confermata o smentita.** Nasce una voce `VER-NNN` (`registri.py next verificato`) che
dice «**Confermata** (era IP-NNN)» o «**Smentita** (era IP-NNN)», con la fonte. Lo stato
dell'ipotesi diventa `→ VER-NNN`; la voce resta dov'è con il suo testo, e in «Smentite o
confermate» aggiungi la riga. Mai cancellare l'ipotesi.

**`risolto DUB-NNN`.** Stato `risolto (GG-MM-AAAA, commit/PR)`, una riga su come, voce spostata
in «Risolti». `accettato` invece resta fra gli aperti, con il motivo per cui lo teniamo così.

**`fatto TODO-NNN`.** La riga si sposta nella tabella «Fatto» con l'issue o la PR e la data.

## 5. Propaga

Segui la tabella «La propagazione» di METODO.md. In pratica, dopo ogni voce chiediti:

- tocca un'altra voce? Aggiornala e cita l'ID nuovo (un'ipotesi `in verifica (ESP-NNN)`
  quando parte l'esperimento; il TODO che l'esperimento chiude; il dubbio che una misura risolve);
- cambia lo stato del progetto? Allora va nel documento ufficiale, che è breve (un tetto di
  parole): entra solo quello che conta per chi lo legge.
  - ogni cambiamento di una scelta → «Le scelte in vigore», una riga nel registro delle
    modifiche e la data in testa;
  - esperimento **positivo**, o **negativo** su un'alternativa importante → una riga in «Cosa
    abbiamo imparato»; gli altri esiti negativi, abbandonati e le ipotesi smentite restano nel
    registro, e li elenca `registri.py scartate`: non serve ricopiarli;
  - **negativo** su una scelta in vigore, **inconcludente** su una cosa che regge una scelta,
    ipotesi con impatto alto → «Dove potremmo sbagliare» se è fra i cinque rischi più gravi, e
    un TODO per rimediare.

  Per una riga basta modificare la sezione; se cambiano più sezioni o una scelta importante,
  passa a `/research-flow:stato`, che riscrive l'ufficiale e salva la fotografia.
- cambia qualcosa che i documenti specchio ripetono (`specchi` nella configurazione)? Aggiornali.

## 6. Controlla e aggiorna il grafo

```bash
python3 registri.py check
```

Nessun errore prima di chiudere. Il grafo non si aggiorna per i soli registri (di solito sono
esclusi da `.graphifyignore`); se hai scritto anche un report o una fonte, l'estrazione semantica
si fa una volta sola, alla fine del lavoro.

## 7. Resoconto

Una riga per voce toccata: `ESP-014 creato (proposto)`, `IP-006 → VER-031 (smentita)`,
`stato_progetto.md § Cosa abbiamo imparato +1`. Non committare.
