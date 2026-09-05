# Memory Foundation v3 — Reference Provenance

Status: REFERENCE SOURCE RECOVERED / READ-ONLY BASELINE  
Date: 2026-09-05

The Python Authority P0 work was built against the canonical Memory Foundation v3 files recovered from ChatGPT Library. The Foundation files were not edited during the P0 resolver implementation.

## Recovered source checksums

```text
memory/__init__.py              fd936476495865290862fb63adbfd0add54bf606a0c56c67d5c73e607e198a70
memory/admission.py             ea52a90056218daf9b96b3d106430b8de4c5f7c0a4f2dcb7cedfdc2c7d1e52fa
memory/admission_models.py      f0e926ed1d1848c3c235e342f1ad36a33c3806c86331ab3bdce044c78afb1bb9
memory/database.py              1b9d2d61157b1aa0b755d59d69ebff04ee29c5b2bfdefc38f2037b1bd59db69a
memory/models.py                e98f43b5191a39df70228bbfbdaff80b09b829d1ffb5ffc8bdc0d9685cd3b357
memory/repository.py            89c34762aaf31cc4eaf4f32022cbf66464142cbb4490a494a328f638103522ad
memory/schema.py                d479b0d9ab4d83fb79e85542d859a7a37e2074471212a92252f3d5e9ef5e357b

tests/conftest.py                         1bff5230e66a62cd8d82afa610a1700956eab251af0e0786e8fc09129fb533d2
tests/test_atomic_rollback.py             31c0d6787d1dacaf9cb49d49cf28dda85b2e92928ab07e101d561ea323f6e44a
tests/test_delete_protection.py           ac705658b4adcd4c84452555637fc4d2e33c502a92eab6e0005f286a857fe50c
tests/test_lineage_protection.py          fbe210c92ff932c1223eb2100c3305516f1fb2c854a4e347090cd58abd8d14a6
tests/test_memory_admission.py            47ba6448686fb7fe497745fea7fcdeb2840e598fdfdad415ecd976dde988be2d
tests/test_memory_admission_authority.py  4ece9b0c80bc2feb5ad4ac19052551d99765fc3dc0df5d95ef0fa71e993bf7fb
tests/test_memory_admission_rejection.py  808b20d96e6f0ffdcf74a6569e98dc8415b5a4f655da6c1267a5ecd979ace35d
tests/test_memory_admission_supersede.py  76a0e4f778c508c438051589b9c1447883f3302af55baca58590713194e2cc38
tests/test_semantic_update.py             512e75427a6f1795c16fbba43261e604fb5fa88e4a97646c3a165765d86ae053
```

## Baseline verification

Running the recovered Foundation unchanged with:

```text
python -m pytest -q
```

produced:

```text
25 passed
```

The recovered `admission.py` consumes explicit `record.contradicts_memory_id`; it does not infer conflicts from actor overlap or content difference. A referenced contradiction target is ignored when missing or not `ValidityStatus.VALID`.

## Python Authority P0 cross-check

The new resolver/tests were then added locally on top of the unchanged recovered Foundation. Combined result:

```text
41 passed
```

This means all 25 Foundation/Admission regressions stayed green while the new Authority P0 tests passed.

## P0 defects closed by the new resolver

```text
P0-PA-01 owner hardcoded `test_agent`
P0-PA-02 fragile regex/free-text property extraction
P0-PA-03 actor overlap + low content similarity treated as conflict
```

The replacement resolver consumes structured TypedClaim semantics only and exposes a read-only `MemoryEvidencePort`; it has no persistence mutation API.
