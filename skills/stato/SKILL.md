---
name: stato
description: "Riscrive la versione ufficiale del progetto (stato_progetto.md) dai registri, in forma breve, entro un tetto di parole: l'obiettivo, le scelte in vigore con i numeri, cosa abbiamo imparato, dove potremmo sbagliare, i prossimi passi e il registro delle modifiche; salva prima la fotografia della versione vecchia e allinea i documenti specchio. Con «leggi» risponde a «a che punto siamo?» senza scrivere. Trigger: /research-flow:stato, «aggiorna lo stato del progetto», «riscrivi la versione ufficiale», «a che punto siamo?», «cosa abbiamo scartato?», «cosa non abbiamo ancora capito?»."
argument-hint: "[leggi | <motivo dell'aggiornamento>]"
---

# /research-flow:stato

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md`, sezione «Il documento ufficiale», e
`.research-flow.json` (`ufficiale` è il file, `ufficiale_parole_max` il tetto, `specchi` i
documenti da allineare). Lo script è `${CLAUDE_PLUGIN_ROOT}/scripts/registri.py` (`registri.py`
qui sotto).

## Il principio

Il documento ufficiale non contiene niente che non sia in un registro: **è una vista, non una
fonte.** Ogni affermazione porta l'ID della voce che la regge, e il lettore capisce dal tipo di
ID quanto è solida: `VER` è verificata, `IP` è un'ipotesi, `ESP` negativo è una strada scartata.
Se nel riscriverlo trovi una cosa che non ha una voce, la voce va creata (con
`/research-flow:annota`), non inventata qui.

**Ed è breve: si legge in una volta.** Il tetto di parole (1.500 di default, senza il registro
delle modifiche) lo controlla `registri.py check`. Per stare dentro il tetto non si comprime il
testo: si sceglie. Una scelta in una o due righe con i numeri che contano; il resto è nei
registri, citato per ID.

## Usage

```
/research-flow:stato                   # riscrive l'ufficiale dai registri
/research-flow:stato <motivo>          # idem, con il motivo nel registro delle modifiche
/research-flow:stato leggi             # risponde «a che punto siamo?» senza scrivere niente
```

## 1. Leggi quello che è cambiato

```bash
python3 registri.py riepilogo           # voci per registro, per stato, esiti degli esperimenti
python3 registri.py scartate            # le strade scartate, con cosa ne abbiamo tratto
python3 registri.py check               # prima si sistemano gli errori: una vista su registri rotti è rotta
```

Poi l'ufficiale di oggi e, dalla data in testa, quello che è cambiato nei registri:
`git log -p --since=<data> -- <dir>/`. Non serve rileggere i registri per intero: le voci che
non sono cambiate dall'ultima riscrittura sono già dentro, o sono state lasciate fuori di
proposito.

Con `leggi` ti fermi qui: rispondi all'utente seguendo le sezioni dell'ufficiale, in breve, con gli
ID, e segnala se l'ufficiale è indietro rispetto ai registri.

## 2. Fotografia

Se cambia una scelta in vigore, o se l'ultima fotografia in `storico/` ha più di qualche
settimana, copia l'ufficiale di oggi in `storico/<nome dell'ufficiale senza .md>_<GG-MM-AAAA>.md`
**prima** di toccarlo, con in testa l'avviso di fotografia (METODO.md, «Le fotografie»). Per
aggiornamenti di contorno (una riga in «Cosa abbiamo imparato», un passo fatto) non serve.

## 3. Riscrivi

Le sei sezioni di METODO.md, in ordine. **Tieni le sottosezioni di dominio** che il progetto ha
aggiunto dentro «Le scelte in vigore», con la loro numerazione: il codice e gli altri documenti
le citano (`stato_progetto.md` §2.5). Sezione per sezione, dove prendere il contenuto:

| Sezione | Da dove |
|---|---|
| 1. L'obiettivo e l'idea | resta com'è, salvo che un fatto nuovo lo cambi |
| 2. Le scelte in vigore | l'ufficiale di oggi, corretto con le voci nuove; ogni scelta in una o due righe, con i numeri che contano e l'ID che la regge |
| 3. Cosa abbiamo imparato | le scoperte che hanno cambiato una scelta, quelle che l'hanno confermata (`VER` di misura, `ESP` positivi) e le strade importanti scartate (`registri.py scartate`), una riga ciascuna; chiudi la sezione con il rimando a `registri.py scartate` per l'elenco completo |
| 4. Dove potremmo sbagliare | al massimo cinque: le `IP` con impatto alto che reggono la §2, gli `ESP` negativi su una scelta in vigore, gli `ESP` inconcludenti e i `DUB` aperti che toccano i risultati, i rischi che i dati non misurano. Scegli i più gravi |
| 5. Prossimi passi | al massimo tre, in ordine, dai `TODO` P0 e dalla roadmap del progetto |
| 6. Registro delle modifiche | aggiungi in alto la riga di oggi, con la fonte (issue, ESP, fonte esterna); tieni le righe delle ultime settimane e rimanda alla fotografia per le altre |

Non vanno nell'ufficiale: le ipotesi aperte a impatto basso, gli esperimenti proposti, i dubbi
che non toccano i risultati, il lavoro da fare oltre i tre passi. Stanno nei registri e nella
pagina di `/research-flow:overview`.

In testa: `**Aggiornato al GG-MM-AAAA.**` con la data di oggi.

## 4. Documenti specchio

Per ogni voce di `specchi` nella configurazione: rileggi il documento e allinealo a quello che è
cambiato nell'ufficiale. Sono documenti di altri (l'app, il README pubblico): cambia il
contenuto, non la forma. **I numeri non si riscrivono a mano**: uno specchio li legge dal codice o
da un'API (METODO.md, «Gli specchi»); se ne trovi uno scritto a mano, sistemalo o dillo
all'utente. Se uno specchio è codice, dopo la modifica lancia i controlli del progetto (lint,
build) come dice il suo `CLAUDE.md`.

## 5. Controlla

```bash
python3 registri.py check
```

Gli avvisi `ufficiale-vecchio` e `ufficiale-lungo` devono essere spariti. Se l'ufficiale è escluso
dal grafo (`.graphifyignore`), il grafo non va aggiornato; altrimenti `graphify update .` per il
codice degli specchi e l'estrazione semantica per i documenti, una volta, alla fine.

## 6. Resoconto

All'utente: cosa è cambiato nell'ufficiale, sezione per sezione in una riga; le parole contate;
la fotografia salvata (se l'hai salvata); gli specchi aggiornati; le cose che hai trovato senza
una voce e che vanno annotate. Non committare.
