# Il metodo

Questo file è il regolamento comune delle skill di research-flow: lo leggono tutte prima di
scrivere. Descrive **come si tiene la conoscenza di un progetto esplorativo**, un progetto in cui
nemmeno chi ci lavora sa dove andrà a finire, e dove quello che si impara conta quanto il codice.

## Il principio

**Un esperimento fallito documentato vale quanto uno riuscito.** Il successo resta nel codice e
si va avanti. Il fallimento invece si toglie dal codice, e se nessuno lo scrive fra tre mesi
qualcuno rifarà lo stesso esperimento, o peggio lo darà per riuscito. Tutto il resto viene da qui:

- **niente si cancella.** Una voce chiusa resta con il suo stato e il motivo per cui è chiusa;
  un ID non si riusa mai;
- **ogni affermazione ha uno stato**: è un fatto verificato, un'ipotesi, un dubbio, un lavoro
  da fare, o il risultato di un esperimento. Nel documento ufficiale non c'è niente che non si
  ritrovi in un registro;
- **ogni fatto ha una fonte che si può ricontrollare**: chi l'ha detto e quando, oppure lo
  script, i dati e la data della misura;
- **il criterio di successo si decide prima.** Un esperimento senza un criterio scritto prima
  di guardare i risultati finisce sempre per «confermare» qualcosa.

Il test che decide se una voce è scritta bene: **chi apre il repo fra sei mesi, senza aver
assistito alla conversazione, capisce da solo cosa sappiamo, come lo sappiamo e cosa resta
aperto?** Se no, manca qualcosa: la fonte, il numero misurato, il file e la riga, il motivo.

## I documenti

La configurazione del progetto (`.research-flow.json` nella radice del repo) dice in che
cartella stanno e come si chiamano. Qui li chiamiamo per tipo; `dir` è la cartella, di solito
`research/`.

| Tipo | File di default | Prefisso | Cosa ci va |
|---|---|---|---|
| dubbi | `dubbi_implementazione.md` | `DUB` | dubbi sul **nostro codice**: una scelta che potrebbe essere sbagliata, un valore copiato a mano, un limite noto, un comportamento che non sappiamo se è voluto |
| ipotesi | `ipotesi_da_verificare.md` | `IP` | quello che **stiamo assumendo** e nessuno ha dimostrato, con come si verifica e l'impatto se è sbagliato |
| verificato | `verificato.md` | `VER` | quello che **sappiamo**: fatti da una fonte, misure nostre, verifiche sul codice, ognuno con la fonte |
| esperimenti | `esperimenti.md` | `ESP` | **ogni esperimento**, proposto, in corso o concluso, con il suo esito: positivo, negativo, inconcludente o abbandonato |
| da_fare | `da_fare.md` | `TODO` | tutto il lavoro che manca per arrivare all'obiettivo, per fase e priorità, e le domande aperte alle fonti |
| ufficiale | `stato_progetto.md` | — | **la versione ufficiale**: le scelte in vigore, cosa funziona, cosa è da testare, cosa manca, cosa non abbiamo capito, le strade scartate, dove potremmo sbagliare |

Al primo livello di `dir` stanno **solo questi sei**. Tutto il resto sta in sottocartelle per
ruolo, e i registri lo citano:

| Cartella | Cosa contiene |
|---|---|
| `fonti/` | le informazioni che arrivano da fuori (persone, documenti, messaggi): una per file, datata, con le parole originali |
| `misure/` | i report di misura e degli esperimenti: `report_<tema>_<GG-MM-AAAA>.md`, ognuno con domanda, metodo, risultati, limiti |
| `storico/` | le fotografie dei documenti ufficiali superati: `stato_progetto_<data>.md` |
| `riferimenti/` | documentazione tecnica di terzi |
| `data/` | dati grezzi citati dai report |
| `val/` | script di analisi e i loro output |
| altre | brainstorm, ricerche iniziali: materiale di partenza, citato ma non tenuto aggiornato |

Dentro `dir` i percorsi si scrivono **relativi a `dir`** (`misure/report_x_2026-09-24.md`); fuori
(codice, `README.md`) dalla radice del repo. Se sposti un file aggiorni **tutte** le citazioni:
`registri.py find` e `grep` le trovano.

### Dove va questa cosa?

