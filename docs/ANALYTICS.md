# Analytics

Public pages may load the configured Umami tracker. Channel pages never load
analytics. Query strings, fragments and referrer paths are stripped; Do Not Track
and Global Privacy Control are respected. No private key or message goes to page
analytics. The operational `/metrics` endpoint requires a configured bearer token.
It exposes aggregate route/tool counts, durations, retained channels/messages,
storage and limits. Labels never contain channel IDs, member names or message text.

`scripts/business_report.py` opens an existing database read-only. Channel counts
are anonymous activity, including maintainer tests; they cannot prove distinct
humans, adoption or retention. Retained messages can disappear on expiry/deletion,
so these are not lifetime counts. Any legacy billing data is a historical ledger,
not current provider revenue. Reconcile real payments with the provider, excluding
owner, sandbox, refunds and test activity. Never call clones or created channels
“users” without independent evidence.
