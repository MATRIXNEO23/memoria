"""Deterministic read-only Authority Resolver reference implementation.

P0 guarantees:
- owner is taken from the structured claim; never hardcoded;
- no regex/free-text property extraction exists;
- shared actor/entity or low text similarity can never create a contradiction.

The resolver consumes structured semantics only and never writes Memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .authority_models import (
    AuthorityResolution,
    AuthorityResolutionStatus,
    AuthorityResolveRequest,
    MemoryEvidence,
    MemoryEvidencePort,
)
from .models import Authority, ValidityStatus


NON_ASSERTIVE_DIALOGUE_ACTS = {"QUESTION", "REQUEST", "COMMAND"}
SINGLE_VALUE_PREDICATES = frozenset({"residence.place", "identity.age", "identity.name"})
DIRECT_COMPARE_TEMPORAL = frozenset({"CURRENT", "ATEMPORAL"})


@dataclass(frozen=True)
class _Classification:
    authority: Optional[Authority]
    reason_code: str


class AuthorityResolver:
    """Canonical Python reference resolver; all Memory access is read-only."""

    def __init__(
        self,
        evidence_port: MemoryEvidencePort,
        *,
        single_value_predicates: frozenset[str] = SINGLE_VALUE_PREDICATES,
    ) -> None:
        self._evidence_port = evidence_port
        self._single_value_predicates = single_value_predicates

    def resolve(self, request: AuthorityResolveRequest) -> AuthorityResolution:
        claim = request.claim

        if claim.structural_status.upper() != "VALID" or claim.interpretation_status.upper() == "ABSTAINED":
            return self._hold(request, "AUTHORITY.CLAIM_INVALID_OR_ABSTAINED")
        if claim.interpretation_status.upper() == "AMBIGUOUS":
            return self._hold(request, "AUTHORITY.CLAIM_AMBIGUOUS")
        if not claim.claim_id or not claim.predicate:
            return self._hold(request, "AUTHORITY.CLAIM_REQUIRED_FIELD_MISSING")
        if not claim.subject:
            return self._hold(request, "AUTHORITY.SUBJECT_UNRESOLVED")
        if not claim.owner:
            return self._hold(request, "AUTHORITY.OWNER_UNRESOLVED")

        classification = self._classify(request)
        if classification.authority is None:
            return self._hold(request, classification.reason_code)
        if classification.authority == Authority.REPORT and not claim.source:
            return self._hold(request, "AUTHORITY.SOURCE_UNRESOLVED")
        if classification.authority == Authority.BELIEF and not claim.perspective:
            return self._hold(request, "AUTHORITY.PERSPECTIVE_UNRESOLVED")

        confidence = self._resolution_confidence(request)
        if claim.dialogue_act.upper() in NON_ASSERTIVE_DIALOGUE_ACTS:
            return AuthorityResolution(
                claim_id=claim.claim_id,
                authority=classification.authority,
                authority_resolution_confidence=confidence,
                source_reliability=request.source_reliability,
                status=AuthorityResolutionStatus.HOLD,
                reason_codes=(classification.reason_code, "AUTHORITY.NON_ASSERTIVE_HOLD"),
            )

        # P0-01: use the actual structured owner; never a hardcoded agent.
        candidates = tuple(self._evidence_port.find_candidates(
            owner=claim.owner,
            subject=claim.subject,
            predicate=claim.predicate,
        ))
        valid_candidates = tuple(c for c in candidates if c.validity == ValidityStatus.VALID)
        candidate_ids = tuple(c.memory_id for c in valid_candidates)
        contradictions = [c for c in valid_candidates if self._is_semantic_contradiction(claim, c)]

        if len(contradictions) == 1:
            return AuthorityResolution(
                claim_id=claim.claim_id,
                authority=classification.authority,
                authority_resolution_confidence=confidence,
                source_reliability=request.source_reliability,
                status=AuthorityResolutionStatus.COMPLETE,
                contradicted_memory_id=contradictions[0].memory_id,
                candidate_memory_ids=candidate_ids,
                reason_codes=(classification.reason_code, "AUTHORITY.CONTRADICTION_SINGLE_TARGET"),
            )
        if len(contradictions) > 1:
            return AuthorityResolution(
                claim_id=claim.claim_id,
                authority=classification.authority,
                authority_resolution_confidence=confidence,
                source_reliability=request.source_reliability,
                status=AuthorityResolutionStatus.HOLD,
                candidate_memory_ids=candidate_ids,
                ambiguity_reasons=("multiple semantic contradiction targets",),
                reason_codes=(classification.reason_code, "AUTHORITY.CONTRADICTION_AMBIGUOUS"),
            )

        return AuthorityResolution(
            claim_id=claim.claim_id,
            authority=classification.authority,
            authority_resolution_confidence=confidence,
            source_reliability=request.source_reliability,
            status=AuthorityResolutionStatus.COMPLETE,
            candidate_memory_ids=candidate_ids,
            reason_codes=(classification.reason_code, "AUTHORITY.CONTRADICTION_NONE"),
        )

    def _classify(self, request: AuthorityResolveRequest) -> _Classification:
        claim = request.claim
        if request.trusted_world_truth:
            return _Classification(Authority.WORLD_TRUTH, "AUTHORITY.RESOLVED_WORLD_TRUTH")
        if request.trusted_observation:
            return _Classification(Authority.OBSERVATION, "AUTHORITY.RESOLVED_OBSERVATION")
        if request.derived_inference:
            return _Classification(Authority.INFERENCE, "AUTHORITY.RESOLVED_INFERENCE")

        kind = claim.claim_kind.upper()
        if kind == "REPORT":
            return _Classification(Authority.REPORT, "AUTHORITY.RESOLVED_REPORT")
        if kind in {"BELIEF", "HYPOTHESIS"}:
            return _Classification(Authority.BELIEF, "AUTHORITY.RESOLVED_BELIEF")
        if kind == "DIRECT":
            return _Classification(Authority.REPORT, "AUTHORITY.RESOLVED_REPORT")
        return _Classification(None, "AUTHORITY.CLASSIFICATION_UNRESOLVED")

    def _resolution_confidence(self, request: AuthorityResolveRequest) -> float:
        confidence = float(request.claim.overall_interpretation_confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("overall_interpretation_confidence must be in [0,1]")
        return confidence if request.source_reliability is None else min(confidence, request.source_reliability)

    def _is_semantic_contradiction(self, claim, memory: MemoryEvidence) -> bool:
        # P0-02/P0-03: structured semantic slot only. No text parsing, regex or actor-overlap score.
        if memory.owner != claim.owner or memory.subject != claim.subject or memory.predicate != claim.predicate:
            return False
        if memory.target != claim.target:
            return False
        if not self._temporal_identity_compatible(claim, memory):
            return False

        claim_object = self._normalized_value(claim.object_value)
        memory_object = self._normalized_value(memory.object_value)
        claim_polarity = claim.polarity.upper()
        memory_polarity = memory.polarity.upper()

        if claim_object is not None and claim_object == memory_object:
            return {claim_polarity, memory_polarity} == {"POSITIVE", "NEGATIVE"}

        if claim.predicate in self._single_value_predicates:
            if claim_object is None or memory_object is None:
                return False
            return claim_object != memory_object and claim_polarity == memory_polarity == "POSITIVE"
        return False

    @staticmethod
    def _temporal_identity_compatible(claim, memory: MemoryEvidence) -> bool:
        claim_relation = claim.temporal_relation.upper()
        memory_relation = memory.temporal_relation.upper()
        if claim_relation != memory_relation:
            return False
        if claim_relation in DIRECT_COMPARE_TEMPORAL:
            return True
        if not claim.temporal_anchor_ref or not memory.temporal_anchor_ref:
            return False
        return claim.temporal_anchor_ref == memory.temporal_anchor_ref

    @staticmethod
    def _normalized_value(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = " ".join(value.strip().casefold().split())
        return normalized or None

    @staticmethod
    def _hold(request: AuthorityResolveRequest, reason: str) -> AuthorityResolution:
        claim_id = request.claim.claim_id or "unresolved-claim"
        confidence = request.claim.overall_interpretation_confidence
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            confidence = None
        return AuthorityResolution(
            claim_id=claim_id,
            authority=None,
            authority_resolution_confidence=None if confidence is None else float(confidence),
            source_reliability=request.source_reliability,
            status=AuthorityResolutionStatus.HOLD,
            reason_codes=(reason,),
        )
