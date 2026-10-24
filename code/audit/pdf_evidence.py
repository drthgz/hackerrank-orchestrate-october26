"""Selectable-text business documents. No OCR, model calls, or label access.

Document metadata is not a resource observation unless its text explicitly names
that resource. Order-level retention supplements only an exact subject/order join.
"""
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

from .models import AuditError


@dataclass(frozen=True)
class PDFDocument:
    pages: tuple[str, ...]
    observations: tuple
    retention: tuple[dict, ...]
    understood: bool


def business_time(text, label):
    # The journal table splits the hour and minute into different columns.
    match = re.search(label + r'\s+(\d{2} [A-Za-z]{3} \d{4}) (\d{2})\s+(\d{2}) UTC', text, re.I)
    if not match:
        raise AuditError('PDF missing explicit ' + label + ' timestamp')
    return datetime.strptime(' '.join(match.groups()), '%d %b %Y %H %M').replace(tzinfo=timezone.utc)


@lru_cache(maxsize=128)
def _pages(path, size, modified):
    try:
        run = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True,
                             text=True, check=True, timeout=30)
    except subprocess.CalledProcessError:
        return ('',)  # Malformed/unreadable PDF remains an unprocessed scope.
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditError('PDF text extraction requires Poppler pdftotext') from exc
    return tuple(run.stdout.rstrip('\f\n').split('\f'))


def read_pdf(file):
    from .evidence import observation
    stat = file.path.stat()
    pages = _pages(file.path, stat.st_size, stat.st_mtime_ns)
    text = '\n'.join(pages)
    observations, retention = [], []
    provenance = dict(_pdf_pages=tuple(range(1, len(pages) + 1)),
                      _source_origin=file.origin, _source_path=str(file.path))
    if 'COMPLIANCE JOURNAL - SIGNED RECORD EXTRACT' in text:
        resource = re.search(r'Event reference\s+(\S+)', text)
        subject = re.search(r'subject reference\s+(\S+)', text)
        if not resource or not subject:
            raise AuditError('PDF journal lacks resource/subject reference')
        issued = business_time(text, 'issued')
        recorded = business_time(text, 'recorded')
        end = business_time(text, 'retain until')
        if recorded > issued:
            raise AuditError('PDF event occurs after journal issue')
        facts = dict(provenance, subject_reference=subject[1], retention_until=end.isoformat(),
                     event_recorded_at=recorded.isoformat())
        observations.append(observation(file, 'security_service', resource[1], 'SECURITY_AUDIT_LOG',
                                        facts, issued, source='pdf:page:1:journal'))
    elif 'DELIVERY ADDRESS CORRECTION REQUEST' in text:
        resource = re.search(r'Support reference\s+[^\n/]+/\s*(\S+)', text)
        email = re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
        upload = re.search(r'\buploader\s+customer\b', text, re.I)
        attachment = re.search(r'\bfile\s+(\S+\.pdf)\b', text, re.I)
        if not resource or len(set(email)) != 1 or not upload or not attachment:
            raise AuditError('PDF attachment ownership/resource link is incomplete')
        observed = business_time(text, 'captured')
        submitted = business_time(text, 'submitted')
        if submitted > observed:
            raise AuditError('PDF submission occurs after capture')
        facts = dict(provenance, owner_email=email[0], belongs_only_to_subject=True,
                     attachment_name=attachment[1], submitted_at=submitted.isoformat())
        observations.append(observation(file, 'support_platform', resource[1], 'SUPPORT_ATTACHMENT',
                                        facts, observed, source='pdf:pages:1-2:customer-upload'))
    elif 'DISPUTED ORDERS AND TAX RECORDS REGISTER' in text:
        for page_no, page in enumerate(pages, 1):
            for match in re.finditer(r'(ORD-[\w-]+)\s*\|\s*(\S+)\s*\|\s*([^|]+)\|[^\n]+?Retain until (\d{2} [A-Za-z]{3} \d{4})', page):
                order, subject, reason, end = match.groups()
                retention.append(dict(provenance, _pdf_pages=(page_no,), order_reference=order,
                                      subject_reference=subject, retention_reason=reason.strip(),
                                      retained_until=datetime.strptime(end, '%d %b %Y').replace(tzinfo=timezone.utc).isoformat(),
                                      evidence_id=file.file_id, observed_at=file.captured_at))
    understood = bool(observations or retention)
    # Customer statements establish business identity/order context only, not a
    # policy resource, legal hold or retention duration.
    return PDFDocument(pages, tuple(observations), tuple(retention), understood)


def supplement_retention(observations, documents, subject, cutoff):
    from dataclasses import replace
    result = []
    for o in observations:
        facts = dict(o.facts)
        matches = [row for doc in documents for row in doc.retention
                   if row['subject_reference'] == subject.user_id
                   and row['order_reference'] == facts.get('order_reference')
                   and row['observed_at'] <= o.observed_at <= cutoff]
        if o.category == 'LEGAL_HOLD_RECORD' and matches:
            row = max(matches, key=lambda r: r['observed_at'])
            if 'retained_until' not in facts:
                facts['retained_until'] = row['retained_until']
                if facts.get('legal_hold_active') is None and row['retention_reason'].lower() in {'card dispute', 'chargeback', 'tax correction', 'tax record'}:
                    facts['legal_hold_active'] = True
                facts['_policy_evidence'] = dict(facts.get('_policy_evidence', {}), retained_until=row['evidence_id'])
                if facts.get('legal_hold_active') is True:
                    facts['_policy_evidence']['legal_hold_active'] = row['evidence_id']
                facts['_policy_pdf_pages'] = row['_pdf_pages']
        result.append(replace(o, facts=facts))
    return result
