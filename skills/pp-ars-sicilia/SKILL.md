---
name: pp-ars-sicilia
description: "L'unica CLI per il portale dell'Assemblea Regionale Siciliana: cerca Trigger phrases: `ars sicilia`, `assemblea regionale siciliana`, `disegni di legge sicilia`, `interrogazioni ars`, `mozioni siciliane`, `resoconti aula sicilia`, `use ars-sicilia`, `run ars-sicilia`."
author: "aborruso"
license: "Apache-2.0"
argument-hint: "<command> [args] | install cli|mcp"
allowed-tools: "Read Bash"
metadata:
  openclaw:
    requires:
      bins:
        - ars-sicilia-pp-cli
---
<!-- GENERATED FILE — DO NOT EDIT.
     This file is a verbatim mirror of library/other/ars-sicilia/SKILL.md,
     regenerated post-merge by tools/generate-skills/. Hand-edits here are
     silently overwritten on the next regen. Edit the library/ source instead.
     See the repository agent guide, section "Generated artifacts: registry.json, cli-skills/". -->

# ARS Sicilia — Printing Press CLI

## Prerequisites: Install the CLI

This skill drives the `ars-sicilia-pp-cli` binary. **You must verify the CLI is installed before invoking any command from this skill.** If it is missing, install it first:

1. Install via the Printing Press installer:
   ```bash
   npx -y @mvanhorn/printing-press-library install ars-sicilia --cli-only
   ```
2. Verify: `ars-sicilia-pp-cli --version`
3. Ensure `$GOPATH/bin` (or `$HOME/go/bin`) is on `$PATH`.

If the `npx` install fails (no Node, offline, etc.), fall back to a direct Go install (requires Go 1.26.5 or newer):

```bash
go install github.com/mvanhorn/printing-press-library/library/other/ars-sicilia/cmd/ars-sicilia-pp-cli@latest
```

If `--version` reports "command not found" after install, the install step did not put the binary on `$PATH`. Do not proceed with skill commands until verification succeeds.

Sostituisce le 12 maschere JSP del portale ufficiale con una CLI agent-native. Sync in SQLite locale per query SQL, ricerca full-text cross-archivio, e novel commands come `ddl iter` (timeline completa di un disegno di legge) e `deputato profilo` (tutta l'attività di un parlamentare in un'unica chiamata).

## When to Use This CLI

Usa ars-sicilia-pp-cli quando devi cercare, scaricare o aggregare atti dell'Assemblea Regionale Siciliana (leggi regionali, disegni di legge, interrogazioni, mozioni, resoconti d'aula, lavori di commissione) e quando hai bisogno di output strutturato JSON/CSV per pipeline downstream o per assistenti AI via MCP. Particolarmente utile per giornalismo politico, ricerca civica, civic-hacking opendata, e analisi cross-archivio impossibili dal portale JSP nativo.

## When Not to Use This CLI

Do not activate this CLI for requests that require creating, updating, deleting, publishing, commenting, upvoting, inviting, ordering, sending messages, booking, purchasing, or changing remote state. This printed CLI exposes read-only commands for inspection, export, sync, and analysis.

## Unique Capabilities

These capabilities aren't available in any other tool for this API.

### Vista cronologica cross-archivio
- **`ddl iter`** — Ricostruisce la cronologia completa di un disegno di legge: presentazione, passaggio in commissione, lavori d'aula, eventuale promulgazione come legge regionale.

  _Quando un agente deve raccontare 'a che punto sta il DDL X', questa è l'unica chiamata che restituisce la timeline completa senza incollare 5 ricerche manuali._

  Gli eventi portano **`seduta`** e, per le sedute d'Aula, un **`url`** che punta alla scheda del resoconto (la scheda dell'atto è nel campo `url` della radice). Usali sempre quando parti da una notizia: la data dell'articolo è quasi sempre il giorno **dopo** la seduta, e confonderle fa concludere che manchi un resoconto che invece c'è.

  Se due eventi d'Aula danno alla **stessa data** numeri di seduta diversi, il link viene omesso su entrambi e un hint lo dice: l'Aula tiene una seduta al giorno, quindi almeno un numero è sbagliato nella fonte (`ddl iter 17 199` dà il voto del 19 feb 2020 in «Seduta n. 179», ma la 179 è del 26 febbraio). In quel caso la chiave affidabile è la data: `resoconti cerca --legisl 17 --data 2020-02-19`.

  ```bash
  ars-sicilia-pp-cli ddl iter 18 1153 --json
  ars-sicilia-pp-cli ddl iter 17 290 --json --select data,fase,seduta,url
  ```
