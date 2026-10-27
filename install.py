#!/usr/bin/env python3
"""Selectively apply versioned model routing using Hermes' supported config CLI."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent
ALLOWED = {'model', 'fallback_providers', 'auxiliary', 'delegation', 'moa'}
FORBIDDEN = {'api_key', 'token', 'access_token', 'refresh_token', 'password', 'secret'}


def validate(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN:
                raise ValueError(f'Credential field forbidden: {key}')
            validate(item)
    elif isinstance(value, list):
        for item in value:
            validate(item)


def settings():
    policy = json.loads((ROOT / 'routing.json').read_text(encoding='utf-8'))
    if policy['schema_version'] != 1 or not set(policy['settings']) <= ALLOWED:
        raise ValueError('Unsupported policy schema or settings')
    validate(policy['settings'])
    return deepcopy(policy['settings'])


def ollama_models():
    try:
        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=3) as response:
            return {m['name'] for m in json.load(response)['models']}
    except (OSError, ValueError, KeyError):
        return set()


def portable(value, available):
    if isinstance(value, dict):
        if value.get('base_url') == 'http://localhost:11434/v1' and value.get('model') not in available:
            return None
        result = {k: portable(v, available) for k, v in value.items()}
        if 'aggregator' in result and result['aggregator'] is None:
            return None
        return {k: v for k, v in result.items() if v is not None}
    if isinstance(value, list):
        return [v for item in value if (v := portable(item, available)) is not None]
    return value


def updates(policy):
    # Preserve unrelated tasks, presets and machine-specific sections.
    for section, value in policy.items():
        if section == 'fallback_providers':
            yield section, value
        elif section == 'moa':
            for key, item in value.items():
                if key == 'presets':
                    for name, preset in item.items():
                        yield f'moa.presets.{name}', preset
                else:
                    yield f'moa.{key}', item
        else:
            for key, item in value.items():
                yield f'{section}.{key}', item


def matches(actual, expected):
    # Hermes config get includes built-in defaults alongside saved values.
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and matches(actual[k], v) for k, v in expected.items())
    return actual == expected


def run(cli, env, *args):
    result = subprocess.run([cli, 'config', *args], env=env, capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, help='Explicit target Hermes home (otherwise ask Hermes)')
    parser.add_argument('--apply', action='store_true', help='Write; default is a dry run')
    parser.add_argument('--no-local', action='store_true', help='Exclude all local Ollama routes')
    args = parser.parse_args()
    cli = shutil.which('hermes')
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    if args.home:
        env['HERMES_HOME'] = str(args.home.expanduser().resolve())
    if args.home:
        home = args.home.expanduser().resolve()
    elif cli:
        home = Path(run(cli, env, 'path')).parent
    else:
        raise RuntimeError('Install Hermes first, or use --home for a dry run.')
    policy = portable(settings(), set() if args.no_local else ollama_models())
    plan = list(updates(policy))
    print(('APPLY' if args.apply else 'DRY RUN') + f': {home}')
    if not args.apply:
        for key, value in plan:
            print(f'  {key} = {json.dumps(value)}')
        print('No files changed. Use --apply to install. Authenticate separately: hermes auth add nous')
        return 0
    if not cli:
        raise RuntimeError('hermes executable not on PATH')
    target = home / 'config.yaml'
    current = Path(run(cli, env, 'path')).resolve()
    if current != target.resolve():
        raise RuntimeError('Hermes resolved a different config path; refusing to write')
    # Read every target before writing. This also checks JSON-capable CLI compatibility.
    changes = []
    for key, value in plan:
        try:
            existing = json.loads(run(cli, env, 'get', key, '--json'))
        except RuntimeError as exc:
            if 'Config key not set:' not in str(exc):
                raise
            existing = object()
        if not matches(existing, value):
            changes.append((key, value))
    if not changes:
        print('Already matches this policy; no writes.')
        return 0
    home.mkdir(parents=True, exist_ok=True)
    backup = None
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = home / f'config.yaml.before-routing-{stamp}'
        shutil.copy2(target, backup)
        print(f'Backup: {backup}')
    try:
        for key, value in changes:
            run(cli, env, 'set', key, value if isinstance(value, str) else json.dumps(value))
        for key, value in plan:
            if not matches(json.loads(run(cli, env, 'get', key, '--json')), value):
                raise RuntimeError(f'Read-back mismatch: {key}')
    except Exception:
        if backup:
            shutil.copy2(backup, target)
            print(f'Restored original config from {backup}', file=sys.stderr)
        elif target.exists():
            target.unlink()
        raise
    print(f'Verified {len(plan)} routing settings. Restart Hermes to use them.')
    print('Credentials were not copied. Authenticate on this device: hermes auth add nous')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
