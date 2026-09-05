# Work Continuity — Python Authority / Memory Reference

Last updated: 2026-09-05T14:40+02:00  
Repository: `MATRIXNEO23/memoria`  
Canonical branch: `main`  
Active branch: `python-authority-p0-v1`

## Owner-approved sequence

```text
1. Understanding V3 real TypedClaims       COMPLETE in assembling
2. Python Authority Resolver P0 fixes      ACTIVE HERE
3. Integrate Authority with Understanding  NOT STARTED
4. Memory Kotlin/Room                      NOT STARTED
```

`MATRIXNEO23/assembling` is read-only during this workstream. Its CP-U3 merge is `089cb7169c5f511ffd5d27b8a1d5e887c4348b0c`, post-merge CI `33966306986 = SUCCESS`.

## Foundation v3 provenance

Reference details/checksums: `REFERENCE_FOUNDATION_V3.md`.

Recovered canonical Foundation/Admission baseline was run unchanged:

```text
25 passed
```

The recovered v3 Admission consumes explicit `contradicts_memory_id` and does not infer contradiction itself.

## Python Authority P0 implementation

Branch base:

`712d84df59aa2e0ce153f6287e4b214c789dc49b`

Files added:

```text
memory/models.py
memory/authority_models.py
memory/authority_resolver.py
tests/test_authority_resolver_p0.py
.github/workflows/ci.yml
REFERENCE_FOUNDATION_V3.md
WORK_CONTINUITY.md
```

`memory/models.py` is the recovered canonical v3 model contract and preserves `contradicts_memory_id`.

The Authority resolver does NOT define a second TypedClaim dataclass. It consumes `TypedClaimLike` as a structural protocol and returns `AuthorityResolution`.

### Closed P0s

```text
P0-PA-01 owner hardcoded test_agent
  FIX: owner is mandatory structured claim evidence and is passed explicitly to MemoryEvidencePort.

P0-PA-02 fragile regex/free-text property extraction
  FIX: resolver contract contains structured predicate/object/polarity/temporal fields; resolver imports no regex parser and never reparses content.

P0-PA-03 false conflict from actor overlap + low content similarity
  FIX: contradiction requires matching owner + subject + predicate + target scope + compatible temporal identity and incompatible structured value/polarity. Actor overlap is not a contradiction signal.
```

### Additional fail-closed behavior covered

```text
VALID-only Memory candidates
same semantic slot current-value contradiction
opposite polarity on same value
historical/current temporal change non-conflict
same historical anchor can conflict
multiple real targets -> HOLD / no guessing
REPORT/BELIEF/DIRECT classification from structured claimKind
WORLD_TRUTH/OBSERVATION only explicit trusted request evidence
high confidence does not promote BELIEF
INVALID/ABSTAINED/AMBIGUOUS -> HOLD
QUESTION/REQUEST/COMMAND -> no contradiction target
read-only evidence port exposes no persistence mutation methods
```

## Local gates

Isolated repo payload:

```text
15 passed
```

Full recovered Foundation + new resolver/tests:

```text
41 passed
= 25 Foundation/Admission regressions + 16 Authority/P0 tests
```

One intermediate test expectation error (`SUPERSEDE` vs enum value `supersede`) was corrected in the test only; production code was unchanged.

## Hard boundaries

```text
no Foundation schema mutation
no Repository semantic mutation
no Admission behavior mutation
no lineage/supersede/rollback changes
no writes from AuthorityResolver
no assembling writes during this repo work
no Memory Kotlin/Room yet
```

## Exact restart point

```text
repo = MATRIXNEO23/memoria
branch = python-authority-p0-v1
Python Authority P0 code = IMPLEMENTED
local isolated tests = 15/15 PASS
full recovered Foundation cross-check = 41/41 PASS
current operation = verify GitHub CI for branch, open PR, merge only if green
next after merge = return to assembling for Understanding V3 -> Authority integration
```