- **`ddl stralci`** — Elenca i disegni di legge ricavati per stralcio da un ddl base; il verso opposto è il campo `stralcio` di `ddl get` e `ddl iter`.

  _La finanziaria viene spacchettata in stralci che proseguono da soli, e la loro numerazione non segue una regola: gli stralci del ddl 1030 sono 3030…8030, quelli del 738 sono una ventina fra 7381 e 73864. Il legame lo dichiara il portale, non si calcola._

  ```bash
  ars-sicilia-pp-cli ddl stralci 18 1030 --json
  ```

  Nell'output, `base_dichiarata: false` con `di: []` significa che il documento **è** uno stralcio ma il portale non dice di quale ddl (succede su parte della XVII legislatura, dove al posto del numero base è scritto l'id interno). Non dedurre la base dalla numerazione. Uno stralcio può inoltre nascere da più ddl abbinati: `di` ha allora più voci.
- **`deputato profilo`** — Aggrega in un'unica vista tutti gli atti firmati o pronunciati da un deputato: DDL, interrogazioni, interpellanze, mozioni, ordini del giorno, risoluzioni e interventi in resoconti d'aula. `--data` (range `YYYY-MM-DD:YYYY-MM-DD`) filtra per data su tutti i sotto-archivi.

  _Sostituisce un workflow di 7 click manuali con un'unica chiamata strutturata: pensata per agenti che rispondono a 'che ha fatto il deputato X?'._

  ```bash
  ars-sicilia-pp-cli deputato profilo "Abbate Ignazio" --legisl 18 --json --select tipo,data,titolo
  ```
- **`commissione dossier`** — Vista completa su una commissione: convocazioni in calendario, sommari lavori, DDL assegnati e pareri richiesti al Governo regionale. Accetta il codice `1`-`6`, l'ordinale (`PRIMA`..`SESTA`) o un frammento della denominazione d'archivio. Le **commissioni speciali** (Antimafia, Statuto, Unione Europea) non hanno un codice e si raggiungono solo per denominazione, che non coincide con l'etichetta d'uso corrente: `"Antimafia"` non corrisponde a nulla, la denominazione è *«Commissione d'inchiesta e vigilanza sul fenomeno della mafia e della corruzione in Sicilia»*. Un termine che non aggancia nessuna commissione non produce un dossier vuoto: l'errore elenca le denominazioni della legislatura.

  _Quando segui i lavori di una commissione specifica, questa è l'unica chiamata che dà il quadro completo invece di 3 ricerche separate._

  ```bash
  ars-sicilia-pp-cli commissione dossier "SESTA" --legisl 18 --json
  ars-sicilia-pp-cli commissione dossier "inchiesta e vigilanza" --legisl 18 --json
  ```
- **`legge cronologia`** — Partendo da una legge regionale promulgata (archivio 201), risale al DDL originario, agli emendamenti citati nei resoconti d'aula e ai pareri di commissione: l'inverso temporale di ddl iter. Aggiungi sempre **`--anno`**: lo stesso numero di legge si ripete in anni diversi della stessa legislatura (nella XVIII ci sono due L.R. 26, ottobre 2024 e giugno 2025) e senza `--anno` l'archivio ne restituisce una sola — la cronologia esce coerente e riferita all'atto sbagliato. Un avviso su stderr dice quale legge è stata presa.

  _Per ricercatori e giornalisti che partono dalla legge promulgata e vogliono raccontare come ci si è arrivati._

  ```bash
  ars-sicilia-pp-cli legge cronologia 18 26 --anno 2025 --json
  ```

### Analytics su campi strutturati
- **`analytics`** — Identifica i deputati che firmano insieme atti parlamentari, restituendo coppie e cluster con conteggio per analisi di network politico. Richiede una **deep sync** dei ddl (`sync --resources ddl --deep`), che estrae i firmatari dalle schede di dettaglio.

  _Per ricercatori e giornalisti che analizzano alleanze e dinamiche politiche: niente foglio Excel di trascrizioni manuali._

  ```bash
  ars-sicilia-pp-cli sync --resources ddl --legisl 18 --deep
  ars-sicilia-pp-cli analytics --type ddl --group-by cofirmatari --limit 50 --json
  ```
