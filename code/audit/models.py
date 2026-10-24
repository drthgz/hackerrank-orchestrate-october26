from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


class AuditError(ValueError):
    """Invalid input or an unsupported case: never substitute a guessed answer."""


def timestamp(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError) as exc:
        raise AuditError(f'Invalid timestamp: {value!r}') from exc
    if result.tzinfo is None:
        raise AuditError('Timestamp must include a timezone')
    return result


@dataclass(frozen=True)
class Request:
    case_id: str
    email: str
    requested_at: datetime
    reported_status: str
    reported_at: datetime
    audit_at: datetime
    request_text: str


@dataclass(frozen=True)
class EvidenceFile:
    file_id: str
    path: Path
    origin: str
    captured_at: datetime


@dataclass(frozen=True)
class Subject:
    user_id: str
    # Historical values are retained for discovery; future aliases are excluded.
    aliases: dict[str, frozenset[str]]
    provenance: tuple[str, ...]
    # Names are scanned for residual PII, never used as identity join keys.
    names: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Observation:
    system_id: str
    resource_id: str
    category: str
    copy_id: str
    present: bool
    observed_at: datetime
    updated_at: datetime | None
    evidence_id: str
    available_at: datetime
    source_table: str
    identifiers: tuple[tuple[str, str], ...]
    facts: dict = field(default_factory=dict)
    subject_id: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    observation: Observation
    action: str
    rule_id: str
    compliant: bool = False
    verify_operation: str = "VERIFY_RECORD_ABSENT"
    final_state: str = "ABSENT"


@dataclass(frozen=True)
class Step:
    step_no: int
    phase: str
    system_id: str
    resource_id: str
    operation: str
    state: str
    evidence_id: str


@dataclass(frozen=True)
class Result:
    case_id: str
    deletion_status: str
    steps: tuple[Step, ...]
