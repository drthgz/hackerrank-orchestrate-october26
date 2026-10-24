"""Reviewed transcriptions of supplied screenshots, keyed by content hash.

These are evidence extraction artifacts, not prediction labels or case mappings.
Only visibly present fields are transcribed. Unknown categories/permissions stay
unresolved. An altered or new image has no cached interpretation and fails scope.
No runtime OCR or model is used. See docs/image_review.md for review limits.
"""
import hashlib
import re
from dataclasses import replace
from functools import lru_cache
from .models import AuditError, timestamp

REVIEWED = {'18b95c1bd8b8956e40216df935498a9f3c181ea2a69b5cd6d3c0841a816d5557': {'rows': [('export_service',
                                                                                'export_1260',
                                                                                'USER_EXPORT',
                                                                                {'download_available': True,
                                                                                 'owner_email': 'ingrid.dahl@outlook.com'})],
                                                                      'selectors': ['ingrid.dahl@outlook.com',
                                                                                    'marcus.lee@northstar.shop',
                                                                                    'sara.kim@northstar.shop',
                                                                                    'daniel.park@northstar.shop'],
                                                                      'source_name': 'customer_export_console_20260618.png'},
 '2c246aa5843bec609b9ddfdf1154cd81e0fd61996f83954735e9856e48c18bf3': {'rows': [],
                                                                      'selectors': ['areed1433@gmail.com',
                                                                                    'bluepeakco@outlook.com',
                                                                                    'miller.logistics@company.com',
                                                                                    'summit-retail@company.com'],
                                                                      'source_name': 'backup_restore_console_20260429.png',
                                                                      'unresolved': 'Archive presence does '
                                                                                    'not establish restore '
                                                                                    'authorization'},
 '4e4cb259bc2010b622b0c53fe5872258f994fefc23452a83bb27473758693484': {'rows': [('analytics_platform',
                                                                                'analytics_7438',
                                                                                'ANALYTICS_PROFILE',
                                                                                {'email': 'darwish.omar@icloud.com',
                                                                                 'identifier_exposure': True,
                                                                                 'user_id': 'user_20'})],
                                                                      'selectors': ['user_20',
                                                                                    'darwish.omar@icloud.com'],
                                                                      'source_name': 'analytics_profile_view_20260713.png'},
 '51fa0e6a38f8fa3629ba1b0d0b90b4ed139715956b97bfd09a6f1a6232c15df5': {'rows': [('marketing_platform',
                                                                                'marketing_001',
                                                                                'MARKETING_PROFILE',
                                                                                {'email': 's.j.park@naver.com',
                                                                                 'phone': '+82 '
                                                                                          '10-5837-9451'})],
                                                                      'selectors': ['s.j.park@naver.com'],
                                                                      'source_name': 'marketing_profile_console.png'},
 '542b7aec17e6b2f38827896e7eb52c70e4bfaaca22433621be1f80f54884e944': {'rows': [('support_platform',
                                                                                'support_1034',
                                                                                'SUPPORT_MESSAGE',
                                                                                {'identifier_exposure': True,
                                                                                 'requester_email': 'kagyeman8947@fastmail.com',
                                                                                 'requester_name': 'Kofi '
                                                                                                   'Agyeman',
                                                                                 'shared_context': True})],
                                                                      'selectors': ['kagyeman8947@fastmail.com'],
                                                                      'source_name': 'support_ticket_console_20260524.png'},
 '68c28a72afd6ed184d5990d15c543f8a516face204f0360f732755a8a63c28be': {'rows': [],
                                                                      'selectors': ['user_17'],
                                                                      'source_name': 'deleted_account_reference_20260310.png',
                                                                      'unresolved': 'Registry links lack an '
                                                                                    'explicit '
                                                                                    'deleted-account state '
                                                                                    'and policy resource ID; '
                                                                                    'displayed update after '
                                                                                    'manifest capture'},
 '75afdb0ae53a4510c83399a70d88073cb4fb2747454095756e4ddad1a8c70605': {'rows': [('search_service',
                                                                                'search_428',
                                                                                'SEARCH_INDEX_ENTRY',
                                                                                {'customer_reference': 'user_13',
                                                                                 'email': 'g.silva76@gmail.com',
                                                                                 'indexed_at': '2026-09-01T05:58:21Z'}),
                                                                               ('search_service',
                                                                                'search_1874',
                                                                                'SEARCH_INDEX_ENTRY',
                                                                                {'email': 'g.silva76.jr@gmail.com'})],
                                                                      'selectors': ['user_13',
                                                                                    'g.silva76@gmail.com',
                                                                                    'g.silva76.jr@gmail.com'],
                                                                      'source_name': 'search_index_inspector_20260901.png'},
 '96e9a191380c29b9e0ab997007268c4cd6353cb6721ebd1ed4a32599d8d37e04': {'filenames': ['delivery_confirmation_19.pdf',
                                                                                    'delivery_confirmation_20.pdf',
                                                                                    'return_label_4821.pdf',
                                                                                    'return_label_4876.pdf',
                                                                                    'invoice_NS-10493.pdf',
                                                                                    'parcel_damage_7713.jpg',
                                                                                    'customer_export_2026-02-10.zip',
                                                                                    'customer_export_2026-02-12.zip'],
                                                                      'attachment_folder': 'support-attachments',
                                                                      'rows': [],
                                                                      'selectors': [],
                                                                      'source_name': 'object_storage_browser_20260213.png',
                                                                      'unresolved': 'Object listing lacks '
                                                                                    'direct subject identity '
                                                                                    'and stable object ID'},
 'ca59f693f4e7002466b3fdeaf1bb6763618770963dd811b60003772d07b4b03b': {'rows': [('security_service',
                                                                                'audit_record_003',
                                                                                'SECURITY_AUDIT_LOG',
                                                                                {'event_recorded_at': '2026-08-25T04:03:00Z',
                                                                                 'subject_reference': 'user_03'})],
                                                                      'selectors': ['user_03'],
                                                                      'source_name': 'security_audit_explorer_20260905.png'},
 'd5c32ca5b6e1a2b4bbe9f5d41835ef1fd5d4f7061dab9067a4f9f88cea3c1861': {'rows': [('account_service',
                                                                                'account_5762',
                                                                                'USER_PROFILE',
                                                                                {'account_status': 'ACTIVE',
                                                                                 'email': 'haruka.s1838@zoho.com',
                                                                                 'phone': '+81 90 7610 2507',
                                                                                 'user_id': 'user_11'})],
                                                                      'selectors': ['user_11',
                                                                                    'haruka.s1838@zoho.com'],
                                                                      'source_name': 'account_admin_console_20260926.png'},
 'e81fabc93ea1b5f4c918d934cdb2bea05d61737adfcc29f281494f5d8ec46355': {'rows': [('integration_service',
                                                                                'data_flow_1121',
                                                                                'DATA_FLOW',
                                                                                {'customer_email': 'jain.aditi@gmail.com',
                                                                                 'enabled': True}),
                                                                               ('integration_service',
                                                                                'data_flow_9846',
                                                                                'DATA_FLOW',
                                                                                {'customer_email': 'lucia-torres@gmail.com',
                                                                                 'enabled': True})],
                                                                      'selectors': ['jain.aditi@gmail.com',
                                                                                    'lucia-torres@gmail.com'],
                                                                      'source_name': 'connector_management_console_20260807.png'}}


