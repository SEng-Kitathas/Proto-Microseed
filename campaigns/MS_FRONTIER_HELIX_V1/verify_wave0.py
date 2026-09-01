import subprocess,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
canon='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
issues=[]
changed=subprocess.check_output(['git','diff','--name-only',canon+'..HEAD'],cwd=root,text=True).splitlines()
prod=[x for x in changed if x.startswith('microseed/')]
if prod: issues.append({'organism_delta':prod})
required=['campaigns/MS_FRONTIER_HELIX_V1/CAMPAIGN_CHARTER.md','campaigns/MS_FRONTIER_HELIX_V1/R3_1_PROCESS_CONTRACT.md','campaigns/MS_FRONTIER_HELIX_V1/PASS_SCHEMA.json','campaigns/MS_FRONTIER_HELIX_V1/LAUNCH_MANIFEST.json']
for p in required:
    if not (root/p).is_file(): issues.append('missing:'+p)
print(json.dumps({'status':'PASS' if not issues else 'FAIL','changed_files':changed,'organism_delta':prod,'issues':issues},indent=2))
sys.exit(0 if not issues else 1)