- **`analytics`** — Classifica i deputati per numero di interventi nei resoconti d'aula, con range date e legislatura, opzionale conteggio parole.

  _Per le persone che vogliono sapere 'chi parla di più' senza scaricare 200 resoconti PDF e fare ctrl+F._

  ```bash
  ars-sicilia-pp-cli analytics --type resoconti --group-by oratore --legisl 18 --limit 30 --csv
  ```
- **`analytics`** — Classifica i disegni di legge per deputato **proponente** (primo firmatario) o per **gruppo** parlamentare, leggendo le viste già aggregate dal portale con **una sola richiesta** (nessuna sync). Copre la legislatura corrente (le classifiche non sono filtrabili per legislatura).

  _Per rispondere subito a 'chi presenta più DDL' / 'quale gruppo è più prolifico' senza deep sync._

  ```bash
  ars-sicilia-pp-cli analytics --type ddl --group-by proponente --limit 20
  ars-sicilia-pp-cli analytics --type ddl --group-by gruppo --json
  ```

### Stato e monitoraggio
- **`ddl drift`** — Confronta lo stato dell'iter dei DDL nella sync corrente con la precedente e segnala i disegni di legge che si sono mossi nel periodo (passati da commissione ad aula, approvati, ritirati). Richiede due **deep sync** (`sync --resources ddl --deep`) a distanza di tempo: solo la deep sync scrive il campo `iter` confrontato.

  _L'RSS shell esistente segnala solo 'nuovi'; per 'mossi' non c'è alternativa. Questo è il segnale che cercavano i journalist che seguono iter politici._

  ```bash
  ars-sicilia-pp-cli ddl drift --since 7d --json
  ```
- **`sync stale`** — Mostra per ognuno dei 12 archivi ARS: timestamp ultima sync, n. record locali, età della sync, eventuale segnalazione di staleness.

  _Per agenti che orchestrano sync automatico: decide se rinfrescare prima di rispondere o se i dati locali sono ancora freschi._

  ```bash
  ars-sicilia-pp-cli sync stale --json
  ```

  Nota: `sync stale --max-age` ha default `7d` (i dati ARS non cambiano su base oraria); `doctor`'s cache section usa invece una soglia fissa di 6h, non configurabile. Le due soglie divergono di proposito — uno store che `sync stale` giudica fresco può risultare `"status": "stale"` in `doctor`. Un agente che orchestra sync automatico non deve fidarsi solo di `sync stale`: controlla anche `doctor`'s `cache.status` se vuoi il segnale più conservativo.

## Command Reference

**biblioteca** — Catalogo Bibliografico (archivio 205) e Opere Multimediali (205multimedia).

- `ars-sicilia-pp-cli biblioteca cerca` — Cerca nel catalogo bibliografico per autore, titolo, soggetto o ISBN.
- `ars-sicilia-pp-cli biblioteca multimediali` — Cerca nelle opere multimediali.

**commissioni** — Lavori delle Commissioni: convocazioni (229) e sommari (230).

- `ars-sicilia-pp-cli commissioni convocazioni` — Convocazioni delle Commissioni.
- `ars-sicilia-pp-cli commissioni sommari` — Sommari dei lavori di commissione.

`--commissione` accetta l'ordinale (`PRIMA`..`SESTA`), un frammento della denominazione (`Bilancio`) o, in alternativa, `--codcom 1`-`6`. Un termine che non corrisponde a nessuna commissione **esce con errore** e propone i nomi vicini: non restituisce una lista vuota, che si leggerebbe come "questa commissione non ha lavori".

**ddl** — Disegni di Legge (archivio 221): proposte di legge presentate all'ARS.

- `ars-sicilia-pp-cli ddl cerca` — Cerca disegni di legge per legislatura, anno, firmatario, materia o testo.
- `ars-sicilia-pp-cli ddl get` — Scarica un singolo disegno di legge.

**interpellanze** — Interpellanze parlamentari (archivio 234).

