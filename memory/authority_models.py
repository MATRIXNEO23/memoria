"""Read-only Authority Resolver contracts for the Matrix Memory Foundation reference.

This module deliberately does NOT define a second TypedClaim dataclass. The resolver
consumes a structural TypedClaimLike protocol produced by the canonical Understanding/MIP
boundary and returns an AuthorityResolution. No persistence APIs live here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol, Sequence, runtime_checkable

from .models import Authority, ValidityStatus


class AuthorityResolutionStatus(Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    HOLD = "HOLD"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


@runtime_checkable
class TypedClaimLike(Protocol):
    """Structural view of the canonical Understanding TypedClaim; not a second owner."""

    claim_id: str
    owner: Optional[str]
    subject: Optional[str]
    target: Optional[str]
    perspective: Optional[str]
    source: Optional[str]
    predicate: str
    object_value: Optional[str]
    polarity: str
    temporal_relation: str
    temporal_anchor_ref: Optional[str]
    dialogue_act: str
    claim_kind: str
    overall_interpretation_confidence: float
    structural_status: str
    interpretation_status: str


@dataclass(frozen=True)
class MemoryEvidence:
    """Read-only semantic projection of an existing Memory record."""

    memory_id: int
    owner: str
    subject: str
    predicate: str
    object_value: Optional[str]
    target: Optional[str] = None
    polarity: str = "POSITIVE"
    temporal_relation: str = "ATEMPORAL"
    temporal_anchor_ref: Optional[str] = None
    validity: ValidityStatus = ValidityStatus.VALID
    authority: Authority = Authority.BELIEF


class MemoryEvidencePort(Protocol):
    """Minimal read-only evidence port. No save/update/delete/supersede API by design."""

    def find_candidates(
        self,
        *,
        owner: str,
        subject: str,
        predicate: str,
    ) -> Sequence[MemoryEvidence]: ...


@dataclass(frozen=True)
class AuthorityResolveRequest:
    claim: TypedClaimLike
    trusted_world_truth: bool = False
    trusted_observation: bool = False
    derived_inference: bool = False
    source_reliability: Optional[float] = None

    def __post_init__(self) -> None:
        if self.source_reliability is not None and not 0.0 <= self.source_reliability <= 1.0:
            raise ValueError("source_reliability must be in [0,1]")


@dataclass(frozen=True)
class AuthorityResolution:
    claim_id: str
    authority: Optional[Authority]
    authority_resolution_confidence: Optional[float]
    source_reliability: Optional[float]
    status: AuthorityResolutionStatus
    contradicted_memory_id: Optional[int] = None
    candidate_memory_ids: tuple[int, ...] = field(default_factory=tuple)
    ambiguity_reasons: tuple[str, ...] = field(default_factory=tuple)
    reason_codes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.claim_id:
            raise ValueError("claim_id must not be blank")
        if self.authority_resolution_confidence is not None and not 0.0 <= self.authority_resolution_confidence <= 1.0:
            raise ValueError("authority_resolution_confidence must be in [0,1]")
        if self.source_reliability is not None and not 0.0 <= self.source_reliability <= 1.0:
            raise ValueError("source_reliability must be in [0,1]")
        if self.contradicted_memory_id is not None and self.contradicted_memory_id <= 0:
            raise ValueError("contradicted_memory_id must be a positive persistent ID")
