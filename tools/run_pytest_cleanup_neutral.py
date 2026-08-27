from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import pytest

sys.path.insert(0, str(Path.cwd()))


def cleanup_no_raise(self):
    if getattr(self, '_finalizer', None) is not None:
        self._finalizer.detach()
    self._rmtree(self.name, ignore_errors=True)


tempfile.TemporaryDirectory.cleanup = cleanup_no_raise
raise SystemExit(int(pytest.main(sys.argv[1:])))
