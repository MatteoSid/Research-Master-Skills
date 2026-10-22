# Il metodo

Questo file è il regolamento comune delle skill di research-flow: lo leggono tutte prima di
scrivere. Descrive **come si tiene la conoscenza di un progetto esplorativo**, un progetto in cui
nemmeno chi ci lavora sa dove andrà a finire, e dove quello che si impara conta quanto il codice.

## Il principio

**Un esperimento fallito documentato vale quanto uno riuscito.** Il successo resta nel codice e
si va avanti. Il fallimento invece si toglie dal codice, e se nessuno lo scrive fra tre mesi
qualcuno rifarà lo stesso esperimento, o peggio lo darà per riuscito. Tutto il resto viene da qui:

- **niente si cancella.** Una voce chiusa resta con il suo stato e il motivo per cui è chiusa;
  un ID non si riusa mai. Resta la voce, non tutte le sue parole: chiudendosi si accorcia, e il
  dettaglio sta nel report, nell'issue e nella storia di git («Quanto è lunga una voce»);
- **ogni affermazione ha uno stato**: è un fatto verificato, un'ipotesi, un dubbio, un lavoro
  da fare, o il risultato di un esperimento. Nel documento ufficiale non c'è niente che non si
  ritrovi in un registro;
- **ogni fatto ha una fonte che si può ricontrollare**: chi l'ha detto e quando, oppure lo
  script, i dati e la data della misura;
- **il criterio di successo si decide prima.** Un esperimento senza un criterio scritto prima
  di guardare i risultati finisce sempre per «confermare» qualcosa.

Il test che decide se una voce è scritta bene: **chi apre il repo fra sei mesi, senza aver
assistito alla conversazione, capisce da solo cosa sappiamo, come lo sappiamo e cosa resta
aperto?** Se no, manca qualcosa: la fonte, il numero misurato, il file e il simbolo, il motivo.

## I documenti

La configurazione del progetto (`.research-flow.json` nella radice del repo) dice in che
cartella stanno e come si chiamano. Qui li chiamiamo per tipo; `dir` è la cartella, di solito
`research/`.

| Tipo | File di default | Prefisso | Cosa ci va |
|---|---|---|---|
| dubbi | `dubbi_implementazione.md` | `DUB` | dubbi sul **nostro codice** che possono cambiare un risultato o una scelta: una scelta che potrebbe essere sbagliata, un valore copiato a mano, un limite noto, un comportamento che non sappiamo se è voluto |
| ipotesi | `ipotesi_da_verificare.md` | `IP` | quello che **stiamo assumendo** e nessuno ha dimostrato, con come si verifica e l'impatto se è sbagliato |
| verificato | `verificato.md` | `VER` | quello che **sappiamo**: fatti da una fonte, misure nostre, verifiche sul codice, ognuno con la fonte |
| esperimenti | `esperimenti.md` | `ESP` | **ogni esperimento**, proposto, in corso o concluso, con il suo esito: positivo, negativo, inconcludente o abbandonato |
| da_fare | `da_fare.md` | `TODO` | tutto il lavoro che manca per arrivare all'obiettivo, per fase e priorità, e le domande aperte alle fonti |
| ufficiale | `stato_progetto.md` | — | **la versione ufficiale**, breve: l'obiettivo, le scelte in vigore, cosa abbiamo imparato, dove potremmo sbagliare, i prossimi passi |

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
| «Non abbiamo capito perché…» | ipotesi se c'è una spiegazione candidata da verificare, altrimenti un esperimento proposto se si può indagare; se pesa sulle scelte, un rischio in ufficiale § «Dove potremmo sbagliare» |
| «Da adesso facciamo così» | ufficiale § «Le scelte in vigore», con una riga nel registro delle modifiche |
| «Oggi l'esperimento in corso ha dato…», una nota a test aperto | il report dell'esperimento in `misure/`, aperto quando l'esperimento parte: **non nella voce** |
| «Questo commento è vecchio», «questo numero è superato», «qui la forma è diversa dal design» | si sistema subito, nello stesso lavoro, o va in una issue del tracker: **non nei registri** |
| un elenco di ritocchi o di difetti piccoli (pagina per pagina, file per file) | una issue del tracker, con l'elenco; nei registri al massimo un TODO di una riga che la cita |

Se una cosa ne tocca più di uno, va in tutti, e le voci si citano a vicenda per ID.

### Cosa entra nei registri, e cosa no

