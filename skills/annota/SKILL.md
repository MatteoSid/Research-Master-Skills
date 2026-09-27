---
name: annota
description: "Scrive nei registri della documentazione esplorativa: aggiunge una voce (dubbio sul codice, ipotesi, fatto verificato, esperimento, cosa da fare) o ne cambia lo stato — chiude un esperimento con il suo esito, anche e soprattutto se è fallito; sposta un'ipotesi confermata o smentita in verificato; segna un dubbio risolto o un TODO fatto — e propaga il cambiamento alle voci collegate. Cerca prima con graphify se la cosa è già scritta. Trigger: /research-flow:annota, «annota che…», «segna questo dubbio», «registra l'esperimento», «l'esperimento X è fallito», «questa ipotesi è smentita», «chiudi TODO-N», «abbiamo provato e non funziona», «tieni traccia di…»."
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

## 2. Cerca se c'è già

Prima di scrivere una voce nuova:

```bash
graphify query "<la cosa, in parole>"        # se esiste graphify-out/graph.json
grep -n -i '<parola chiave>' <dir>/*.md
python3 registri.py find <ID>                # per ogni ID che la richiesta nomina
```

- se la voce **esiste già**, la aggiorni: non ne crei una seconda;
- se esiste una voce **vicina**, la nuova la cita, e se serve la vicina cita la nuova;
- se tocca il codice, trova file e simbolo con `graphify explain` e **verifica la riga leggendo
  il file**: una voce con un riferimento sbagliato è peggio di una senza.

## 3. Scrivi la voce

```bash
python3 registri.py next <tipo>              # es. next esperimenti → ESP-014
```

Segui il formato scritto in testa al registro (e i modelli in `${CLAUDE_PLUGIN_ROOT}/templates/`).
Metti la voce nella sezione giusta: le aperte in alto, le chiuse nella sezione dei chiusi, le più
recenti per prime. Rispetta lo stile di METODO.md: numeri misurati, date `GG-MM-AAAA`, e sempre
**perché conta**.

Per tipo, quello che non deve mancare:

- **dubbio:** `Dove` con file e riga verificati; come si risolve è una proposta, non una decisione.
- **ipotesi:** `Dove la usiamo` (se è un parametro nostro, il nome nel codice o nella
  configurazione) e `Come si verifica` concreto. Se l'impatto è alto, va anche nell'ufficiale,
  «Dove potremmo sbagliare» (vedi passo 5).
- **fatto verificato:** la fonte ricontrollabile. Una misura dice script, dati e data. Un fatto
  da una fonte esterna passa di norma da `/research-flow:fonte`, che scrive anche le parole
  originali.
- **esperimento proposto:** domanda sì/no e **criterio di successo scritto adesso**. Se l'utente
  non lo dà, proponilo tu e faglielo confermare: è l'unico momento in cui si può scrivere onesto.
- **TODO:** fase, priorità, e il perché con gli ID che chiude.

## 4. Chiudere una voce

**`esito ESP-NNN`.** È il caso più importante, e il più facile da fare male.

1. L'esito è una delle quattro parole: `positivo`, `negativo`, `inconcludente`, `abbandonato`.
   Si decide **confrontando il risultato con il criterio scritto quando l'esperimento è stato
   proposto**, non con quello che ci si aspettava dopo. Se il criterio non c'era, dillo nella
   voce.
2. Il report deve esistere in `misure/` (modello `templates/report.md`). Se non c'è, scrivilo o
   chiedi all'utente dove sta: un esperimento concluso senza report è un errore per `check`.
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
- cambia lo stato del progetto? Allora va nel documento ufficiale:
  - esperimento **positivo** → «Cosa funziona», e «Le scelte in vigore» se cambia una scelta;
  - **negativo o abbandonato**, ipotesi **smentita** → una riga in «Strade scartate»;
  - **inconcludente** → «Cosa non abbiamo capito»;
  - ipotesi con impatto alto → «Dove potremmo sbagliare»;
  - ogni cambiamento di una scelta → una riga nel registro delle modifiche e la data in testa.

  Per una riga basta modificare la sezione; se cambiano più sezioni o una scelta importante,
  passa a `/research-flow:stato`, che riscrive l'ufficiale e salva la fotografia.
- cambia qualcosa che i documenti specchio ripetono (`specchi` nella configurazione)? Aggiornali.

## 6. Controlla e aggiorna il grafo

```bash
python3 registri.py check
```

Nessun errore prima di chiudere. Poi aggiorna il grafo, se c'è: la skill graphify con
`--update`, perché sono cambiati documenti.

## 7. Resoconto

Una riga per voce toccata: `ESP-014 creato (proposto)`, `IP-006 → VER-031 (smentita)`,
`stato_progetto.md § Strade scartate +1`. Non committare.
