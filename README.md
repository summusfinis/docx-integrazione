# docx-integrazione

Strumenti per produrre un compendio in formato Word (.docx) e integrarlo con il testo di un
manuale: creazione del documento da un file Markdown, inserimento di sezioni e capoversi nelle
schede, corsivi e grassetti, ricalcolo dell'indice e dei numeri di pagina. Non serve un .docx di
partenza: il documento si può creare da zero.

## Requisiti

- Python 3.10 o successivo, nessuna dipendenza Python esterna
- `bash`, `unzip`, `zip`
- LibreOffice (`soffice`) e `pdftotext` (pacchetto poppler), per misurare le pagine

## Configurazione

| Variabile | Significato | Default |
|---|---|---|
| `DOCX_WORK` | cartella di lavoro: contiene i file di input e riceve `docx/`, `out.docx`, `pagine.json` | `./lavoro` |
| `DOCX_SOURCE` | .docx di partenza, se si vuole partire da un documento esistente | `$DOCX_WORK/sorgente.docx`, se presente |
| `DOCX_CONTENUTO` | file Markdown da cui creare il documento, se non c'è un .docx di partenza | `$DOCX_WORK/contenuto.md` |
| `DOCX_PRIMO_TITOLO` | testo che apre il primo titolo, per misurare le pagine | `Titolo I – ` |
| `DOCX_VOCAB` | dizionario dei termini da corsivizzare | `dati/vocab.txt` |
| `DOCX_SCAMBI=1` | attiva lo scambio di titoli e schede (`indice_swap.py`), solo per il caso del compendio di partenza | non attivo |
| `DOCX_NUOVE=1` | attiva l'inserimento di schede nuove da `delta/*.json` (`nuove.py`), solo per il caso del compendio di partenza | non attivo |

## Formato di `contenuto.md`

Riga per riga, sopra la prima intestazione:

    titolo_copertina: NOME DEL COMPENDIO
    sottotitolo: PARTE GENERALE

Poi il testo, con queste intestazioni:

    # Titolo I – Nome del titolo          titolo (voce d'indice)
    ## Scheda 1 – Nome della scheda       scheda (voce d'indice); il Sommario si genera da solo
    ### Nome della sezione                sezione, numerata automaticamente
    #### Nome della sottosezione          sottosezione

Le righe di testo sono capoversi (una riga vuota separa i capoversi). Inline: `**grassetto**`,
`*corsivo*`, `***grassetto corsivo***`. Il numero delle sezioni è automatico: non va scritto.

Esempio completo: `esempi/contenuto_esempio.md` (testo inventato, per prova).

## Struttura

- `bin/build.sh`: catena completa, da `contenuto.md` (o dal .docx di partenza) a `out.docx`
- `bin/crea_documento.py`: crea il pacchetto Word da `contenuto.md`: stili, copertina, indice, schede, sezioni
- `bin/misura_pagine.py`: misura le pagine di schede e titoli su `out.docx` e scrive `pagine.json`
- `bin/xmltext.py`, `bin/runs.py`, `bin/mk.py`: lettura e scrittura di paragrafi e run di `word/document.xml`
- `bin/indice_swap.py`: scambio di blocchi nell'indice e nel corpo (solo con `DOCX_SCAMBI=1`)
- `bin/corsivi.py`: corsivi sui termini del dizionario, più suffissi degli articoli (`-bis`, `-ter`, …)
- `bin/tabapply.py`: grassetti e corsivi sulle righe di elenco delle tabelle, da coppie `tab/in_N.txt`/`out_N.txt`
- `bin/integra.py`: inserisce sezioni e capoversi da `delta/*.json` nelle schede esistenti
- `bin/nuove.py`: schede nuove da `delta/*.json` (solo con `DOCX_NUOVE=1`)
- `bin/sistema.py`: rinumera le sezioni non consecutive, riallinea i sommari, porta il corpo delle schede
  a 10,5 (stile `Normale`) tenendo i titoli di sezione a 11,5
- `bin/firstpage.py`: prima pagina senza numero
- `bin/indice_pagine.py`: aggiorna i numeri dell'indice da `pagine.json`
- `bin/ocr_pagina.py`: OCR di una foto di pagine affiancate: ritaglio delle due pagine, rimozione
  delle sottolineature a penna, riconoscimento con tesseract (`-l ita`, `OMP_THREAD_LIMIT=1`)
- `bin/pulisci_ocr.py`: dai file OCR per mezza pagina al testo continuo di un intervallo, con `[p. N]`
- `bin/trascrizione.py`: come sopra, con titoli di capitolo e di paragrafo, per la trascrizione da consegnare
- `bin/mappa_pagine_ocr.py`: numero di pagina stampato e titolo corrente di ogni mezza pagina
- `bin/estrai_schede.py`: estrae il testo delle schede indicate dal `document.xml`, in markdown leggero
- `bin/indice_ripara.py`: ripara le voci d'indice in cui il numero di pagina si era attaccato al titolo
- `dati/vocab.txt`: dizionario dei corsivi, formato `conteggio | termine`
- `istruzioni/`: istruzioni per i subagenti che producono i file di input
- `esempi/`: esempio di `contenuto.md`

## Uso

Creare il documento da zero:

```bash
export DOCX_WORK=/percorso/alla/cartella/di/lavoro   # contiene contenuto.md
bash bin/build.sh                                    # produce $DOCX_WORK/out.docx
python3 -I bin/misura_pagine.py                      # scrive pagine.json
bash bin/build.sh                                    # rigenera con i numeri di pagina
```

Partire da un .docx esistente: stessi comandi, con `DOCX_SOURCE` al posto di `contenuto.md`.

Il ciclo di misura va ripetuto finché `pagine.json` non cambia. Di norma bastano due giri.

L'indice dei documenti creati da `contenuto.md` è un campo `TOC` di Word. Il file contiene già i
numeri misurati; all'apertura Word chiede di aggiornare i campi: rispondere sì. Dopo ogni modifica
al testo, basta aggiornare il campo (tasto F9 sull'indice, o clic destro → Aggiorna campo).
I documenti creati a partire da un .docx di partenza mantengono l'indice a mano.

## Istruzioni per i subagenti

Nei file in `istruzioni/`, `<LAVORO>` indica la cartella `DOCX_WORK`. Sostituirla con il percorso
reale prima di affidare il lavoro a un agente.

## Limiti noti

- Nessun test automatico. I controlli fatti finora sono script di verifica eseguiti a mano, più un
  confronto con un build di riferimento.
- Le tabelle «Mappa concettuale» non vengono generate da `contenuto.md`: il corpo è solo testo.
- I numeri di pagina iniziali sono misurati con LibreOffice; in Word si aggiornano con il campo indice.
  Non verificato su Word da questo ambiente.
- Il dizionario dei corsivi va rigenerato per ogni testo.
- Gli script non verificano la fedeltà del testo alla fonte: è compito della revisione umana.
