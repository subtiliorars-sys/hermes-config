#!/usr/bin/env python3
"""Audit public model catalogs without credentials or inference charges.

Catalog membership and advertised pricing are not inference/quality benchmarks.
Never modifies routing or a workstation's config.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import sys
import urllib.request

URLS = {
    'nous': 'https://inference-api.nousresearch.com/v1/models',
    'openrouter': 'https://openrouter.ai/api/v1/models',
}
ROOT = Path(__file__).resolve().parent


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'hermes-config-catalog-audit/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def advertised_free(model):
    prices = model.get('pricing') or {}
    try:
        return all(Decimal(str(prices[key])) == 0 for key in ('prompt', 'completion'))
    except (KeyError, InvalidOperation):
        return False


def routes(value, path=''):
    if isinstance(value, dict):
        model = value.get('model', value.get('default'))
        if isinstance(model, str) and 'provider' in value:
            yield path, value['provider'], model
        for key, item in value.items():
            yield from routes(item, f'{path}.{key}'.strip('.'))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from routes(item, f'{path}[{i}]')


def atomic_json(path, data):
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def refresh(output, policy, fetcher=fetch):
    output.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    report = {'checked_at': now.isoformat(), 'kind': 'catalog-audit-not-inference-benchmark',
              'providers': {}, 'configured_routes': []}
    failed = False
    for provider, url in URLS.items():
        try:
            data = fetcher(url)['data']
            if not isinstance(data, list) or not data:
                raise ValueError('Empty/invalid catalog; keep last known good report')
            models = []
            for m in data:
                if not isinstance(m.get('id'), str) or not m['id']:
                    raise ValueError('Model without an ID')
                models.append({'id': m['id'], 'advertised_free': advertised_free(m),
                               'pricing': m.get('pricing', {}),
                               'input_modalities': (m.get('architecture') or {}).get('input_modalities', []),
                               'supported_parameters': m.get('supported_parameters', []),
                               'context_length': m.get('context_length')})
            if len({m['id'] for m in models}) != len(models):
                raise ValueError('Duplicate catalog IDs')
            report['providers'][provider] = {'source': url, 'count': len(models),
                'free_count': sum(m['advertised_free'] for m in models),
                'models': sorted(models, key=lambda m: m['id'])}
        except Exception as exc:
            failed = True
            report['providers'][provider] = {'source': url, 'error': f'{type(exc).__name__}: {exc}'}
    for path, provider, model in routes(policy):
        source = report['providers'].get(provider)
        entry = {'path': path, 'provider': provider, 'model': model}
        if source is None:
            entry['status'] = 'local-not-checked'
        elif 'error' in source:
            entry['status'] = 'unknown-provider-fetch-failed'
        else:
            match = next((m for m in source['models'] if m['id'] == model), None)
            entry['status'] = 'listed' if match else 'missing-from-catalog'
            if match:
                entry['advertised_free'] = match['advertised_free']
                if path.startswith('auxiliary.') and not match['advertised_free']:
                    entry['warning'] = 'auxiliary-route-not-advertised-free'
        report['configured_routes'].append(entry)
    atomic_json(output / 'attempt.json', report)
    if not failed:
        atomic_json(output / 'latest.json', report)
    lines = ['# Model catalog audit', '', f"Checked: {report['checked_at']}", '',
             'Listing/pricing audit only; no inference calls, quality ranking, entitlement test or automatic routing changes.', '']
    for provider, value in report['providers'].items():
        lines.append(f"- {provider}: " + (value['error'] if 'error' in value else f"{value['count']} listed; {value['free_count']} advertised zero-cost text tokens"))
    lines += ['', '| Config path | Provider | Model | Status |', '|---|---|---|---|']
    for entry in report['configured_routes']:
        lines.append(f"| {entry['path']} | {entry['provider']} | {entry['model']} | {entry.get('warning', entry['status'])} |")
    (output / 'latest.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines[:9]))
    if failed:
        print('Fetch failure: latest.json preserved; attempt.json records failure.', file=sys.stderr)
    return int(failed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'reports')
    parser.add_argument('--if-due', action='store_true', help='Skip if last success was less than 72 hours ago')
    args = parser.parse_args()
    last = args.output / 'latest.json'
    if args.if_due and last.exists():
        checked = datetime.fromisoformat(json.loads(last.read_text(encoding='utf-8'))['checked_at'])
        if (datetime.now(timezone.utc) - checked).total_seconds() < 72 * 3600:
            print('Last successful audit is less than 72 hours old; skipped.')
            return 0
    policy = json.loads((ROOT / 'routing.json').read_text(encoding='utf-8'))['settings']
    return refresh(args.output, policy)


if __name__ == '__main__':
    sys.exit(main())
