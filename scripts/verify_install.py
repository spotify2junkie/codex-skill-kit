#!/usr/bin/env python3
"""Install the marketplace into a disposable CODEX_HOME; no user auth is copied."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {'pstack-for-codex': 45, 'lark-work': 28, 'reading-notes': 3}


def run(args, env, cwd=None):
    result = subprocess.run(args, env=env, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{args[0:3]} failed: {result.stderr[-3000:]}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=str(ROOT), help='Local marketplace root or GitHub owner/repo')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='codex-skill-kit-') as folder:
        temporary = Path(folder)
        codex_home = temporary / 'codex-home'
        codex_home.mkdir()
        env = {**os.environ, 'CODEX_HOME': str(codex_home)}
        version = run(['codex', '--version'], env).strip()
        market = json.loads(run(['codex', 'plugin', 'marketplace', 'add', args.source, '--json'], env))
        assert market['marketplaceName'] == 'personal', market
        installed = {}
        for name, count in COUNTS.items():
            data = json.loads(run(['codex', 'plugin', 'add', f'{name}@personal', '--json'], env))
            installed[name] = Path(data['installedPath'])
            assert len(list(installed[name].glob('skills/*/SKILL.md'))) == count, name
            source = ROOT / 'plugins' / name
            for item in source.rglob('*'):
                if not item.is_file() or any(x in item.parts for x in ['node_modules', '.git', '__pycache__']):
                    continue
                target = installed[name] / item.relative_to(source)
                assert target.is_file() and target.read_bytes() == item.read_bytes(), str(item.relative_to(ROOT))
        # Prove root-relative agent templates survive packaging; write only to disposable roots.
        project = temporary / 'project'
        user = temporary / 'user'
        project.mkdir()
        user.mkdir()
        helper = installed['pstack-for-codex'] / 'skills/setup-pstack/scripts/manage-agents.mjs'
        cmd = ['node', str(helper), 'install', '--scope', 'project', '--project-root', str(project), '--user-home', str(user)]
        run(cmd, env)
        before = {p.name: p.read_bytes() for p in (project / '.codex/agents').glob('*.toml')}
        assert len(before) == 2
        run(cmd, env)
        assert before == {p.name: p.read_bytes() for p in (project / '.codex/agents').glob('*.toml')}
        assert all(b'{{PROMPT}}' not in value and b'{{MODEL_CONFIG}}' not in value for value in before.values())
        # Validate the installed reading helper with a real text-only fixture.
        note = temporary / 'note.md'
        note.write_text('# Paper\n\n## 01. Example\n\nSource: https://example.com/paper\n')
        verifier = installed['reading-notes'] / 'skills/obsidian-paper-note/scripts/verify_note_bundle.py'
        verify_cmd = ['python3', str(verifier), '--note', str(note), '--vault-root', str(temporary), '--expected-articles', '1', '--expected-pdfs', '0']
        assert json.loads(run(verify_cmd, env))['status'] == 'PASS'
        note.write_text(note.read_text() + '\n![[missing.png]]\n')
        missing = subprocess.run(verify_cmd, env=env, text=True, capture_output=True)
        assert missing.returncode == 1 and 'missing embed' in missing.stdout
        listing = json.loads(run(['codex', 'plugin', 'list', '--json'], env))
        assert {item['pluginId'] for item in listing['installed']} == {f'{name}@personal' for name in COUNTS}
        assert all(item['installed'] and item['enabled'] for item in listing['installed'])
        print(json.dumps({'result': 'PASS', 'codex': version, 'skill_counts': COUNTS,
                          'installed_files_match_source': True,
                          'agent_template_install_and_repeat': 'PASS',
                          'reading_verifier_valid_note_and_missing_embed': 'PASS',
                          'runtime_skill_discovery': 'Requires a new Codex task; not exercised',
                          'lark_auth': 'Not exercised; user login required'}, ensure_ascii=False, indent=2))
        for name in COUNTS:
            run(['codex', 'plugin', 'remove', f'{name}@personal'], env)
        run(['codex', 'plugin', 'marketplace', 'remove', 'personal'], env)


if __name__ == '__main__':
    main()
