"""Schema dei record di memoria."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Authority(Enum):
    WORLD_TRUTH = "WORLD_TRUTH"
    OBSERVATION = "OBSERVATION"
    REPORT = "REPORT"
    BELIEF = "BELIEF"
    INFERENCE = "INFERENCE"


class MemoryCategory(Enum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    RELATIONSHIP = "RELATIONSHIP"
    GOAL = "GOAL"
    COMMITMENT = "COMMITMENT"
    EMOTION_STATE = "EMOTION_STATE"
    CORRECTION = "CORRECTION"
    IGNORE = "IGNORE"


class ValidityStatus(Enum):
    VALID = "valid"
    SUPERSEDED = "superseded"
    RETRACTED = "retracted"
    UNCERTAIN = "uncertain"


@dataclass
class MemoryRecord:
    id: Optional[int] = None
    owner: str = ""
    memory_type: str = ""
    category: MemoryCategory = MemoryCategory.IGNORE
    content: str = ""
    summary: str = ""
    actors: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    world_time: Optional[int] = None
    real_time: int = 0
    location_id: Optional[str] = None
    authority: Authority = Authority.BELIEF
    provenance: str = ""
    source_event_id: Optional[str] = None
    confidence: float = 0.5
    salience: float = 0.5
    emotional_weight: float = 0.0
    validity: ValidityStatus = ValidityStatus.VALID
    superseded_by: Optional[int] = None
    revision_of: Optional[int] = None
    revision_count: int = 0
    contradicts_memory_id: Optional[int] = None
    links: list[int] = field(default_factory=list)
    goal_id: Optional[str] = None
    created_at: int = 0
    updated_at: int = 0
    access_count: int = 0
    last_accessed: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "owner": self.owner,
            "memory_type": self.memory_type,
            "category": self.category.value,
            "content": self.content,
            "summary": self.summary,
            "actors": self.actors,
            "entities": self.entities,
            "world_time": self.world_time,
            "real_time": self.real_time,
            "location_id": self.location_id,
            "authority": self.authority.value,
            "provenance": self.provenance,
            "source_event_id": self.source_event_id,
            "confidence": self.confidence,
            "salience": self.salience,
            "emotional_weight": self.emotional_weight,
            "validity": self.validity.value,
            "superseded_by": self.superseded_by,
            "revision_of": self.revision_of,
            "revision_count": self.revision_count,
            "contradicts_memory_id": self.contradicts_memory_id,
            "links": self.links,
            "goal_id": self.goal_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        return cls(
            id=data.get("id"),
            owner=data.get("owner", ""),
            memory_type=data.get("memory_type", ""),
            category=MemoryCategory(data.get("category", "IGNORE")),
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            actors=data.get("actors", []),
            entities=data.get("entities", []),
            world_time=data.get("world_time"),
            real_time=data.get("real_time", 0),
            location_id=data.get("location_id"),
            authority=Authority(data.get("authority", "BELIEF")),
            provenance=data.get("provenance", ""),
            source_event_id=data.get("source_event_id"),
            confidence=data.get("confidence", 0.5),
            salience=data.get("salience", 0.5),
            emotional_weight=data.get("emotional_weight", 0.0),
            validity=ValidityStatus(data.get("validity", "valid")),
            superseded_by=data.get("superseded_by"),
            revision_of=data.get("revision_of"),
            revision_count=data.get("revision_count", 0),
            contradicts_memory_id=data.get("contradicts_memory_id"),
            links=data.get("links", []),
            goal_id=data.get("goal_id"),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed"),
        )