- `ars-sicilia-pp-cli interpellanze cerca` — Cerca interpellanze.
- `ars-sicilia-pp-cli interpellanze get` — Scarica una singola interpellanza.

**interrogazioni** — Interrogazioni parlamentari (archivio 233).

- `ars-sicilia-pp-cli interrogazioni cerca` — Cerca interrogazioni per legislatura, firmatario o rubrica.
- `ars-sicilia-pp-cli interrogazioni get` — Scarica una singola interrogazione.

**leggi** — Leggi della Regione Siciliana (archivio 201): testo storico delle leggi regionali.

- `ars-sicilia-pp-cli leggi cerca` — Cerca leggi regionali per legislatura, anno, numero o testo. Restituisce **una riga per legge**, non per articolo: l'archivio è indicizzato per articolo e senza aggregazione il `--limit` lo consumavano gli articoli della prima legge (alla domanda «quali leggi nel 2025?» rispondeva con una sola legge). `articoli_trovati` conta gli articoli agganciati **da questa ricerca**, non quelli della legge. Con `--articoli` tornano le righe per articolo: servono con `--testo`, per sapere in quale articolo ricorre il termine. La paginazione si ferma sulle **leggi** chieste, non su un budget di righe stimato prima: le leggi lunghe (finanziarie, ~25 articoli) costano più richieste, le corte meno. Resta un tetto di sicurezza sulle righe lette; se scatta prima di completare le leggi chieste, un avviso su stderr lo dice — **leggilo**, altrimenti un elenco corto sembra completo.
- `ars-sicilia-pp-cli leggi get` — Scarica una singola legge regionale.

**mozioni** — Mozioni parlamentari (archivio 235).

- `ars-sicilia-pp-cli mozioni cerca` — Cerca mozioni.
- `ars-sicilia-pp-cli mozioni get` — Scarica una singola mozione.

**odg** — Ordini del Giorno (archivio 236).

- `ars-sicilia-pp-cli odg cerca` — Cerca ordini del giorno.
- `ars-sicilia-pp-cli odg get` — Scarica un singolo ordine del giorno.

**pareri** — Pareri richiesti dal Governo regionale alle Commissioni (archivio 226).

- `ars-sicilia-pp-cli pareri cerca` — Cerca pareri richiesti dal Governo.
- `ars-sicilia-pp-cli pareri get` — Scarica un singolo parere.

**resoconti** — Resoconti delle Sedute d'Aula (archivio 217).

- `ars-sicilia-pp-cli resoconti cerca` — Cerca resoconti per data, oratore o argomento. `--oratore` risolve il nome sull'anagrafica del portale: se non corrisponde a nessuna voce **esce con errore e propone i nomi vicini**, invece di restituire una lista vuota che si leggerebbe come "non è mai intervenuto". Usa il solo cognome se il nome completo non aggancia.
- `ars-sicilia-pp-cli resoconti get` — Scarica un singolo resoconto. **Non restituisce la trascrizione integrale**: l'archivio Icaro ne conserva solo frammenti per punto dell'ordine del giorno, e per le sedute recenti non ha nulla (si ferma alla n. 232 del 25.02.2026, mentre `cerca` arriva a luglio 2026). Quando Icaro non ha la seduta, `get` ripiega sulla scheda del backend corrente e restituisce `pdf_url`: **è lì il resoconto stenografico completo**. Il PDF non viene scaricato — pesa alcuni MB e supera i 200.000 caratteri di testo — ma l'URL è stabile e citabile. In quel caso la risposta non ha il campo `body` (che invece c'è quando il record viene da Icaro) e porta un campo `nota` che lo dice: l'assenza di `body` non significa «testo non disponibile».

  ```bash
  ars-sicilia-pp-cli resoconti get 18 263 --agent --select pdf_url
  # poi, se serve il testo: curl -sL "<pdf_url>" -o seduta.pdf
  ```

**risoluzioni** — Risoluzioni parlamentari (archivio 238).

- `ars-sicilia-pp-cli risoluzioni cerca` — Cerca risoluzioni.
- `ars-sicilia-pp-cli risoluzioni get` — Scarica una singola risoluzione.


### Nessun argomento posizionale sui comandi di ricerca

