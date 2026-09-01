#!/usr/bin/env python3
"""Compute cross-platform receipt digests from committed Git blob bytes.

Use this for evidence/receipt identity. It intentionally reads `REF:path` through
Git, so line endings are the committed blob bytes (normally LF), not the caller's
working-tree checkout bytes (which may be CRLF on Windows with core.autocrlf).
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys


def git_blob(ref: str, path: str) -> bytes:
    proc = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.decode("utf-8", errors="replace"))
    return proc.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="repository-relative paths to hash")
    ap.add_argument("--ref", default="HEAD", help="Git ref to read; default HEAD")
    ns = ap.parse_args()
    rows = []
    for path in ns.paths:
        blob = git_blob(ns.ref, path.replace('\\', '/'))
        rows.append({
            "path": path.replace('\\', '/'),
            "ref": ns.ref,
            "digest_algorithm": "sha256",
            "normalization_form": "git_committed_blob_bytes__not_worktree_checkout_bytes",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        })
    print(json.dumps({"schema": "microseed.receipt_blob_digest.v1", "entries": rows}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
