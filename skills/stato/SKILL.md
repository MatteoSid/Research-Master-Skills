---
name: stato
description: "Riscrive la versione ufficiale del progetto (stato_progetto.md) dai registri: le scelte in vigore, cosa funziona, cosa è da testare, cosa manca, cosa non abbiamo capito, le strade scartate, dove potremmo sbagliare, i prossimi passi e il registro delle modifiche; salva prima la fotografia della versione vecchia e allinea i documenti specchio. Con «leggi» risponde a «a che punto siamo?» senza scrivere. Trigger: /research-flow:stato, «aggiorna lo stato del progetto», «riscrivi la versione ufficiale», «a che punto siamo?», «cosa abbiamo scartato?», «cosa non abbiamo ancora capito?»."
argument-hint: "[leggi | <motivo dell'aggiornamento>]"
---

# /research-flow:stato

Prima leggi `${CLAUDE_PLUGIN_ROOT}/METODO.md`, sezione «Il documento ufficiale», e
`.research-flow.json` (`ufficiale` è il file, `specchi` i documenti da allineare). Lo script è
`${CLAUDE_PLUGIN_ROOT}/scripts/registri.py` (`registri.py` qui sotto).

## Il principio

Il documento ufficiale non contiene niente che non sia in un registro: **è una vista, non una
fonte.** Ogni affermazione porta l'ID della voce che la regge, e il lettore capisce dal tipo di
ID quanto è solida: `VER` è verificata, `IP` è un'ipotesi, `ESP` negativo è una strada scartata.
Se nel riscriverlo trovi una cosa che non ha una voce, la voce va creata (con
`/research-flow:annota`), non inventata qui.

## Usage

```
/research-flow:stato                   # riscrive l'ufficiale dai registri
/research-flow:stato <motivo>          # idem, con il motivo nel registro delle modifiche
/research-flow:stato leggi             # risponde «a che punto siamo?» senza scrivere niente
```

## 1. Leggi i registri

```bash
python3 registri.py riepilogo           # voci per registro, per stato, esiti degli esperimenti
python3 registri.py check               # prima si sistemano gli errori: una vista su registri rotti è rotta
```

Poi leggi i registri per intero e l'ufficiale di oggi. Dalla data in testa all'ufficiale,
`git log --since=<data> -- <dir>/` ti dice cosa è cambiato da allora: parti da lì.

Con `leggi` ti fermi qui: rispondi all'utente seguendo le dieci sezioni, in breve, con gli ID,
e segnala se l'ufficiale è indietro rispetto ai registri.

## 2. Fotografia

Se cambia una scelta in vigore, o se l'ultima fotografia in `storico/` ha più di qualche
settimana, copia l'ufficiale di oggi in `storico/<nome dell'ufficiale senza .md>_<GG-MM-AAAA>.md`
**prima** di toccarlo, con in testa l'avviso di fotografia (METODO.md, «Le fotografie»). Per
aggiornamenti di contorno (una riga in «Strade scartate», un TODO fatto) non serve.

## 3. Riscrivi

Le dieci sezioni di METODO.md, in ordine. **Tieni le sottosezioni di dominio** che il progetto ha
aggiunto (vanno dentro o prima di «Le scelte in vigore»): non sono del modello, ma sono del
progetto. Sezione per sezione, dove prendere il contenuto:

| Sezione | Da dove |
|---|---|
| 1. L'obiettivo e l'idea | resta com'è, salvo che un fatto nuovo lo cambi |
| 2. Le scelte in vigore | l'ufficiale di oggi, corretto con le voci nuove; ogni scelta con l'ID che la regge |
| 3. Cosa funziona | `VER` di misura, `ESP` positivi, `TODO` fatti che hanno cambiato cosa sappiamo fare |
| 4. Cosa è da testare | `IP` aperte che reggono le scelte della §2 (prima quelle ad alto impatto), `ESP` in corso e i proposti più importanti |
| 5. Cosa manca | `TODO` P0 e P1 non fatti, per fase |
| 6. Cosa non abbiamo capito | `ESP` inconcludenti, domande aperte alle fonti che bloccano qualcosa, `DUB` aperti che toccano i risultati, contraddizioni fra fonti |
| 7. Strade scartate | **ogni** `ESP` negativo su un'alternativa, **ogni** `ESP` abbandonato e **ogni** `IP` smentita: nessuna esclusa, una riga ciascuna, con «si riprova se…» |
| 8. Dove potremmo sbagliare | `IP` con impatto alto, `ESP` negativi su una scelta in vigore, rischi noti che i dati non misurano |
| 9. Prossimi passi | in ordine, dai TODO e dalla roadmap del progetto |
| 10. Registro delle modifiche | le righe esistenti **restano tutte**; aggiungi in alto quella di oggi, con la fonte (issue, ESP, fonte esterna) |

Le §6-§8 sono quelle che si dimenticano. Il controllo incrociato lo fa `registri.py check` al
passo 5: ogni esperimento negativo, abbandonato o inconcludente e ogni ipotesi smentita deve
comparire nell'ufficiale, altrimenti dà l'avviso `esito-non-citato`. Lo script controlla che l'ID
ci sia, non che stia nella sezione giusta: quello lo controlli tu con la regola di METODO.md
(alternativa bocciata → §7, scelta in vigore messa in dubbio → §8 o §6).

In testa: `**Aggiornato al GG-MM-AAAA.**` con la data di oggi.

## 4. Documenti specchio

Per ogni voce di `specchi` nella configurazione: rileggi il documento e allinealo a quello che è
cambiato nell'ufficiale. Sono documenti di altri (l'app, il README pubblico): cambia il
contenuto, non la forma. Se uno specchio è codice (componenti che mostrano testo, costanti),
dopo la modifica lancia i controlli del progetto (lint, build) come dice il suo `CLAUDE.md`.

## 5. Controlla e aggiorna il grafo

```bash
python3 registri.py check
```

L'avviso «ufficiale-vecchio» deve essere sparito. Poi il grafo, se c'è: `graphify update .` se
hai toccato codice negli specchi, e la skill graphify con `--update` per i documenti.

## 6. Resoconto

All'utente: cosa è cambiato nell'ufficiale, sezione per sezione in una riga; la fotografia salvata
(se l'hai salvata); gli specchi aggiornati; le cose che hai trovato senza una voce e che vanno
annotate. Non committare.