Ogni criterio si passa come **flag**. I comandi `*/cerca`, `commissioni convocazioni|sommari` e `biblioteca multimediali` non prendono argomenti posizionali e li rifiutano con un errore: `commissioni sommari cerca --commissione X` è sbagliato (`cerca` non è un sottocomando lì), la forma giusta è `commissioni sommari --commissione X`. Prima venivano accettati e scartati in silenzio, il che faceva credere di aver invocato un comando diverso da quello realmente eseguito.

### Un atto per numero: `--numero`, mai `--testo`

Se la notizia dà il numero dell'atto, `--numero` lo aggancia sul campo (`NUMORD` per interrogazioni, interpellanze, mozioni, odg, risoluzioni; `NUMDDL` per i ddl; `LEGNUM` per le leggi) e restituisce quell'atto.

Passare il numero come testo libero aggancia invece **ogni documento che lo cita**, in ordine dal più recente: l'atto cercato può finire oltre il `--limit`. `mozioni cerca --testo "143"` mette la mozione 143 in diciassettesima posizione su diciannove — col limite di default non si vede, e sembra che non esista.

```bash
ars-sicilia-pp-cli mozioni cerca --legisl 18 --numero 143 --json
```

Un numero però non sempre aggancia **un** documento: il portale ne tiene di distinti sotto lo stesso numero, di norma versioni diverse della stessa pratica. Sul ddl 6030 sono due — uno col testo del ddl e l'iter aggiornato, l'altro la sola scheda ferma a due settimane prima — identici in ogni campo della lista, titolo e data comprese. Quando succede, `cerca` e `get` lo dicono con un hint: `get` apre il primo e ne riporta il `docno`.

### `docno` e `permalink`: l'unico URL che si può conservare

Sugli archivi Icaro — tutti tranne `resoconti`, `sommari` e `convocazioni` — `doc_id` e `url` **non identificano il documento**: `icaDocId` è la posizione nella short list della sessione corrente, quindi con un'altra query lo stesso valore apre un altro atto, e fuori sessione l'URL risponde 302. Non citarli e non salvarli.

`get` restituisce anche `docno` — il numero di documento interno del portale, stabile — e `permalink`, che riapre quel documento in una sessione nuova. Sono quelli da conservare in una nota o in un articolo.

```bash
ars-sicilia-pp-cli ddl get 18 6030 --agent --select docno,permalink
```

Gli `url` dei tre archivi serviti dal backend `/bd/` sono invece già citabili (`bd/resoconti/scheda/18/269` risponde 200 senza sessione), e lì `doc_id` non compare affatto.

Il campo `nota` non va messo in `--select`: c'è solo quando serve, e chiederlo dove non c'è fa comparire l'avviso «nota non esiste in questi record». Lo stesso testo arriva comunque su stderr.

### `--testo` cerca le parole, `--frase` cerca la locuzione

`--testo "aree idonee"` costruisce `(aree E idonee)`: entrambe le parole devono comparire **da qualche parte** nel documento. Su un disegno di legge lungo questo aggancia anche atti che hanno una parola all'articolo 3 e l'altra all'articolo 40 — con «aree idonee» escono peschicoltura e coworking accanto agli atti pertinenti.

`--frase "aree idonee"` costruisce `(aree adj idonee)`: parole **adiacenti, nell'ordine dato**, e restano solo gli atti che contengono davvero la locuzione (ddl 803 «Norme in materia di aree idonee e non idonee», ddl 726).

```bash
ars-sicilia-pp-cli ddl cerca --legisl 18 --frase "aree idonee" --json
```

Una parola sola passa invariata. Non esiste su `resoconti`, `sommari` e `convocazioni` (backend `/bd/`): lì il comando **fallisce con un errore esplicito** invece di ignorare il filtro. Se una ricerca a due parole restituisce troppi risultati poco pertinenti, prova `--frase` prima di concludere che l'atto non c'è.

### Finding the right command

When you know what you want to do but not which command does it, ask the CLI directly:

```bash
ars-sicilia-pp-cli which "<capability in your own words>"
```

`which` resolves a natural-language capability query to the best matching command from this CLI's curated feature index. Exit code `0` means at least one match; exit code `2` means no confident match — fall back to `--help` or use a narrower query.

## Recipes

### Sync iniziale completo XVIII legislatura

