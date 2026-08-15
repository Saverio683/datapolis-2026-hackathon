# Casalinghe a vent'anni — il meccanismo, non solo il divario

> A Bagheria il 13.4% delle ragazze fra i 15 e i 24 anni si dichiara casalinga: 387 persone,
> contro il 4.6% nazionale. Non è un tasso di disoccupazione: è una condizione dichiarata.

## L'idea

Quasi tutte le analisi di genere si fermano al divario. Questa idea prova a spiegare
**attraverso quale canale** il divario si produce, perché è il canale a determinare quale
policy possa funzionare.

Il thread genere ha già trovato che l'inattività maschile e quella femminile a Bagheria non
sono la stessa cosa: i ragazzi inattivi finiscono in "altra condizione", le ragazze inattive
si dichiarano **casalinghe**. Sono due stati diversi, con due significati diversi rispetto al
mercato del lavoro: "altra condizione" è un residuo, "casalinga" è un ruolo — e a vent'anni è
un ruolo che di solito non è stato scelto in alternativa a un'occupazione, ma **al posto di
un'occupazione che non c'era**.

La domanda è: **cosa produce una casalinga ventenne a Bagheria e non a Palermo?**

## Perché è rilevante

È la parte dell'analisi che non si può ottenere con un indicatore preconfezionato e che
distingue un lavoro da hackathon da un cruscotto. Ed è quella che rende la proposta
progettabile: un servizio per l'inserimento lavorativo di ragazze *disoccupate* e uno per
ragazze *fuori dalle forze di lavoro* sono due servizi diversi (il secondo deve prima
riportare le persone dentro il mercato, l'altro deve solo intermediarlo).

## Cosa dicono già i dati

- 13.4% contro 1.7% dei coetanei maschi (`fig02_composizione_stato`); 4.6% il dato nazionale
  femminile. La serie 2018-2024 è **stabile**: non è un effetto pandemia.
- Il tasso di disoccupazione femminile a Bagheria poggia su 430-680 persone: è stato
  **declassato a misura non conclusiva** nel notebook. Un motivo in più per lavorare sulla
  composizione degli stati invece che sui tassi standard.
- Le ragazze si perdono dalle coorti **dopo i 25 anni**, non prima (`genere_coorti.csv`):
  la casalinga ventenne non è ancora andata via. C'è una finestra.

## Cosa bisogna sviluppare

1. **Chi sono, per età**: la condizione professionale esiste solo sulla classe `Y15-24`, ma la
   popolazione per **età singola** c'è. Incrociando le due si può almeno delimitare quanto la
   quota di casalinghe sia compatibile con le sole 20-24enni o richieda anche le più giovani.
   È un ragionamento di bounds, non una stima puntuale: va scritto come tale.
2. **Formazione precoce della famiglia**: al 2011, `F5`-`F7` di 8milaCensus danno coppie
   giovani con e senza figli e famiglie monogenitoriali (<35 anni) per tutti i 390 comuni,
   e `F4` i giovani che vivono da soli (15-34). Bagheria si posiziona in quella distribuzione:
   se la formazione familiare è precoce rispetto ai comuni comparabili, il canale ha un nome.
3. **Stato civile per età e genere (2018-2024)** — 🟡 **richiede un fetch nuovo**: nella
   tavola demografica attualmente scaricata lo stato civile è presente solo come totale
   (`ALL`). L'SDMX lo espone: è un task "nuova fonte", da pianificare e non da improvvisare.
   Se si fa, la domanda "le ventenni di Bagheria si sposano prima che altrove?" ha una
   risposta al 2024 e non solo al 2011.
4. **Confronto con i benchmark** su tutta la composizione degli stati, non solo su
   "casalinga": la figura deve mostrare che a Palermo quelle stesse persone stanno in
   "studente" o "in cerca", cioè dentro percorsi che un servizio può intercettare.

## Fattibilità

🟢 Punti 1, 2, 4 con i dati già in `data/processed/`.
🟡 Punto 3 richiede un fetch SDMX aggiuntivo (dataflow demografico con `MARITAL_STATUS`
valorizzato). Da decidere in team prima di iniziare.
🔴 Il **motivo** della condizione (cura di familiari, scoraggiamento, norma sociale) **non è
nei dati**. Se serve, va detto che è un'ipotesi da verificare con dati qualitativi o
un'indagine locale — non lo si inferisce dalla tabella. Questo limite va scritto nel
notebook, non nascosto nella proposal.

## Verso la proposal

- **Evidenza** → 387 ragazze 15-24 in una condizione che a livello nazionale riguarda un
  terzo di quella quota, stabile da sette anni; l'inattività femminile giovanile a Bagheria è
  fuori dal mercato del lavoro, non dentro la disoccupazione.
- **Intervento** → un servizio che agisce sulla soglia d'ingresso (contatto attivo, non
  sportello passivo), perché chi non si dichiara "in cerca" non si presenta a uno sportello.
- **Target** → le 387, per nome del gruppo e non per stima: è un numero che si rigenera dalla
  cella del notebook a ogni release del censimento.
- **KPI** → quota di 15-24enni femmine in condizione "casalinga": dal 13.4% verso il valore
  dei territori di confronto (il livello-obiettivo si legge da `genere_casalinghe.csv`, non
  si sceglie a mano); misurabile annualmente sulla stessa fonte, a costo zero.
