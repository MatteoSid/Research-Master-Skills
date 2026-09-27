### Documentazione esplorativa (research-flow)

La conoscenza del progetto sta in `{dir}/` e si tiene con il plugin research-flow, che ha il
regolamento completo nel suo `METODO.md`. In breve:

- sei documenti al primo livello di `{dir}/`: dubbi (`DUB-NNN`), ipotesi (`IP-NNN`), verificato
  (`VER-NNN`), esperimenti (`ESP-NNN`), da fare (`TODO-NNN`) e la versione ufficiale
  `{ufficiale}`. Tutto il resto in sottocartelle per ruolo (`fonti/`, `misure/`, `storico/`…);
- **gli esperimenti falliti si documentano come quelli riusciti**, con l'esito e cosa non rifare;
- niente si cancella: una voce chiusa resta con il suo stato, un ID non si riusa;
- `/research-flow:annota` per aggiungere o chiudere una voce, `/research-flow:fonte` per
  un'informazione nuova da una fonte, `/research-flow:stato` per riscrivere la versione
  ufficiale, `/research-flow:controlla` prima di un commit che tocca `{dir}/`.
{extra}
