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
| `fonti/` | le informazioni che arrivano da fuori (persone, documenti, documentazione, articoli, pagine web, messaggi): un file per fonte e per data, con il testo originale, e l'indice delle fonti `fonti/README.md` |
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
| «Una persona, un documento, una pagina dice che…» | il testo in `fonti/`; il fatto in verificato (fonte esterna), o un'ipotesi se la fonte è poco affidabile |
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

### Cosa vuol dire l'esito

**La domanda di un esperimento si scrive come l'idea che mettiamo alla prova, in modo che «sì»
voglia dire «l'idea regge».** Così l'esito si legge senza rileggere la domanda:

| Esito | Vuol dire |
|---|---|
| `positivo` | sì: l'idea regge, con i numeri che lo mostrano |
| `negativo` | no: l'idea non regge. È un risultato, non un fallimento dell'esperimento |
| `inconcludente` | i dati non bastano per rispondere, o la risposta cambia con dettagli di metodo |
| `abbandonato` | interrotto prima di rispondere; il motivo è obbligatorio (ha risposto una fonte, i dati non esistono, non serve più) |

Un esperimento che cerca un **problema** si scrive dalla parte della scelta che rischia: non «il
timeout interrompe operazioni che sarebbero andate a buon fine?» (dove «sì» è una cattiva
notizia), ma «il timeout interrompe solo operazioni che sarebbero fallite comunque?». Un
`positivo` deve sempre poter finire in «Cosa funziona».

Dove finisce un esito `negativo` nel documento ufficiale dipende da cosa metteva alla prova:

- un'**alternativa** che stavamo valutando (un riferimento diverso, un filtro nuovo) → «Strade
  scartate»: non la prendiamo;
- una **scelta in vigore** (la definizione che usiamo, un parametro già in produzione) → «Dove
  potremmo sbagliare» o «Cosa non abbiamo capito», con un TODO per rimediare. La scelta resta
  finché non ne abbiamo una migliore, ma non si presenta più come verificata.

### Esperimenti ricostruiti

Quando si adotta il metodo su un progetto già avviato, gli esperimenti fatti prima si
ricostruiscono dai report, dalle voci verificate e dalla storia di git. Valgono le stesse regole,
con tre accortezze:

- l'**esito si decide dal report**, mai a memoria; se il report non basta per decidere, è
  `inconcludente`;
- il criterio quasi sempre non c'è: la voce lo dice, nel Metodo («Nessun criterio scritto prima»),
  invece di inventarne uno che i risultati confermano per costruzione;
- il **Report** è il report in `misure/` se c'è; per le misure che non ne hanno uno (una tabella
  in una fonte, un numero nel `README.md`, uno script di test) è il posto dove sta il risultato,
  detto esplicitamente: «nessun report in `misure/`: la misura è in …».

Il campo facoltativo **Origine** dice da dove viene l'esperimento quando aveva un altro nome («era
E7 in `brainstorm/esperimenti.md`», «TODO-042»): chi arriva dal nome vecchio trova il nuovo.

### Due livelli di fiducia

Nel registro verificato si tengono distinti:

