# Screenshot evidence review

All eleven supplied screenshots were visually inspected in full. The reviewed
transcriptions in `code/audit/reviewed_images.py` are keyed by SHA-256 of the
original image bytes, not case IDs, expected decisions or sample labels. They
contain only visible evidence fields. New or changed images remain unprocessed.
This is a corpus-specific evidence extraction cache, not a general OCR engine.

The cache supplies account/profile identity, selected search documents, continuous
connector selectors, an attributable analytics profile, a ready export, shared
support conversation, a security record and a live marketing profile. It preserves
manifest file ID/capture, origin/path and the inspected region in observations.
Source subject selectors are also retained for per-subject evidence scope.

Limits observed during review:

- The registry shows user_17 and business references, not an explicit deleted-account
  policy resource ID or direct identifier fields; its displayed update is later
  than manifest capture. It cannot independently prove compliant tombstoning.
- The backup console shows an archive but not restore authorization. Presence
  alone is insufficient for a restore-risk finding or blocked-restore verification.
- The object browser lists filenames in a support-attachments folder but no
  direct subject or stable object ID. An exact filename/resource/sole-owner join
  to an admissible catalog event now supplies ownership and lineage. The listing
  supplies presence; the catalog supplies metadata. Both witnesses and their
  availability times are retained. Unlisted filenames or future events cannot join.
- Search execution time is fourteen seconds after manifest capture; only visible
  indexed records with earlier indexed times are transcribed, not a later query
  state or inferred absence. Customer export rows with displayed future dates
  relative to capture are not used. The selected ready export predates capture.
- The marketing screenshot and later catalog claim disagree on owner for the same
  resource ID. The catalog claim does not overwrite the visible screenshot owner.
- Displayed linked resources and activity timelines are not automatically expanded
  into extra policy resources without a grounded category/state/ownership link.

Best-effort mode uses these reviewed fields; strict mode keeps its existing
unprocessed-image diagnostic behavior. Known reviewed media for unrelated subjects
no longer blocks every COMPLETE case globally. Related unresolved media, unknown
images, missing policy facts and state-changing claims after readback still block
COMPLETE. Metadata-only identity-link events do not mutate resource state.
