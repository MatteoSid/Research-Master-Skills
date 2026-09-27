# Esperimenti

**Ogni esperimento**, riuscito o no. Un esperimento fallito si toglie dal codice, e se non resta
scritto qui qualcuno prima o poi lo rifarà. Questo registro risponde a «l'abbiamo già provato?
com'era andata?».

Come si scrive una voce (forma a intestazione):

- **ID** `ESP-NNN`, progressivo, mai riusato.
- **Domanda:** cosa vogliamo sapere, in una frase che ammette un sì o un no.
- **Tocca:** le voci che l'esperimento verifica o cambia (`IP-NNN`, `DUB-NNN`, `TODO-NNN`).
- **Metodo:** dati, script, e il **criterio di successo deciso prima** di guardare i risultati.
- **Report:** `misure/report_<tema>_<data>.md` e gli script in `val/`. Obbligatorio a esperimento
  concluso; per una misura senza report, dove sta il risultato («nessun report in `misure/`: la
  misura è in …»).
- **Esito:** `positivo`, `negativo`, `inconcludente` o `abbandonato`, e in una frase il risultato
  con i numeri. Solo a esperimento concluso. La domanda si scrive in modo che «sì» voglia dire
  «l'idea regge»: `positivo` è sì, `negativo` è no.
- **Cosa ne abbiamo tratto:** cosa cambia (`VER-NNN`, scelte del documento ufficiale). Se è
  negativo o abbandonato: **cosa non rifare, e a quali condizioni avrebbe senso riprovare**.
- **Origine** (facoltativo): il nome che aveva prima, se ne aveva uno («era E7 in …», «TODO-042»).
- **Stato:** `proposto`, `in corso (#issue)`, `concluso (data)`.

---

## In corso

## Proposti

## Conclusi

I più recenti in alto.