- **fonte esterna**: un fatto che viene da una fonte (con il nome della fonte, la data e il codice
  dell'informazione). È quello che abbiamo su ciò che non possiamo misurare, e vale quanto
  l'affidabilità della fonte: una fonte poco affidabile non produce fatti, ma ipotesi;
- **misura**: un risultato riproducibile sui nostri dati, con lo script, i dati e la data.
  Vale per i dati su cui è stata fatta: se i dati cambiano molto si rifà, e la voce nuova
  sostituisce la vecchia citandola.

Le verifiche sul codice («il ciclo di import non scatta a runtime») sono misure sul codice, con
file e simbolo.

### Le fonti

Una fonte è **qualunque informazione che non abbiamo prodotto noi**: una persona che risponde o
racconta, un documento, una documentazione tecnica, un articolo, una pagina web, un messaggio, uno
screenshot, un dataset di terzi. Non esiste un elenco di fonti deciso all'inizio del progetto: le
fonti si aggiungono quando arrivano.

**Chi decide.** Una fonte si aggiunge quando lo decide l'utente, o quando lo decide Claude di sua
iniziativa. In questo caso Claude lo dice, con il motivo; nel dubbio chiede. Si registra
un'informazione che viene da fuori, tocca i registri (un'ipotesi, una domanda aperta, un fatto,
una scelta) e si può ricontrollare (c'è il testo, il documento o il link, e una data). Il
dettaglio è nella skill `fonte`.

**L'indice.** `fonti/README.md` ha una riga per fonte: che cos'è, perché ne sa qualcosa,
l'**affidabilità** (alta, media, bassa, con il motivo), i file, e chi l'ha aggiunta e quando.
L'affidabilità decide dove finisce quello che la fonte dice: in verificato come fatto, o fra le
ipotesi. Una fonte non si cancella: se si rivela inaffidabile, la riga lo dice, e i fatti che
reggeva tornano ipotesi.

## La propagazione

Un'informazione nuova non si scrive in un posto solo. Questa è la tabella che le skill seguono;
un passo che non serve si salta, ma si salta sapendolo.

| Quando… | …si aggiorna |
|---|---|
| arriva un'informazione da una fonte | se la fonte è nuova, la sua riga nell'indice `fonti/README.md`; il file in `fonti/` con il testo originale; i fatti in verificato; le ipotesi che tocca (confermate → VER, indebolite o rafforzate → nota); la domanda tolta da da_fare «Da chiedere a…»; l'ufficiale se cambia una scelta |
| si propone un esperimento | esperimenti (`proposto`, con domanda, metodo e criterio); le ipotesi che verifica passano a `in verifica (ESP-NNN)` quando parte |
| si conclude un esperimento | il report in `misure/`; l'esperimento `concluso` con esito; il fatto in verificato; le ipotesi confermate o smentite; i TODO chiusi o nati; l'ufficiale: «Cosa funziona» se positivo; se negativo «Strade scartate» (un'alternativa) o «Dove potremmo sbagliare» (una scelta in vigore); «Strade scartate» se abbandonato; «Cosa non abbiamo capito» se inconcludente |
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
7. **Strade scartate**: ogni alternativa che un esperimento ha bocciato o abbandonato e ogni
   ipotesi smentita, in una riga con il motivo, la voce che lo documenta e a quali condizioni si
   riprova. **È la sezione che impedisce di rifare lo stesso errore**;
8. **Dove potremmo sbagliare**: le ipotesi con impatto alto, le scelte in vigore che un
   esperimento ha messo in dubbio, i rischi che i dati non misurano;
9. **Prossimi passi**: in ordine;
10. **Registro delle modifiche**: una riga per ogni cambiamento di una scelta, con data e fonte,
    le più recenti in alto.

In testa: `**Aggiornato al GG-MM-AAAA.**`. `registri.py check` avvisa quando un registro è
cambiato dopo quella data, e quando un esperimento negativo, abbandonato o inconcludente, o
un'ipotesi smentita, non compare nell'ufficiale.

**Le fotografie.** Quando cambia una scelta importante, prima di riscrivere si salva la versione
vecchia in `storico/stato_progetto_<GG-MM-AAAA>.md`: copiata com'è, con in testa solo un avviso
(«Fotografia del GG-MM-AAAA, non più aggiornata: la versione in vigore è `stato_progetto.md`»,
e la mappa delle sezioni se sono cambiate). I documenti in `storico/` non si aggiornano più:
i percorsi e i riferimenti vecchi lì dentro sono giusti così.

## Graphify

Se il repo ha un grafo (`graphify-out/graph.json`), il grafo collega le voci ai report, agli
script e al codice. Fra una voce e l'altra si naviga meglio con `registri.py`:

- **prima di aggiungere una voce** si cerca se esiste già o a cosa si collega:
  `registri.py find <ID>` per le voci nominate (definizione e tutte le citazioni, con la riga),
  `grep` con le parole dei registri, poi `graphify query "<la cosa in parole>"` come aggiunta.
  `graphify query` cerca per parole, non per significato: una voce descritta con altre parole
  spesso non la trova. `graphify explain "<ID o simbolo>"` porta dalla voce trovata ai report e
  al codice collegati;
- **per citare il codice** in una voce (il campo «Dove» dei dubbi, «Dove la usiamo» delle
  ipotesi) si usano `graphify explain`/`graphify path` per trovare file e simbolo, poi si
  verifica la riga leggendo il file;
- **dopo aver scritto**: `graphify update .` se è cambiato codice (solo AST, gratis); se sono
  cambiati documenti o immagini serve l'estrazione semantica, quindi la skill graphify con
  `--update` (`/graphify . --update`). `registri.py stale` dice quali documenti il grafo non ha
  ancora visto;
- **le fotografie in `storico/` conviene escluderle dal grafo** con `storico/` (dal percorso del
  repo, per esempio `research/storico/`) nel `.graphifyignore`: il grafo non distingue una
  scelta superata da una in vigore, e ogni fotografia nuova costerebbe un'estrazione semantica.
  `registri.py stale` salta i file esclusi da `.graphifyignore`.

Il grafo dice **cosa è collegato a cosa**, non lo stato di una voce: se un esperimento è già
stato fatto, se un'ipotesi è chiusa, lo dicono i registri (`registri.py find` e `riepilogo`).

L'aggiornamento del grafo fa parte del lavoro: si fa prima di chiudere, non si rimanda.

## Lo stile

- Frasi dirette, in italiano, senza enfasi. I **grassetti** solo per la frase che conta.
- **Numeri misurati, non stimati**; quando è una stima, lo si dice e si dice come.
- Date `GG-MM-AAAA`. Mai «ieri», «la settimana scorsa».
- Ogni riferimento al codice è `file:riga` o `file` + simbolo, verificato leggendo il file.
- Una voce dice anche **perché conta**: una voce senza conseguenze non serve a nessuno.
