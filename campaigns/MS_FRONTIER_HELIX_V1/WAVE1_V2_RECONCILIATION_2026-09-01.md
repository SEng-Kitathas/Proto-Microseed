# Wave-1 V2 Reconciliation — 2026-09-01

This append-only receipt reconciles the actual admitted pass files against branch heads and `RESEARCH_STOP.json`. `ARM_CLOSEOUT.json` / HELIX summaries from earlier runtime phases may be stale and are not authoritative for resume when counts differ.

Resume authority is: exact branch HEAD + admitted `Pxx.json` chain + pass-bundle SHA-256 + latest `RESEARCH_STOP.json`.

No arm has promotion authority and all arms have zero `microseed/` delta from canon.
