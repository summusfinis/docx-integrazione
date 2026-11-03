# docx-integrazione

Strumenti per integrare un compendio in formato Word (.docx) con il testo di un
manuale: inserimento di sezioni e capoversi nelle schede, creazione di schede nuove con
rinumerazione, corsivi e grassetti nelle tabelle di riepilogo, ricalcolo dell'indice e dei
numeri di pagina. Nati per un compendio di diritto civile; la logica dei documenti è generica,
ma molte regole di redazione e il dizionario dei corsivi sono specifici di quel testo.

## Requisiti

- Python 3.10 o successivo, nessuna dipendenza Python esterna
- `bash`, `unzip`, `zip`
- LibreOffice (`soffice`) e `pdftotext` (pacchetto poppler), per misurare le pagine

## Configurazione

| Variabile | Significato | Default |
|---|---|---|
| `DOCX_WORK` | cartella di lavoro: contiene `delta/`, `tab/`, `pagine.json`, e riceve `docx/` e `out.docx` | `./lavoro` |
| `DOCX_SOURCE` | il .docx di partenza | `$DOCX_WORK/sorgente.docx` |
| `DOCX_PRIMO_TITOLO` | testo che apre il primo titolo del corpo, per `misura_pagine.py` | `Titolo I – ` |
| `DOCX_VOCAB` | dizionario dei termini da corsivizzare | `dati/vocab.txt` |

## Struttura

- `bin/build.sh`: catena completa, dal sorgente a `out.docx`
- `bin/misura_pagine.py`: misura le pagine di schede e titoli su `out.docx` e scrive `pagine.json`
- `bin/xmltext.py`, `bin/runs.py`, `bin/mk.py`: lettura e scrittura di paragrafi e run di `word/document.xml`
- `bin/indice_swap.py`: scambio di blocchi nell'indice e nel corpo, con rinumerazione (specifico del caso di partenza)
- `bin/corsivi.py`: corsivi sui termini del dizionario, più suffissi degli articoli (`-bis`, `-ter`, …)
- `bin/tabapply.py`: grassetti e corsivi sulle righe di elenco delle tabelle di riepilogo, da coppie `in_N.txt`/`out_N.txt`
- `bin/integra.py`: inserisce sezioni e capoversi da `delta/*.json` nelle schede esistenti
- `bin/nuove.py`: crea schede nuove da `_nuove_schede` in `delta/*.json`, con rinumerazione e voce d'indice
- `bin/sistema.py`: rinumera sezioni non consecutive, riallinea i sommari, porta il corpo delle schede a 11,5
- `bin/firstpage.py`: prima pagina senza numero
- `bin/indice_pagine.py`: aggiorna i numeri dell'indice da `pagine.json`
- `dati/vocab.txt`: dizionario dei corsivi, formato `conteggio | termine`
- `istruzioni/`: istruzioni per i subagenti che producono i file di input (`delta/`, `tab/`, trascrizioni)

## Uso

```bash
export DOCX_WORK=/percorso/alla/cartella/di/lavoro
export DOCX_SOURCE=/percorso/al/sorgente.docx   # opzionale
bash bin/build.sh                               # produce $DOCX_WORK/out.docx
python3 -I bin/misura_pagine.py                 # scrive $DOCX_WORK/pagine.json
bash bin/build.sh                               # rigenera con i numeri di pagina
```

Il ciclo va ripetuto finché `pagine.json` non cambia. Con due giri, di norma, è stabile.

## Istruzioni per i subagenti

Nei file in `istruzioni/`, `<LAVORO>` indica la cartella `DOCX_WORK`. Sostituirla con il
percorso reale prima di affidare il lavoro a un agente.

## Limiti noti

- Nessun test automatico. Il repository ha un solo controllo riproducibile: rifare il build da
  un sorgente e confrontare `docx/word/document.xml` con un build di riferimento.
- I numeri di pagina sono misurati con LibreOffice. Word può scostarsi di una pagina su qualche voce.
- `indice_swap.py` scambia due titoli e due schede numerate in modo fisso: va riscritto per un altro documento.
- Le regole di redazione (corsivi, misure, grassetti) e il dizionario sono di un compendio di diritto civile.
- Gli script non verificano la fedeltà del testo inserito alla fonte: è compito della revisione umana.