**Nei registri entra quello che può cambiare una decisione:** un fatto da una fonte, una misura,
un esperimento con il suo esito, un'ipotesi che regge un parametro o una scelta, un dubbio sul
codice che può cambiare un risultato, un lavoro che serve all'obiettivo. Il test: se fra un mese
qualcuno, leggendo la voce, potrebbe scegliere diversamente, la voce serve; se no, non serve.

Le cose piccole che si trovano lavorando (un commento superato, un numero vecchio in un documento,
una differenza di forma dal design, un avviso del linter) **non diventano voci**: si sistemano
subito, nello stesso lavoro, oppure vanno in una issue del tracker, che è il posto del lavoro da
fare. Un registro pieno di cose piccole nasconde quelle che contano, e ognuna costa una lettura a
ogni sessione che lo apre.

## Le voci

Ogni voce ha un **ID** `<PREFISSO>-NNN` progressivo, mai riusato: il successivo lo dà
`registri.py next <tipo>`, non si conta a mano. Le voci si citano per ID ovunque: nei registri,
nei report, nel documento ufficiale, nei commenti del codice, nelle issue.

Due forme, e ogni registro dichiara in testa la sua:

- **a intestazione** (dubbi, ipotesi, esperimenti): `### IP-012 · Il titolo in una frase`, poi i
  campi come elenco `- **Campo:** testo`. Serve quando la voce ha bisogno di spiegazione;
- **a tabella** (verificato, da_fare): una riga per voce, con l'ID nella prima colonna. Serve
  quando la voce è un fatto o un compito in una riga.

I campi obbligatori li controlla `registri.py check`. Il campo **Stato** è sempre l'ultimo. Il
controllo si lancia prima di una PR verso il branch principale che tocca i registri
(`/research-flow:controlla`), non a ogni commit né alla chiusura di ogni issue figlia.

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
  «Fatto»), le più recenti in alto, e si accorciano nella forma chiusa («Quanto è lunga una
  voce»). Un dubbio `accettato` è chiuso come uno risolto: va in «Risolti», con il motivo per cui
  lo teniamo così.

### Quanto è lunga una voce

Una voce si legge in un minuto. È la scheda che dice cosa sappiamo e dove sta il resto, non il
posto del lavoro: ogni `registri.py find`, ogni `grep` che la tocca e ogni sessione che apre il
registro se la porta dietro intera. I tetti stanno nella configurazione: `voce_parole_max` (400
di default) per le voci a intestazione, `riga_parole_max` (250) per le righe di tabella, e
`registri.py check` avvisa sopra il tetto (`voce-lunga`). Sono tetti, non obiettivi: una voce
chiusa ne usa molte meno.

Il dettaglio ha già un posto suo:

- **le note di un esperimento in corso** (misure intermedie, decisioni prese strada facendo,
  episodi) vanno nel suo report in `misure/`, che si apre quando l'esperimento parte, con
  `**Stato:** in corso` in testa e le note datate nella sezione «Diario». La voce tiene domanda,
  criterio, un metodo breve, lo stato e il link al report; se una nota cambia una decisione, la
  voce lo dice in una riga che rimanda al report;
