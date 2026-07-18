"""06-unified-crm-chat — CRM messaging channel infrastructure (F4).

Contains the email channel's send/ingest surfaces. Deliberately separate from
``services/api`` (the HTTP layer) — these modules talk to IMAP/SMTP, not to FastAPI.
"""
