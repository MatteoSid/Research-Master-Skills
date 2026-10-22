### Documentazione esplorativa (research-flow)

La conoscenza del progetto sta in `{dir}/` e si tiene con il plugin research-flow (regolamento
completo nel METODO.md del plugin). In breve:

- sei documenti al primo livello di `{dir}/`: dubbi (`DUB-NNN`), ipotesi (`IP-NNN`), verificato
  (`VER-NNN`), esperimenti (`ESP-NNN`), da fare (`TODO-NNN`) e la versione ufficiale
  `{ufficiale}`. Tutto il resto in sottocartelle per ruolo (`fonti/`, `misure/`, `storico/`…);
- **gli esperimenti falliti si documentano come quelli riusciti**, con l'esito e cosa non rifare;
- niente si cancella: una voce chiusa resta con il suo stato, un ID non si riusa;
- **una voce è corta** (un tetto di parole): le note di un esperimento in corso vanno nel suo
  report, la storia di un lavoro nell'issue, e chiudendosi una voce si accorcia;
- **nei registri entra quello che può cambiare una decisione.** Le cose piccole trovate lavorando
  (un commento vecchio, un numero superato, una differenza di forma) si sistemano subito o vanno
  in una issue;
- il codice si cita con file e simbolo, **mai con il numero di riga**; un report dice in testa il
  commit su cui ha misurato, e le sue righe non si riallineano;
- `{ufficiale}` è breve (un tetto di parole): le scelte in vigore, cosa abbiamo imparato, dove
  potremmo sbagliare, i prossimi passi. Il dettaglio sta nei registri.

Quando usare le skill:

| Quando | Skill |
|---|---|
| arriva un'informazione esterna che tocca i registri (una risposta, un documento, una pagina, un messaggio) | `/research-flow:fonte`: se è il momento di aggiungere una fonte lo decide l'utente, o Claude dicendolo |
| si conclude una misura o un esperimento, **anche andato male** | `/research-flow:annota esito ESP-NNN` (o `annota` con la descrizione, se l'esperimento non era registrato) |
| si vuole provare qualcosa | `/research-flow:annota` (esperimento proposto, con il criterio di successo scritto prima) |
| lavorando sul codice nasce un dubbio che può cambiare un risultato, o si sceglie un parametro senza saperlo giustificare | `/research-flow:annota`, **prima** di andare avanti |
| si chiude una issue | `/research-flow:annota fatto TODO-NNN #issue`, `risolto DUB-NNN` |
| cambia una scelta, o qualcuno chiede «a che punto siamo?» | `/research-flow:stato` (`leggi` per rispondere senza scrivere) |
| prima di una PR verso il branch principale che tocca `{dir}/` (non a ogni commit) | `/research-flow:controlla` |
| si vogliono vedere i registri nel browser, con le voci complete e gli ID cliccabili | `/research-flow:overview` (`serve` per tenerla accesa e aggiornata) |
{extra}