```bash
ars-sicilia-pp-cli sync --max-pages 0 --resources ddl,leggi,interrogazioni,mozioni,interpellanze,odg,risoluzioni,pareri,resoconti,convocazioni,sommari
```

Prima sincronizzazione di tutti gli archivi politici della XVIII legislatura — i dati restano in `~/.local/share/ars-sicilia-pp-cli/store.db`.

### Iter completo di un DDL con output narrowing

```bash
ars-sicilia-pp-cli ddl iter 18 1153 --json --select fase,data,sede,oratori
```

Timeline del DDL 1153, mostrando solo i campi essenziali — riduce il payload per agenti.

### Network di co-firmatari su DDL

```bash
ars-sicilia-pp-cli sync --resources ddl --deep
ars-sicilia-pp-cli analytics --type ddl --group-by cofirmatari --limit 30 --csv
```

Produce un CSV con le coppie di deputati che firmano DDL insieme — pronto per import in `duckdb` o gephi. **La deep sync è obbligatoria**: i firmatari stanno solo nelle schede di dettaglio, quindi senza di essa il comando restituisce `[]` (con un hint su stderr) — risultato vuoto per mancanza di dati locali, non per assenza di co-firme.

### Drift settimanale dei DDL

```bash
ars-sicilia-pp-cli ddl drift --since 7d --json
```

Confronta lo stato dell'iter rispetto a una settimana fa — i DDL che si sono mossi (commissione → aula, voto, ritiro) compaiono qui.

### Top cofirmatari DDL (XVIII legislatura)

```bash
ars-sicilia-pp-cli sync --resources ddl --legisl 18 --deep
ars-sicilia-pp-cli analytics --type ddl --group-by cofirmatari --limit 20 --legisl 18 --json
```

Classifica i deputati che firmano più DDL insieme (richiede una **deep sync** dei ddl: i firmatari stanno solo nelle schede di dettaglio).

## Auth Setup

Nessuna credenziale richiesta: il portale ARS è pubblico. La sessione `JSESSIONID` per la ricerca è gestita automaticamente in modo trasparente dal client.

Run `ars-sicilia-pp-cli doctor` to verify setup.

## Agent Mode

Add `--agent` to any command. Expands to: `--json --compact --no-input --no-color --yes`.

- **Pipeable** — JSON on stdout, errors on stderr
- **`--envelope` on searches: read the truncation flag, do not infer absence** ⚠️ — by default `*/cerca` prints a bare array and the warnings ("results truncated", "no result has your terms in its title") go to **stderr**, so an agent parsing stdout never sees them. That is not hypothetical: a truncated 3-month search was read as "this sitting record is not indexed", and the record was there. Add `--envelope` and you get `{"risultati": [...], "troncato": true, "hint": "..."}`; `--select` still filters inside `risultati`. **A short list is never proof of absence** — check `troncato` before concluding anything does not exist.

  ```bash
  ars-sicilia-pp-cli resoconti cerca --legisl 17 --data 2019-10-01:2019-12-31 --agent --envelope --limit 10
  ```
- **List titles are cut at 256 characters: never conclude an act is off-topic from its title alone** ⚠️ — the acts with the longest titles (`Schema di progetto di legge costituzionale…`, `Disegno di legge voto…`) are the ones whose subject falls past the cut. XVII-legislature bill 199 is titled "…riconoscimento degli svantaggi derivanti dalla **condizione di insularità**", but the list shows "…svantaggi deriva". Search results whose title hits the cap without matching are ranked between the proven matches and the off-topic rows, and the "no relevant title" hint reports how many titles were cut — when it does, open the document (`ddl get`) for the full title instead of raising `--limit`.

  ```bash
  ars-sicilia-pp-cli ddl cerca --legisl 17 --testo "insularità" --agent --envelope   # ddl 199 first, hint: 1 title cut
  ```
- **Filterable** — `--select` keeps a subset of fields. Dotted paths descend into nested structures; arrays traverse element-wise. On the aggregate commands (`legge cronologia`, `ddl iter`, `deputato profilo`, `commissione dossier`) the payload is an object wrapping an array, so name the fields at the level where they live: `--select data,fase` filters the events, `--select titolo` keeps the act's own title, and mixing both returns both. A name that exists nowhere is reported on stderr with the list of available fields. Critical for keeping context small on verbose APIs:

  ```bash
  ars-sicilia-pp-cli ddl get mock-value mock-value --agent --select id,name,status
  ```