- **la storia di un lavoro** (cosa è stato rilasciato, quando, con quale backup) sta nell'issue o
  nella PR. La cella **Stato** di un TODO dice lo stato e l'issue (`in corso (#92)`, `fatto (#99,
  02-10-2026)`), più al massimo una frase su cosa manca;
- **un elenco di cose piccole** sta in una issue («Cosa entra nei registri, e cosa no»).

**La forma chiusa.** Quando una voce si chiude si accorcia. Prima si controlla che quello che si
toglie stia nel report, nell'issue o nella PR, e se non c'è si sposta lì; poi la voce tiene solo
quello che serve a chi la ritrova fra sei mesi:

| Registro | La voce chiusa tiene |
|---|---|
| esperimenti | Domanda; Metodo in una o due frasi (dati, script, criterio) che rimandano al report; Esito: la parola e i numeri che decidono, in una o due frasi; **Cosa ne abbiamo tratto, per intero**, perché è quello che impedisce di rifare l'errore; Report; Tocca e Origine se ci sono; Stato |
| dubbi | Dove; il dubbio in una o due frasi; come si è chiuso (cosa è cambiato, con la PR o il commit, o perché lo accettiamo); Stato |
| da_fare | una riga: cosa, in una frase, e `fatto (#issue, data)` |
| ipotesi | resta com'è: la conclusione sta nel VER che la chiude |

Il registro verificato non si chiude: una voce è già un fatto in una riga, e vale il tetto delle
righe. Una voce chiusa vale per il commit della sua chiusura, e accorciandola i riferimenti non si
riallineano. Un progetto che adotta questa regola con molte voci chiuse e lunghe le accorcia una
volta per tutte, dopo aver salvato la fotografia dei registri in `storico/registri_<GG-MM-AAAA>/`.

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
`positivo` deve sempre poter finire in «Cosa abbiamo imparato».

Ogni esito `negativo`, `abbandonato` e `inconcludente`, e ogni ipotesi smentita, resta nel suo
registro, e `registri.py scartate` li elenca tutti con cosa ne abbiamo tratto: **è l'elenco che
impedisce di rifare lo stesso errore**, e non si ricopia nell'ufficiale. Nell'ufficiale un esito
negativo entra solo se conta per chi legge, e il posto dipende da cosa metteva alla prova:

- un'**alternativa** importante che stavamo valutando (un riferimento diverso, un filtro nuovo) →
  «Cosa abbiamo imparato»: non la prendiamo, e perché;
- una **scelta in vigore** (la definizione che usiamo, un parametro già in produzione) → «Dove
  potremmo sbagliare», con un TODO per rimediare. La scelta resta finché non ne abbiamo una
  migliore, ma non si presenta più come verificata.

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
| parte un esperimento lungo (giorni o settimane) | il report in `misure/` con `**Stato:** in corso`: le note di ogni giorno vanno nel suo «Diario», la voce cita il report |
| si conclude un esperimento | il report in `misure/`; l'esperimento `concluso` con esito, nella forma chiusa; il fatto in verificato; le ipotesi confermate o smentite; i TODO chiusi o nati; l'ufficiale se cambia una scelta, o se l'esito è fra le cose importanti imparate o fra i rischi («Cosa vuol dire l'esito») |
| il codice introduce un parametro scelto da noi | ipotesi (con dove lo usiamo nel codice) |
| lavorando sul codice nasce un dubbio che può cambiare un risultato o una scelta | dubbi, con file e simbolo, **prima** di andare avanti |
| si chiude una issue | i TODO che chiude passano a «Fatto» e i dubbi che risolve a «Risolti», nella forma chiusa; l'ufficiale se cambia una scelta |
| cambia una scelta | l'ufficiale (§ «Le scelte in vigore» e registro delle modifiche); i documenti specchio (`specchi` nella configurazione) |

## Il documento ufficiale

È la risposta a «a che punto siamo?» per chi non segue il progetto tutti i giorni, e **si legge in
una volta**: ha un tetto di parole (`ufficiale_parole_max` nella configurazione, 1.500 di default,
senza contare il registro delle modifiche), che `registri.py check` controlla. È un tetto, non un
obiettivo. Si riscrive, non si appende: una sezione descrive lo stato di oggi, non la sua storia.
La storia sta nel registro delle modifiche in fondo e nelle fotografie in `storico/`; il dettaglio
sta nei registri, e l'ufficiale lo cita per ID.

Sezioni fisse, in quest'ordine (il progetto può aggiungere sottosezioni sue dentro «Le scelte in
vigore», per esempio una per parte del dominio):

1. **L'obiettivo e l'idea**: in un paragrafo, cosa stiamo cercando di fare;
2. **Le scelte in vigore**: cosa facciamo oggi, con i numeri che contano, e su cosa si regge ogni
   scelta (VER, IP, ESP). Una scelta in una o due righe;
3. **Cosa abbiamo imparato**: le scoperte che hanno cambiato le scelte, quelle che hanno retto e
   le strade importanti che abbiamo scartato, una riga ciascuna con la voce che lo documenta.
   L'elenco completo delle strade scartate lo dà `registri.py scartate`;
4. **Dove potremmo sbagliare**: al massimo cinque rischi, i più gravi: le ipotesi con impatto
   alto, le scelte in vigore che un esperimento ha messo in dubbio, quello che non abbiamo capito
   e i rischi che i dati non misurano;
5. **Prossimi passi**: al massimo tre, in ordine. Il resto del lavoro è in da_fare;
6. **Registro delle modifiche**: una riga per ogni cambiamento di una scelta, con data e fonte, le
   più recenti in alto. Tiene le righe delle ultime settimane; le più vecchie restano nella
   fotografia in `storico/` da cui si è ripartiti, che la sezione cita.

Le ipotesi aperte, gli esperimenti proposti, i dubbi e il lavoro da fare non si ripetono
nell'ufficiale: li mostrano i registri e `/research-flow:overview`.

Si scrive per una persona: frasi, non celle di tabella con un paragrafo dentro; i numeri che
contano, non tutti quelli misurati.

