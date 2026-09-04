from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE_ID="RAHL_ENGINEERING_CANONICAL_SOP_R4_2_2026-09-03"
ZIP_SHA="eb167543e9ceb2ae01449f421d2916e61b7dd924270ea2e83e3364c9d808ce9a"
def sha(b): return hashlib.sha256(b).hexdigest()
def fail(x): print("FAIL:",x); return 2
def main():
 zpath=ROOT/"governance"/(PACKAGE_ID+".zip"); exploded=ROOT/"governance"/PACKAGE_ID
 if not zpath.is_file() or sha(zpath.read_bytes())!=ZIP_SHA: return fail("sealed zip identity")
 with zipfile.ZipFile(zpath) as z:
  if z.testzip() is not None: return fail("zip crc")
  infos=[i for i in z.infolist() if not i.is_dir()]; prefix=PACKAGE_ID+"/"
  m=json.loads(z.read(prefix+"MANIFEST_SHA256.json").decode("utf-8")); declared=set(prefix+k for k in m["files"])|{prefix+"MANIFEST_SHA256.json"}
  if declared!=set(i.filename for i in infos): return fail("zip membership")
  for i in infos:
   if not i.filename.startswith(prefix): return fail("member prefix")
   rel=i.filename[len(prefix):]; b=z.read(i.filename); p=exploded/rel
   if not p.is_file() or p.read_bytes()!=b: return fail("exploded identity "+rel)
   if rel!="MANIFEST_SHA256.json":
    meta=m["files"].get(rel)
    if not meta or len(b)!=meta["bytes"] or sha(b)!=meta["sha256"]: return fail("manifest identity "+rel)
 adoption=(ROOT/"governance"/"RAHL_ENGINEERING_CANONICAL_SOP_R4_2_ADOPTION_2026-09-04.md").read_text(encoding="utf-8"); pointer=(ROOT/"GOVERNING_ENGINEERING_SOP.md").read_text(encoding="utf-8"); receipt=json.loads((ROOT/"governance"/"RAHL_ENGINEERING_CANONICAL_SOP_R4_2_SEMANTIC_READ_RECEIPT_2026-09-04.json").read_text(encoding="utf-8"))
 if ZIP_SHA not in adoption or ZIP_SHA not in pointer: return fail("authority hash binding")
 if receipt.get("semantic_read_gate")!="COMPLETE" or receipt.get("readable_outer_member_count")!=35: return fail("semantic receipt")
 print("PASS: R4.2 sealed ZIP hash/CRC, exact ZIP-to-exploded identity, manifest membership/hash, adoption bindings, semantic-read receipt")
 return 0
if __name__=="__main__": raise SystemExit(main())
