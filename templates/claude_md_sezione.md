### Documentazione esplorativa (research-flow)

La conoscenza del progetto sta in `{dir}/` e si tiene con il plugin research-flow (regolamento
completo nel METODO.md del plugin). In breve:

- sei documenti al primo livello di `{dir}/`: dubbi (`DUB-NNN`), ipotesi (`IP-NNN`), verificato
  (`VER-NNN`), esperimenti (`ESP-NNN`), da fare (`TODO-NNN`) e la versione ufficiale
  `{ufficiale}`. Tutto il resto in sottocartelle per ruolo (`fonti/`, `misure/`, `storico/`…);
- **gli esperimenti falliti si documentano come quelli riusciti**, con l'esito e cosa non rifare;
- niente si cancella: una voce chiusa resta con il suo stato, un ID non si riusa.

Quando usare le skill:

| Quando | Skill |
|---|---|
| arriva un'informazione esterna che tocca i registri (una risposta, un documento, una pagina, un messaggio) | `/research-flow:fonte`: se è il momento di aggiungere una fonte lo decide l'utente, o Claude dicendolo |
| si conclude una misura o un esperimento, **anche andato male** | `/research-flow:annota esito ESP-NNN` (o `annota` con la descrizione, se l'esperimento non era registrato) |
| si vuole provare qualcosa | `/research-flow:annota` (esperimento proposto, con il criterio di successo scritto prima) |
| lavorando sul codice nasce un dubbio, o si sceglie un parametro senza saperlo giustificare | `/research-flow:annota`, **prima** di andare avanti |
| si chiude una issue | `/research-flow:annota fatto TODO-NNN #issue`, `risolto DUB-NNN` |
| cambia una scelta, o qualcuno chiede «a che punto siamo?» | `/research-flow:stato` (`leggi` per rispondere senza scrivere) |
| prima di un commit che tocca `{dir}/` | `/research-flow:controlla` |
{extra}
