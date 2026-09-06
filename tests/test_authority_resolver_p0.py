from dataclasses import dataclass

from memory.authority_models import AuthorityResolveRequest, AuthorityResolutionStatus, MemoryEvidence
from memory.authority_resolver import AuthorityResolver
from memory.models import Authority, ValidityStatus


@dataclass(frozen=True)
class ClaimFixture:
    claim_id: str = "c0"
    owner: str | None = "luna"
    subject: str | None = "albert"
    target: str | None = None
    perspective: str | None = "user"
    source: str | None = "user"
    predicate: str = "residence.place"
    object_value: str | None = "Milan"
    polarity: str = "POSITIVE"
    temporal_relation: str = "CURRENT"
    temporal_anchor_ref: str | None = None
    dialogue_act: str = "ASSERT"
    claim_kind: str = "DIRECT"
    overall_interpretation_confidence: float = 0.95
    structural_status: str = "VALID"
    interpretation_status: str = "RESOLVED"


class FakeEvidencePort:
    def __init__(self, candidates=()):
        self.candidates = tuple(candidates)
        self.calls = []

    def find_candidates(self, *, owner: str, subject: str, predicate: str):
        self.calls.append((owner, subject, predicate))
        return self.candidates


def evidence(memory_id=1, **overrides):
    values = dict(
        memory_id=memory_id,
        owner="luna",
        subject="albert",
        predicate="residence.place",
        object_value="Venice",
        target=None,
        polarity="POSITIVE",
        temporal_relation="CURRENT",
        temporal_anchor_ref=None,
        validity=ValidityStatus.VALID,
        authority=Authority.REPORT,
    )
    values.update(overrides)
    return MemoryEvidence(**values)


def resolve(claim=ClaimFixture(), candidates=(), **request_overrides):
    port = FakeEvidencePort(candidates)
    result = AuthorityResolver(port).resolve(AuthorityResolveRequest(claim=claim, **request_overrides))
    return result, port


def test_p0_owner_is_never_hardcoded():
    claim = ClaimFixture(owner="agent-42", subject="alice", predicate="identity.age", object_value="31")
    result, port = resolve(claim)
    assert result.status == AuthorityResolutionStatus.COMPLETE
    assert port.calls == [("agent-42", "alice", "identity.age")]
    assert all("test_agent" not in value for call in port.calls for value in call)


def test_p0_contract_has_no_free_text_property_extraction():
    fields = set(ClaimFixture.__dataclass_fields__)
    assert {"predicate", "object_value", "polarity", "temporal_relation"} <= fields
    assert "content" not in fields
    result, _ = resolve(
        ClaimFixture(predicate="residence.place", object_value="Milano"),
        (evidence(predicate="residence.place", object_value="Venezia"),),
    )
    assert result.contradicted_memory_id == 1


def test_p0_unrelated_fact_same_subject_is_not_conflict():
    claim = ClaimFixture(predicate="preference.like", object_value="coffee")
    result, _ = resolve(claim, (evidence(predicate="residence.place", object_value="Venice"),))
    assert result.status == AuthorityResolutionStatus.COMPLETE
    assert result.contradicted_memory_id is None


def test_same_slot_current_different_value_is_conflict():
    result, _ = resolve(ClaimFixture(object_value="Milan"), (evidence(memory_id=7, object_value="Venice"),))
    assert result.contradicted_memory_id == 7


def test_opposite_polarity_same_value_is_conflict():
    result, _ = resolve(
        ClaimFixture(object_value="Milan", polarity="NEGATIVE"),
        (evidence(memory_id=8, object_value="Milan", polarity="POSITIVE"),),
    )
    assert result.contradicted_memory_id == 8


def test_temporal_change_is_not_conflict_by_default():
    old = evidence(memory_id=9, object_value="Venice", temporal_relation="PAST", temporal_anchor_ref="year:2020")
    result, _ = resolve(ClaimFixture(object_value="Milan", temporal_relation="CURRENT"), (old,))
    assert result.contradicted_memory_id is None


def test_same_historical_anchor_can_conflict():
    old = evidence(memory_id=10, object_value="Venice", temporal_relation="PAST", temporal_anchor_ref="year:2020")
    claim = ClaimFixture(object_value="Milan", temporal_relation="PAST", temporal_anchor_ref="year:2020")
    result, _ = resolve(claim, (old,))
    assert result.contradicted_memory_id == 10


def test_superseded_candidate_is_not_target():
    result, _ = resolve(ClaimFixture(object_value="Milan"), (evidence(memory_id=11, validity=ValidityStatus.SUPERSEDED),))
    assert result.contradicted_memory_id is None
    assert result.candidate_memory_ids == ()


def test_multiple_conflicts_hold_instead_of_guessing():
    result, _ = resolve(
        ClaimFixture(object_value="Milan"),
        (evidence(memory_id=12, object_value="Venice"), evidence(memory_id=13, object_value="Rome")),
    )
    assert result.status == AuthorityResolutionStatus.HOLD
    assert result.contradicted_memory_id is None
    assert "AUTHORITY.CONTRADICTION_AMBIGUOUS" in result.reason_codes


def test_structured_claim_kind_classification():
    report, _ = resolve(ClaimFixture(claim_kind="REPORT", source="alice"))
    belief, _ = resolve(ClaimFixture(claim_kind="BELIEF", perspective="alice", source=None))
    direct, _ = resolve(ClaimFixture(claim_kind="DIRECT", source="user"))
    assert report.authority == Authority.REPORT
    assert belief.authority == Authority.BELIEF
    assert direct.authority == Authority.REPORT


def test_world_truth_and_observation_require_explicit_trusted_evidence():
    observation, _ = resolve(ClaimFixture(source=None), trusted_observation=True)
    truth, _ = resolve(ClaimFixture(source=None), trusted_world_truth=True)
    ordinary, _ = resolve(ClaimFixture(claim_kind="DIRECT", source="user"))
    assert observation.authority == Authority.OBSERVATION
    assert truth.authority == Authority.WORLD_TRUTH
    assert ordinary.authority == Authority.REPORT


def test_confidence_never_promotes_belief_authority():
    result, _ = resolve(ClaimFixture(claim_kind="BELIEF", perspective="alice", source=None, overall_interpretation_confidence=1.0))
    assert result.authority == Authority.BELIEF


def test_invalid_abstained_and_ambiguous_claims_hold():
    invalid, _ = resolve(ClaimFixture(structural_status="INVALID", interpretation_status="ABSTAINED"))
    ambiguous, _ = resolve(ClaimFixture(interpretation_status="AMBIGUOUS"))
    assert invalid.status == AuthorityResolutionStatus.HOLD
    assert ambiguous.status == AuthorityResolutionStatus.HOLD


def test_non_assertive_act_never_selects_contradiction():
    result, _ = resolve(
        ClaimFixture(dialogue_act="QUESTION", object_value="Milan"),
        (evidence(memory_id=14, object_value="Venice"),),
    )
    assert result.status == AuthorityResolutionStatus.HOLD
    assert result.contradicted_memory_id is None


def test_evidence_port_is_read_only_by_construction():
    public = {name for name in dir(FakeEvidencePort) if not name.startswith("_")}
    assert public == {"find_candidates"}
    assert not ({"save", "update", "delete", "supersede", "admit"} & public)
