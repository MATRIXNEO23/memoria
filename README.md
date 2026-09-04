# Matrix Memory Foundation

Data: 2026-09-04
Repo: `MATRIXNEO23/memoria`
Stato: discussione tecnica salvata / punto di ripresa operativo

Questo repository nasce per raccogliere e sviluppare il sistema memoria del progetto Matrix / Luna / Neon Tides.

L'obiettivo non e' copiare un sistema completo esistente, ma costruire una Memory Foundation compatibile con gli altri moduli gia' previsti:

```text
ONNX NLU
→ Understanding
→ Coherence Guard / Semantic Coherence Buffer
→ Authority Resolver
→ Memory Admission
→ MemoryRepository
→ Affective Engine
→ GGUF Context Builder
→ Risposta
```

## Decisione principale

Ha senso fare prima una base memoria, ma non ha senso scrivere memoria stabile prima dei controlli semantici.

Distinzione fondamentale:

```text
SI:
Memory substrate prima
= schema, repository, stati, provenance, raw log, provisional memory

NO:
memoria definitiva/stabile prima
= scrivere fatti persistenti senza Coherence Guard / Authority Resolver
```

Ordine consigliato:

```text
1. Memory Foundation v0.1
2. Coherence Guard v0.1
3. Authority Resolver P0 fix
4. Memory Admission stabile
5. Affective Engine collegato solo a claim/memorie sicure
```

## Perche' la memoria prima ha senso

Il Coherence Guard ha bisogno di confrontare il nuovo claim con qualcosa:

- memoria precedente;
- owner;
- source/provenance;
- confidence;
- validita' temporale;
- stato provvisorio/stabile;
- eventuale memoria superseded.

Senza una memoria minima, il filtro puo' solo dire che una frase e' incerta, ma non puo' decidere bene se:

- contraddice un fatto precedente;
- aggiorna un fatto;
- corregge una memoria;
- e' solo un report di terzi;
- deve restare transient;
- puo' diventare memoria stabile.

## Regola di sicurezza

La memoria iniziale puo' accettare dati non sicuri solo come RAW o PROVISIONAL, mai come verita' stabile.

Lifecycle minimo:

```text
RAW_OBSERVATION
↓
PROVISIONAL_CLAIM
↓
COHERENCE_CHECKED
↓
AUTHORITY_RESOLVED
↓
ADMITTED_MEMORY
↓
AFFECTIVE_SAFE_EVENT
```

## Memory Foundation v0.1

Prima versione consigliata: store stupido ma sicuro.

Non deve ragionare troppo. Deve salvare bene, con stati e provenienza.

Componenti minimi:

```text
MemoryObservation
- id
- sessionId
- speakerId
- rawText
- timestamp
- source
- diagnosticTraceId

MemoryClaim
- id
- ownerId
- subjectId
- predicate
- objectValue
- polarity
- temporalRelation
- confidence
- sourceType
- status
- validAt
- invalidAt
- supersedesId
- createdFromObservationId

MemorySearchIndex
- claimId
- searchableText
```

Stati minimi:

```text
RAW
PROVISIONAL
COHERENCE_CHECKED
AUTHORITY_RESOLVED
ADMITTED
SUPERSEDED
REJECTED
```

## Implementazione Android consigliata

Base piu' compatibile:

```text
Room / SQLite locale
+ FTS per ricerca testuale
+ schema a stati
+ provenance
+ valid_at / invalid_at
+ supersedes_id
+ raw log immutabile
```

Questa e' la soluzione piu' facile da integrare in Android/Kotlin e non richiede server.

## Cosa copiare/adattare da progetti esistenti

Non conviene fare reverse engineering di codice proprietario.
Conviene invece studiare e adattare pattern da codice open-source con licenza compatibile.

Fonti/pattern utili:

| Fonte | Cosa prendere | Cosa evitare |
|---|---|---|
| Room/SQLite | database locale, DAO, FTS, indici | reinventare lo storage |
| Atlas | belief revision, dependency ledger, ripple/reassessment | portare tutto Python/Neo4j |
| Graphiti/Zep | temporal facts, valid_at, invalid_at, invalidazione storica | stack server/graph completo |
| Letta/MemGPT | separazione core memory / recall memory / archival memory | runtime agent/server |
| Mem0 | operazioni ADD / UPDATE / DELETE / NOOP | SDK completo come dipendenza principale |
| Drools/TMS | justification/retraction | motore rules intero |