- **Previewable** — `--dry-run` shows the request without sending
- **Offline-friendly** — sync/search commands can use the local SQLite store when available
- **Non-interactive** — never prompts, every input is a flag
- **Read-only** — do not use this CLI for create, update, delete, publish, comment, upvote, invite, order, send, or other mutating requests

### Response envelope

Commands that read from the local store or the API wrap output in a provenance envelope:

```json
{
  "meta": {"source": "live" | "local", "synced_at": "...", "reason": "..."},
  "results": <data>
}
```

Parse `.results` for data and `.meta.source` to know whether it's live or local. A human-readable `N results (live)` summary is printed to stderr only when stdout is a terminal AND no machine-format flag (`--json`, `--csv`, `--compact`, `--quiet`, `--plain`, `--select`) is set — piped/agent consumers and explicit-format runs get pure JSON on stdout.

## Agent Feedback

When you (or the agent) notice something off about this CLI, record it:

```
ars-sicilia-pp-cli feedback "the --since flag is inclusive but docs say exclusive"
ars-sicilia-pp-cli feedback --stdin < notes.txt
ars-sicilia-pp-cli feedback list --json --limit 10
```

Entries are stored locally at `~/.local/share/ars-sicilia-pp-cli/feedback.jsonl`. They are never POSTed unless `ARS_SICILIA_FEEDBACK_ENDPOINT` is set AND either `--send` is passed or `ARS_SICILIA_FEEDBACK_AUTO_SEND=true`. Default behavior is local-only.

Write what *surprised* you, not a bug report. Short, specific, one line: that is the part that compounds.

## Output Delivery

Every command accepts `--deliver <sink>`. The output goes to the named sink in addition to (or instead of) stdout, so agents can route command results without hand-piping. Three sinks are supported:

| Sink | Effect |
|------|--------|
| `stdout` | Default; write to stdout only |
| `file:<path>` | Atomically write output to `<path>` (tmp + rename) |
| `webhook:<url>` | POST the output body to the URL (`application/json` or `application/x-ndjson` when `--compact`) |

Unknown schemes are refused with a structured error naming the supported set. Webhook failures return non-zero and log the URL + HTTP status on stderr.

## Named Profiles

A profile is a saved set of flag values, reused across invocations. Use it when a scheduled agent calls the same command every run with the same configuration - HeyGen's "Beacon" pattern.

```
ars-sicilia-pp-cli profile save briefing --json
ars-sicilia-pp-cli --profile briefing ddl get mock-value mock-value
ars-sicilia-pp-cli profile list --json
ars-sicilia-pp-cli profile show briefing
ars-sicilia-pp-cli profile delete briefing --yes
```

Explicit flags always win over profile values; profile values win over defaults. `agent-context` lists all available profiles under `available_profiles` so introspecting agents discover them at runtime.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Usage error (wrong arguments) |
| 3 | Resource not found |
| 5 | API error (upstream issue) |
| 7 | Rate limited (wait and retry) |
| 10 | Config error |

## Argument Parsing

Parse `$ARGUMENTS`:

1. **Empty, `help`, or `--help`** → show `ars-sicilia-pp-cli --help` output
2. **Starts with `install`** → ends with `mcp` → MCP installation; otherwise → see Prerequisites above
3. **Anything else** → Direct Use (execute as CLI command with `--agent`)

## MCP Server Installation

Install the MCP binary from this CLI's published public-library entry or pre-built release, then register it:

```bash
claude mcp add ars-sicilia-pp-mcp -- ars-sicilia-pp-mcp
```

Verify: `claude mcp list`

## Direct Use

1. Check if installed: `which ars-sicilia-pp-cli`
   If not found, offer to install (see Prerequisites at the top of this skill).
2. Match the user query to the best command from the Unique Capabilities and Command Reference above.
3. Execute with the `--agent` flag:
   ```bash
   ars-sicilia-pp-cli <command> [subcommand] [args] --agent
   ```
4. If ambiguous, drill into subcommand help: `ars-sicilia-pp-cli <command> --help`.