| Hai in mano… | Va in |
|---|---|
| «Questo pezzo di codice forse è sbagliato / fragile / approssimato» | dubbi |
| «Stiamo dando per scontato che…», «abbiamo scelto X ma non sappiamo se è giusto» | ipotesi |
| «Tizio ci ha detto che…» | la parola esatta in `fonti/`, il fatto in verificato (fonte esterna) |
| «Abbiamo misurato che…» | il report in `misure/`, il fatto in verificato (misura), l'esperimento in esperimenti |
| «Proviamo a vedere se…» | esperimenti, stato `proposto`, con il criterio deciso adesso |
| «Abbiamo provato e non funziona» | esperimenti, esito `negativo`: **soprattutto questo** |
| «Prima o poi bisogna…» | da_fare |
| «Non abbiamo capito perché…» | ipotesi se c'è una spiegazione candidata da verificare, altrimenti in ufficiale § «Cosa non abbiamo capito» e, se si può indagare, un esperimento proposto |
| «Da adesso facciamo così» | ufficiale § «Le scelte in vigore», con una riga nel registro delle modifiche |

Se una cosa ne tocca più di uno, va in tutti, e le voci si citano a vicenda per ID.

## Le voci

Ogni voce ha un **ID** `<PREFISSO>-NNN` progressivo, mai riusato: il successivo lo dà
`registri.py next <tipo>`, non si conta a mano. Le voci si citano per ID ovunque: nei registri,
nei report, nel documento ufficiale, nei commenti del codice, nelle issue.

Due forme, e ogni registro dichiara in testa la sua:

- **a intestazione** (dubbi, ipotesi, esperimenti): `### IP-012 · Il titolo in una frase`, poi i
  campi come elenco `- **Campo:** testo`. Serve quando la voce ha bisogno di spiegazione;
- **a tabella** (verificato, da_fare): una riga per voce, con l'ID nella prima colonna. Serve
  quando la voce è un fatto o un compito in una riga.

I campi obbligatori li controlla `registri.py check`. Il campo **Stato** è sempre l'ultimo.

### Il ciclo di vita

```
ipotesi   da verificare ──► in verifica (ESP-NNN) ──► → VER-NNN  (confermata o smentita)
                                                        │
esperimenti   proposto ──► in corso (#issue) ──► concluso (data), Esito: positivo | negativo
                    │                                             inconcludente | abbandonato
                    └──────────────► concluso (data), Esito: abbandonato  (con il motivo)

dubbi     aperto ──► in lavorazione (#issue) ──► risolto (data, commit/PR) | accettato (motivo)
da_fare   da fare ──► in corso (#issue) ──► fatto (#issue, data)
```

- **Un'ipotesi non si cancella quando si chiude**: nasce una voce `VER-NNN` che dice «era
  IP-NNN» e riporta se è confermata o **smentita**, e lo stato dell'ipotesi diventa
  `→ VER-NNN`. In fondo al file delle ipotesi, in «Smentite o confermate», una riga la ricorda.
- **Un esperimento concluso ha sempre un esito**, e l'esito è una delle quattro parole. Il campo
  «Cosa ne abbiamo tratto» dice cosa cambia e, se è negativo, **cosa non rifare e a quali
  condizioni avrebbe senso riprovare** (con più dati, con un'altra definizione…).
  `inconcludente` non è un fallimento da nascondere: dice che i dati non bastano, e di solito
  genera un TODO.
- Le voci chiuse si spostano nella sezione dei chiusi del loro registro («Risolti», «Conclusi»,
  «Fatto»), le più recenti in alto.

### Due livelli di fiducia

Nel registro verificato si tengono distinti:

- **fonte esterna**: un fatto riferito da qualcuno (con nome, data e codice della risposta).
  È la fonte migliore che abbiamo su ciò che non possiamo misurare, ma è di seconda mano;
- **misura**: un risultato riproducibile sui nostri dati, con lo script, i dati e la data.
  Vale per i dati su cui è stata fatta: se i dati cambiano molto si rifà, e la voce nuova
  sostituisce la vecchia citandola.

Le verifiche sul codice («il ciclo di import non scatta a runtime») sono misure sul codice, con
file e simbolo.

## La propagazione

Un'informazione nuova non si scrive in un posto solo. Questa è la tabella che le skill seguono;
un passo che non serve si salta, ma si salta sapendolo.

| Quando… | …si aggiorna |
|---|---|
| arriva un'informazione da una fonte | il file in `fonti/` con le parole originali; i fatti in verificato; le ipotesi che tocca (confermate → VER, indebolite o rafforzate → nota); la domanda tolta da da_fare «Da chiedere a…»; l'ufficiale se cambia una scelta |
| si propone un esperimento | esperimenti (`proposto`, con domanda, metodo e criterio); le ipotesi che verifica passano a `in verifica (ESP-NNN)` quando parte |
| si conclude un esperimento | il report in `misure/`; l'esperimento `concluso` con esito; il fatto in verificato; le ipotesi confermate o smentite; i TODO chiusi o nati; l'ufficiale: «Cosa funziona» se positivo, «Strade scartate» se negativo o abbandonato, «Cosa non abbiamo capito» se inconcludente |
| il codice introduce un parametro scelto da noi | ipotesi (con dove lo usiamo nel codice) |
| lavorando sul codice nasce un dubbio | dubbi, con file e riga, **prima** di andare avanti |
| si chiude una issue | i TODO che chiude passano a «Fatto»; i dubbi che risolve a «Risolti»; l'ufficiale se cambia una scelta |
| cambia una scelta | l'ufficiale (§ «Le scelte in vigore» e registro delle modifiche); i documenti specchio (`specchi` nella configurazione) |

## Il documento ufficiale

È la risposta a «a che punto siamo?» per chi non segue il progetto tutti i giorni. Si riscrive,
non si appende: una sezione descrive lo stato di oggi, non la sua storia. La storia sta nel
registro delle modifiche in fondo e nelle fotografie in `storico/`.

Sezioni fisse, in quest'ordine (il progetto può aggiungere sottosezioni sue, per esempio il
contesto del dominio, dentro «Le scelte in vigore» o prima):