In testa: `**Aggiornato al GG-MM-AAAA.**`. `registri.py check` avvisa quando un registro è
cambiato dopo quella data (`ufficiale-vecchio`) e quando il testo supera il tetto
(`ufficiale-lungo`).

**Le fotografie.** Quando cambia una scelta importante, prima di riscrivere si salva la versione
vecchia in `storico/stato_progetto_<GG-MM-AAAA>.md`: copiata com'è, con in testa solo un avviso
(«Fotografia del GG-MM-AAAA, non più aggiornata: la versione in vigore è `stato_progetto.md`»,
e la mappa delle sezioni se sono cambiate). I documenti in `storico/` non si aggiornano più:
i percorsi e i riferimenti vecchi lì dentro sono giusti così.

### Gli specchi

Uno specchio (una pagina dell'app, un README pubblico: `specchi` nella configurazione) ripete a
parole le scelte dell'ufficiale, ma **non riscrive i numeri a mano**: li legge dal codice o da
un'API, così non resta indietro quando un parametro cambia. Un numero scritto a mano in uno
specchio va sistemato: si legge dal codice.

## Graphify

Se il repo ha un grafo (`graphify-out/graph.json`), il grafo serve per il codice e per i
documenti che cambiano di rado (report, fonti, README). **I sei documenti conviene escluderli dal
grafo**, nel `.graphifyignore` (dal percorso del repo, per esempio `research/verificato.md`),
insieme a `storico/`:

- cambiano a ogni lavoro, e ogni estrazione semantica di un registro costa centinaia di migliaia di
  token;
- per navigarli il grafo non serve: `registri.py find <ID>` dà la definizione di una voce e tutte
  le sue citazioni, nei registri, nei report e nel codice, con file e riga, e `registri.py
  scartate` le strade scartate;
- il grafo non distingue una scelta superata da una in vigore, e cerca per parole, non per
  significato.

Per la stessa ragione **un report in corso**, con il «Diario» che cresce ogni giorno, sta in
`.graphifyignore` finché l'esperimento non si conclude: alla conclusione si toglie dall'elenco e il
report si estrae una volta.

`registri.py stale` salta i file esclusi da `.graphifyignore`. Nel lavoro sulle voci:

- **prima di aggiungere una voce** si cerca se esiste già: `registri.py find <ID>` per le voci
  nominate, `grep` con le parole dei registri (più di una, e i sinonimi), `registri.py scartate`
  se è un'idea da provare. Anche quando i registri erano nel grafo, `graphify query` trovava una
  voce descritta con altre parole circa una volta su due;
- **per citare il codice** in una voce (il campo «Dove» dei dubbi, «Dove la usiamo» delle
  ipotesi) si trovano file e simbolo con `graphify explain`, `graphify path` o `grep`, e si
  verifica leggendo il file;
- **dopo aver scritto**: `graphify update .` se è cambiato codice (solo AST, gratis).
  L'estrazione semantica (`/graphify . --update`) serve solo per i documenti che il grafo legge
  (report, fonti, README) e per le immagini, **una volta sola alla fine del lavoro**, non dopo
  ogni modifica.

Il grafo dice **cosa è collegato a cosa**, non lo stato di una voce: se un esperimento è già
stato fatto, se un'ipotesi è chiusa, lo dicono i registri (`registri.py find`, `riepilogo`,
`scartate`).

## Lo stile

- Frasi dirette, in italiano, senza enfasi. I **grassetti** solo per la frase che conta.
- **Numeri misurati, non stimati**; quando è una stima, lo si dice e si dice come.
- Date `GG-MM-AAAA`. Mai «ieri», «la settimana scorsa».
- Ogni riferimento al codice è `file` + simbolo (una funzione, una classe, una costante),
  verificato leggendo il file: **mai il numero di riga nei registri e nell'ufficiale.** Le righe
  si spostano a ogni modifica del codice, e una citazione con la riga diventa sbagliata senza che
  nessuno se ne accorga, o costa un giro di riallineamento. `registri.py check` avvisa
  (`riga-citata`) sulle voci aperte, sull'ufficiale, sul `README.md` e sul `CLAUDE.md`.
- I documenti datati fanno eccezione: un report, o una fonte che cita righe, scrive in testa il
  commit su cui ha misurato (`**Commit:** `abc1234``) e le righe che cita valgono per quel
  commit; una voce chiusa vale per il commit della sua chiusura. **Né gli uni né le altre si
  riallineano.**
- Una voce dice anche **perché conta**: una voce senza conseguenze non serve a nessuno.