## Pattern da Atlas

Atlas e' il candidato concettualmente piu' vicino, ma non va integrato direttamente.

Pattern da copiare:

```text
quando un fatto cambia:
- non cancellare il vecchio;
- crea nuova revisione;
- collega supersedes_id;
- rivaluta i fatti dipendenti;
- mantieni audit/ledger.
```

Uso previsto in Matrix:

```text
MemoryClaim A viene superseded da MemoryClaim B
→ i claim dipendenti vengono marcati NEEDS_REVIEW o STALE
→ il GGUF non riceve piu' A come verita' attiva
→ Affective Engine non usa A per effetti persistenti futuri
```

## Pattern da Graphiti/Zep

Pattern da copiare:

```text
ogni fatto ha:
- quando e' stato osservato;
- da quando e' valido;
- quando viene invalidato;
- da quale episodio/frase deriva;
- quale fatto precedente sostituisce.
```

Campi consigliati:

```text
observedAt
validAt
invalidAt
expiredAt opzionale
supersedesId
sourceObservationId
```

## Pattern da Letta/MemGPT

Separare le memorie per funzione:

```text
Core Memory
- informazioni sempre importanti su utente/personaggio/relazione;
- molto piccola;
- alta affidabilita'.

Recall Memory
- cronologia conversazionale cercabile;
- episodi, dialoghi, eventi.

Archival Memory
- fatti lunghi, dettagli, conoscenza accumulata;
- recuperata solo quando serve.
```

Per Luna/Neon Tides:

```text
Core Memory = identita', relazione, preferenze stabili, limiti, promesse importanti
Recall Memory = episodi di chat e gioco
Archival Memory = fatti secondari, storia, eventi, dettagli ambientali
```

## Pattern da Mem0

Usare un classificatore di operazione memoria:

```text
ADD
UPDATE
DELETE / FORGET
NOOP
```

In Matrix puo' diventare:

```text
MemoryOperation.ADD_PROVISIONAL
MemoryOperation.ADMIT_STABLE
MemoryOperation.SUPERSEDE
MemoryOperation.REJECT
MemoryOperation.NOOP
```

## Pattern da Drools/TMS

Ogni memoria stabile dovrebbe avere una giustificazione.

```text
MemoryClaim stabile
→ giustificato da Observation + Confidence + Source + CoherenceDecision + AuthorityDecision
```

Se la giustificazione cade:

```text
claim.status = SUPERSEDED / REJECTED / NEEDS_REVIEW
```

Non serve integrare Drools. Serve solo il pattern di justification/retraction.

## Collegamento con Coherence Guard

Il Coherence Guard non deve duplicare l'NLU.

Divisione corretta:

```text
NLU / Understanding
= interpreta il linguaggio: soggetto, predicato, oggetto, negazione, tempo, intenzione

Coherence Guard / Authority
= verifica se l'interpretazione e' sicura, affidabile, contraddittoria, reportata o memorizzabile
```

Non devono esistere due moduli che interpretano entrambi testo libero.

Schema corretto:

```text
NLU ONNX
↓
Understanding
    produce TypedClaim strutturato
↓
Coherence Guard
    valida stabilita' e rischio
↓
Authority Resolver
    fonte / conflitto / supersede
↓
Memory Admission
    scrittura finale controllata
```

## Coherence Guard v0.1 collegato alla memoria

Scelta piu' veloce:

```text
Understanding → CoherenceGuard → MemoryAdmission
```

Decisioni minime:

```text
SAFE_TO_ADMIT
SAFE_TRANSIENT_ONLY
LOW_CONFIDENCE_HOLD
REPORT_ONLY
QUESTION_ONLY
CONFLICT_REQUIRES_REVIEW
REJECTED_UNSAFE
```

Regole iniziali:

