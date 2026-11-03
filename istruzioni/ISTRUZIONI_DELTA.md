# Integrazione di un gruppo di schede con il manuale

Il tuo materiale è **tutto** in un solo file, indicato nel messaggio: `<LAVORO>/estratti/gN.md`.
Leggilo una volta sola, per intero, e non aprire nessun altro file.

- **Parte A**: il testo attuale delle schede del compendio (titoli `## Scheda NN`, sezioni
  numerate `### N.`, un capoverso iniziale «Sommario: 1. … – 2. …», e in chiusura la
  tabella di riepilogo).
- **Parte B**: i paragrafi del manuale (trascrizione fedele; `[p. NNNN]` per pagina,
  `## N.N` per i titoli, `> nota N:` per le note).

## Che cosa produrre

Per ciascuna scheda del gruppo: individua **ciò che il manuale ha e la scheda non ha**
(istituti, distinzioni, orientamenti, sentenze, argomenti di dottrina) e collocalo:

- materia nuova e autonoma → **sezione numerata** in coda alla scheda (`append_sections`);
- completamento di un discorso già avviato → **capoversi** dopo un capoverso esistente
  (`inline_inserts`).

Non riscrivere e non parafrasare quello che la scheda già dice. Quantità attesa, se la
materia c'è: 1-4 sezioni per scheda (ciascuna 3-6 capoversi di 90-160 parole) e/o 2-8
capoversi inline. Se per una scheda il manuale non aggiunge nulla, liste vuote.

Se il manuale tratta materia che non ha **nessuna** scheda corrispondente né simile nel
gruppo, proponila in `_nuove_schede` (soglia alta: solo un argomento mai trattato).

## Formato del file di uscita (JSON, UTF-8)

```json
{"Scheda72": {"append_sections": [{"title":"…","paras":["…","…"]}],
              "inline_inserts": [{"after_anchor":"…","paras":["…"]}]},
 "Scheda73": {"append_sections": [], "inline_inserts": []},
 "_nuove_schede": [{"title":"…","dopo_scheda":91,"sections":[{"title":"…","paras":["…"]}]}]}
```

Una chiave `SchedaNN` per **ogni** scheda del gruppo, anche vuota.

### `after_anchor`

È il punto di aggancio: i capoversi entrano subito dopo il capoverso che la contiene.
Copiala **verbatim** dalla Parte A, dalla **fine** del capoverso dopo cui inserire,
lunga 50-90 caratteri, **senza** alcun carattere di markdown al suo interno (`*`, `[`,
`]`, `^`, `#`, `>`, `|`, `_`) e senza `--` né `–`: un tratto di testo piano, non in
grassetto e non in corsivo. Deve essere **unica**: scegli un tratto con un dato concreto
(numero di sentenza, articolo, termine tecnico raro), non una formula ricorrente. Se non
trovi un tratto adatto, metti quella materia in una sezione nuova invece che inline.

## Regole di redazione

Materiale di studio per il concorso in magistratura: denso, tecnico, senza riempitivi.

- Abbreviazioni ammesse: `art.`, `artt.`, `l. n. 24/2017`, `d.lgs. n. 206/2005`, `Cost.`,
  `Corte cost.`, `C.G.U.E.`, `Corte EDU`, `Cass.`, `Sez. Un.`.
- **Corsivo** per le parole latine e inglesi (`*ex lege*`, `*contra ius*`,
  `*punitive damages*`), per i suffissi degli articoli (`art. 2645-*ter* c.c.`) e per il
  testo fra virgolette «» (`«*morte naturale dell'obbligazione*»`).
- **Mai marcature annidate**: `**garanzia** ***ex lege***`, non `**garanzia *ex lege***`.
- Importi «euro 1.000»; percentuali «60%». Niente trattini lunghi: solo `–`, con parsimonia.
- Due o tre **grassetti** per capoverso, sulle parole chiave, non su frasi intere.
- Fedeltà assoluta ai dati del manuale (numeri di sentenza, anni, articoli, cifre). Se il
  manuale non dà un dato, non scriverlo. Non citare il manuale né le sue pagine.
- Contrasti giurisprudenziali o dottrinali: le tesi contrapposte in un capoverso, la
  soluzione (Sezioni unite, dottrina maggioritaria) nel capoverso immediatamente dopo.

## Prima di consegnare

Verifica che il JSON sia valido e che ogni `after_anchor` compaia una volta sola nella
Parte A del tuo file. In chat rispondi con **una riga per scheda**: quante sezioni e
quanti inline. Niente testo dei capoversi in chat.
