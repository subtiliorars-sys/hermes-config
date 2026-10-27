import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def test_dry_run_does_not_modify_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            original = 'terminal:\n  cwd: keep-me\n'
            (home / 'config.yaml').write_text(original)
            result = subprocess.run([sys.executable, str(ROOT / 'install.py'), '--home', tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('DRY RUN', result.stdout)
            self.assertEqual((home / 'config.yaml').read_text(), original)
            self.assertEqual(list(home.iterdir()), [home / 'config.yaml'])


class CatalogTests(unittest.TestCase):
    def test_fetch_failure_preserves_last_good_report(self):
        sys.path.insert(0, str(ROOT))
        import catalog
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            prior = {'providers': {'nous': {'models': [{'id': 'old:free'}]}}}
            (output / 'latest.json').write_text(json.dumps(prior))
            def failed(url):
                raise OSError('offline')
            status = catalog.refresh(output, {'model': {'provider': 'nous', 'default': 'old:free'}}, failed)
            self.assertEqual(status, 1)
            self.assertEqual(json.loads((output / 'latest.json').read_text()), prior)
            self.assertIn('error', json.loads((output / 'attempt.json').read_text())['providers']['nous'])


if __name__ == '__main__':
    unittest.main()