```text
owner mancante → REJECTED_UNSAFE
dialogueAct == QUESTION → QUESTION_ONLY
sourceType == THIRD_PARTY_REPORT → REPORT_ONLY
negation < 0.94 → LOW_CONFIDENCE_HOLD
predicate < 0.90 → LOW_CONFIDENCE_HOLD
subjectReferent < 0.92 → LOW_CONFIDENCE_HOLD
targetReferent < 0.92 → LOW_CONFIDENCE_HOLD
temporalRelation < 0.88 → SAFE_TRANSIENT_ONLY
stessa proprieta' + valore opposto → CONFLICT_REQUIRES_REVIEW
proprieta' diversa → nessun conflitto
tutto stabile → SAFE_TO_ADMIT
```

## Protezione Affective Engine

Regola obbligatoria:

```text
Affective Engine persistente solo da:
- SAFE_TO_ADMIT
- CORRECTION_SUPERSEDES / memoria ammessa stabile
```

Claim incerti, domande, report di terzi e conflitti non risolti possono produrre solo contesto temporaneo o diagnostica, non cambi persistenti di fiducia/risentimento/affetto.

## Authority Resolver P0 da correggere

La memoria deve aiutare a correggere questi problemi:

1. owner hardcoded;
2. property extraction fragile;
3. falso conflitto tra fatti indipendenti;
4. confronto basato su testo diverso invece che su stessa proprieta' normalizzata.

Regola nuova:

```text
Conflitto solo se:
- stesso owner/scope;
- stesso subject normalizzato;
- stessa proprieta' normalizzata;
- valore/polarita'/validita' incompatibili.

Nessun conflitto se cambia solo il testo o se la proprieta' e' diversa.
```

Esempio corretto:

```text
Marco vive a Roma
Marco ama il caffe'
→ nessun conflitto
```

Esempio conflitto:

```text
Marco vive a Roma
Marco vive a Milano
→ stesso subject + stessa proprieta' location + valore diverso
→ conflict/review/supersede
```

## Ordine pratico di sviluppo

```text
1. Room database + entita' MemoryObservation / MemoryClaim
2. DAO base:
   - insertRaw
   - insertProvisional
   - getActiveClaims
   - markSuperseded
   - markRejected
3. FTS search per ricordi candidati
4. Status lifecycle RAW → PROVISIONAL → ADMITTED / REJECTED
5. validAt / invalidAt / supersedesId
6. diagnostica Memory Lifecycle Trace
7. Coherence Guard v0.1
8. Authority Resolver P0 fix
9. Integration test Understanding → Memory → Coherence → Authority → Affective
```

## Tempo stimato

```text
Memory Foundation v0.1 funzionante: 1 giorno
Memory + FTS + lifecycle + diagnostica buona: 2-3 giorni
Memoria robusta con supersede, rollback, dependency ledger e integrazione completa: circa 1 settimana
```

## Decisione finale salvata

La strada migliore e piu' facile e':

```text
BUILD interno
+ Room/SQLite come base reale
+ pattern Atlas per revisioni/dipendenze
+ pattern Graphiti/Zep per temporalita'
+ pattern Letta/MemGPT per core/recall/archive
+ pattern Mem0 per add/update/delete/noop
+ pattern Drools/TMS per justification/retract
```

Non usare un sistema esterno completo come drop-in.
Non fare reverse engineering proprietario.
Costruire una Memory Foundation piccola, sicura, locale e compatibile con tutti gli altri moduli.

## Punto di ripresa operativo

Prossimo step consigliato:

```text
Implementare Memory Foundation v0.1
```

Output atteso:

```text
- entita' Room/SQLite per observation e claim;
- DAO minimo;
- lifecycle status;
- campi provenance/confidence/source;
- supersedesId/validAt/invalidAt;
- test unitari su ADD, PROVISIONAL, ADMITTED, SUPERSEDED, REJECTED;
- nessuna integrazione affettiva persistente prima di Coherence/Authority.
```

Criterio di accettazione:

```text
La memoria puo' salvare osservazioni grezze e claim provvisori,
ma nessun claim diventa verita' stabile senza passare dai gate successivi.
```