@lru_cache(maxsize=128)
def _review(path, size, modified):
    return REVIEWED.get(hashlib.sha256(path.read_bytes()).hexdigest())


def review(file):
    stat = file.path.stat()
    return _review(file.path, stat.st_size, stat.st_mtime_ns)


def read_image(file):
    from .evidence import observation
    data = review(file)
    if not data:
        return ()
    return tuple(observation(file, system, resource, category,
                 dict(facts, _source_origin=file.origin, _source_path=str(file.path),
                      _image_region='selected detail/header or explicitly linked table row',
                      _extraction='reviewed screenshot transcription'),
                 file.captured_at, source='image:reviewed-fields')
                 for system, resource, category, facts in data['rows'])


def catalog_attachment_observations(file, subject, activity, cutoff):
    """Join a visible attachment filename to explicit catalog ownership.

    Catalog metadata establishes identity and policy ownership, never presence.
    The hash-bound screenshot establishes presence in a support-attachment folder.
    Both witnesses must be available by the cutoff; neither supplies guessed IDs.
    """
    from .evidence import linked_facts, observation
    data = review(file)
    if not data or data.get('attachment_folder') != 'support-attachments':
        return ()
    result = []
    pattern = re.compile(r'^Attachment catalog confirmed (\S+) \(([^)]+)\) belongs only to (\S+) and (\S+); no other subject is linked\.$')
    for event in activity:
        available = timestamp(event['event_time'])
        if event['event_type'] != 'LINK_RESOURCE_IDENTITY' or available > cutoff:
            continue
        match = pattern.fullmatch(event.get('details', ''))
        if not match:
            continue
        resource, filename, email, user = match.groups()
        facts = dict(owner_email=email, subject_reference=user, belongs_only_to_subject=True,
                     attachment_name=filename, _policy_evidence={'belongs_only_to_subject': event['activity_id']},
                     _lineage_evidence=event['activity_id'])
        if (resource != event['resource_id'] or filename not in data.get('filenames', ())
                or not linked_facts(facts, subject)):
            continue
        o = observation(file, event['target_system'], resource, 'SUPPORT_ATTACHMENT', facts,
                        file.captured_at, source='image:attachment-list+catalog-ownership')
        result.append(replace(o, available_at=max(file.captured_at, available)))
    return tuple(result)
