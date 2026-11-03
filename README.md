# docx-integrazione

Strumenti per integrare un compendio in formato Word (.docx) con il testo di un
manuale: inserimento di sezioni e capoversi nelle schede, creazione di schede nuove
con rinumerazione, formattazione di corsivi e tabelle di riepilogo, ricalcolo
dell'indice e del numero di pagina. Scritti per un compendio di diritto civile,
ma la logica dei documenti è generica.

## Requisiti

- Python 3.10 o successivo, nessuna dipendenza esterna
- `unzip`, `zip`
- LibreOffice (`soffice`) per il ricalcolo dei numeri di pagina dell'indice

## Struttura

- `bin/build.sh`: esegue la catena completa partendo dal .docx originale
- `bin/xmltext.py`, `bin/runs.py`, `bin/mk.py`: lettura e scrittura dei paragrafi e dei run di `word/document.xml`
- `bin/indice_swap.py`: scambio di blocchi nell'indice e nel corpo, con rinumerazione
- `bin/corsivi.py`: corsivi su termini da un dizionario, più suffissi degli articoli (`-bis`, `-ter`, …)
- `bin/tabapply.py`: grassetti sulle parole chiave delle tabelle di riepilogo, applicati da file di input/output
- `bin/integra.py`: inserimento di sezioni e capoversi (`delta/*.json`) nelle schede esistenti
- `bin/nuove.py`: creazione di schede nuove con rinumerazione e voce d'indice
- `bin/sistema.py`: sezioni non consecutive, sommari disallineati, dimensione uniforme del corpo
- `bin/firstpage.py`: prima pagina senza numero
- `bin/indice_pagine.py`: numeri di pagina dell'indice da `pagine.json`
- `istruzioni/`: istruzioni per i subagenti che producono i file di input (integrazione schede, tabelle, trascrizione)

## Percorsi da configurare

Gli script oggi usano percorsi fissi, da sostituire prima dell'uso:

- `/home/user/src/pg.docx`: il .docx di partenza (in `bin/build.sh`)
- `/home/user/work/`: cartella di lavoro con `delta/`, `tab/`, `bin/` e `vocab.txt`
- `/home/user/work/vocab.txt` in `bin/corsivi.py`: dizionario dei termini da corsivizzare
  (formato `conteggio | termine`), da ricavare dai corsivi già presenti nel documento

## Ordine di esecuzione

`bash bin/build.sh` esegue, nell'ordine:

1. `indice_swap.py`: scambi di blocchi
2. `corsivi.py`
3. `tabapply.py`
4. `integra.py`
5. `nuove.py`
6. `sistema.py`
7. `corsivi.py` (seconda passata)
8. `firstpage.py`, `indice_pagine.py`
9. ricostruzione di `out.docx`

`indice_swap.py` e lo scambio di blocchi sono specifici di un caso: vanno riscritti
per un altro documento.

## Limiti noti

- Nessun test automatico: i controlli di qualità sono script di verifica eseguiti a mano.
- I numeri di pagina sono calcolati con LibreOffice; Word può scostarsi di una pagina.
- Il dizionario dei corsivi va rigenerato per ogni testo.
- Gli script non controllano la fedeltà del testo inserito rispetto alla fonte: è compito
  delle istruzioni per i subagenti e della revisione umana.
