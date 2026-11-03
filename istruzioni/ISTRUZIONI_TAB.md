# Formattazione delle tabelle «Mappa concettuale»

Ogni scheda del compendio si chiude con una tabella di riepilogo: un titolo, alcune
etichette di sezione, righe di elenco che cominciano con «•» e una riga finale
«Punti chiave». Le righe di elenco sono **senza grassetti** e in parte senza i
corsivi dovuti. Vanno formattate.

## Il tuo file

Ti è stato indicato un file `<LAVORO>/tab/in_N.txt`. È fatto così:

```
#T226565
0	**titolo della tabella**
2	• Norme universali a struttura aperta, con molteplici funzioni (art. 12 Preleggi, analogia iuris)
```

`#T…` apre una tabella; poi una riga per paragrafo, con `indice<TAB>testo`.
Il testo è markdown: `**grassetto**`, `*corsivo*`, `***grassetto corsivo***`.

## Che cosa devi fare

Scrivi `<LAVORO>/tab/out_N.txt` con **le sole righe che hai modificato**,
mantenendo le righe `#T…` di apertura delle tabelle a cui appartengono e il
formato `indice<TAB>testo`. Le righe non modificate non vanno riportate.

Intervieni **solo** sulle righe che cominciano con «•»:

1. **Grassetto** su una o due parole chiave per riga: il concetto che la riga
   introduce, non la frase intera, non i riferimenti normativi. Una riga molto
   breve può restare senza grassetto se non c'è una parola chiave da isolare.
2. **Corsivo** su tutte le parole latine e inglesi (`*analogia iuris*`,
   `*a non domino*`, `*claims made*`, `*trust*`) e sui suffissi degli articoli
   (`art. 2645-*ter* c.c.`), dove manca.
3. Mai marcature annidate: `**scissione** tra *titulus* e *modus adquirendi*`,
   non `**scissione tra *titulus***`.

## Vincolo assoluto

**Non si cambia una sola parola.** Vietato riscrivere, abbreviare, correggere,
riordinare, aggiungere o togliere testo, punteggiatura, spazi o accenti. L'unica
differenza ammessa fra riga di partenza e riga di arrivo sono gli asterischi.
Il controllo è automatico: le righe che non superano il confronto vengono scartate.

Verifica da te prima di consegnare, con questo comando (deve stampare `OK`):

```bash
python3 -I - <<'EOF'
import re,io,sys
N="N"   # metti il tuo numero
def key(s): return re.sub(r'\*+','',s)
src={}
for l in io.open(f'<LAVORO>/tab/in_{N}.txt',encoding='utf-8'):
    if l.startswith('#T'): t=l.strip(); continue
    i,tx=l.rstrip('\n').split('\t',1); src[(t,i)]=tx
bad=0
for l in io.open(f'<LAVORO>/tab/out_{N}.txt',encoding='utf-8'):
    if l.startswith('#T'): t=l.strip(); continue
    i,tx=l.rstrip('\n').split('\t',1)
    if (t,i) not in src: print('ID ignoto',t,i); bad+=1
    elif key(src[(t,i)])!=key(tx): print('TESTO ALTERATO',t,i); bad+=1
print('OK' if not bad else f'{bad} righe da correggere')
EOF
```

In chat rispondi con una riga: quante tabelle e quante righe hai formattato.
