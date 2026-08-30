# Recovery and Restore

## Original server available
Use project id `protoagi_microseed_reincarnation_20260827`; rehydrate current state; compare live repo HEAD/tree/status to `source/GIT_STATE.json`; exact match permits resuming MS1945, divergence requires RECOVERY localization first.

## Offline Git restore
PowerShell: `./source/RESTORE_REPO.ps1`  
POSIX: `sh ./source/RESTORE_REPO.sh`

Expected HEAD `18696b19bf090ace01e6a4d2226b7b88609a3ad0` and tree `de240e3424debf7d170bf29d24dc3c564518c753`. The bundle was independently cloned and checked during packaging.

## Public fallback
GitHub is `https://github.com/SEng-Kitathas/Proto-Microseed.git`, but public remote remains MS1939 `3473834...`; public clone alone does not contain MS1940–MS1944.

## Evidence map
- `state/`: active state/doctrine/revisit/trace
- `continuity/`: Live Shadow + Design Thread Stream
- `notes/maintenance/`: durable milestone evidence
- `evidence/project_reports/`: project validation reports
- `evidence/repo_reports/`: repo-local reports
- `evidence/execution_logs/`: cited recent job logs still present
- `historical/`: older hand-stitched recovery archaeology