1. **L'obiettivo e l'idea**: in un paragrafo, cosa stiamo cercando di fare;
2. **Le scelte in vigore**: cosa facciamo oggi e su cosa si regge ogni scelta (VER, IP, ESP);
3. **Cosa funziona**: verificato e in uso, con le voci VER ed ESP positivi;
4. **Cosa è da testare**: le ipotesi che reggono le scelte in vigore, gli esperimenti in corso e
   proposti più importanti;
5. **Cosa manca**: i TODO P0 e P1, per fase;
6. **Cosa non abbiamo capito**: le domande aperte, gli esiti inconcludenti, i comportamenti che
   non sappiamo spiegare;
7. **Strade scartate**: ogni esperimento negativo o abbandonato e ogni ipotesi smentita, in una
   riga con il motivo e la voce che lo documenta. **È la sezione che impedisce di rifare lo
   stesso errore**;
8. **Dove potremmo sbagliare**: le ipotesi con impatto alto e i rischi che i dati non misurano;
9. **Prossimi passi**: in ordine;
10. **Registro delle modifiche**: una riga per ogni cambiamento di una scelta, con data e fonte,
    le più recenti in alto.

In testa: `**Aggiornato al GG-MM-AAAA.**`. `registri.py check` avvisa quando un registro è
cambiato dopo quella data. Quando cambia una scelta importante, prima di riscrivere si salva la
fotografia della versione vecchia in `storico/stato_progetto_<data>.md`.

## Graphify

Se il repo ha un grafo (`graphify-out/graph.json`), il grafo è il punto di partenza:

- **prima di aggiungere una voce** si cerca se esiste già o a cosa si collega:
  `graphify query "<la cosa in parole>"`, poi `graphify explain "<concetto>"`. `registri.py find
  <ID>` dice dove una voce è definita e chi la cita;
- **per citare il codice** in una voce (il campo «Dove» dei dubbi, «Dove la usiamo» delle
  ipotesi) si usano `graphify explain`/`graphify path` per trovare file e simbolo, poi si
  verifica la riga leggendo il file;
- **dopo aver scritto**: `graphify update .` se è cambiato codice (solo AST, gratis); se sono
  cambiati documenti o immagini serve l'estrazione semantica, quindi la skill graphify con
  `--update` (`/graphify . --update`). `registri.py stale` dice quali documenti il grafo non ha
  ancora visto.

L'aggiornamento del grafo fa parte del lavoro: si fa prima di chiudere, non si rimanda.

## Lo stile

- Frasi dirette, in italiano, senza enfasi. I **grassetti** solo per la frase che conta.
- **Numeri misurati, non stimati**; quando è una stima, lo si dice e si dice come.
- Date `GG-MM-AAAA`. Mai «ieri», «la settimana scorsa».
- Ogni riferimento al codice è `file:riga` o `file` + simbolo, verificato leggendo il file.
- Una voce dice anche **perché conta**: una voce senza conseguenze non serve a nessuno.
