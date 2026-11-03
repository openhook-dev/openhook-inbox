"""Preview or apply a reversible local skill and project-hook setup.

No credentials are created, copied or printed. Unrelated hooks are preserved.
Codex hook trust must be reviewed through the runtime, never bypassed here.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from openhook.channel_listener import validate_origin


def skill_matches(source, target):
    if not target.is_dir() or target.is_symlink():
        return False
    files = lambda directory: {p.relative_to(directory): p.read_bytes()
                               for p in directory.rglob('*') if p.is_file()}
    return files(source) == files(target)


def setup(project, skills, backups, apply=False, origin='https://openhook.dev', claude_skills=None, codex_socket=None):
    project, skills, backups = (Path(p).expanduser().resolve() for p in (project, skills, backups))
    python = project / '.venv/bin/python'
    if not python.is_file():
        raise ValueError('Run uv sync --frozen --extra dev in the project first.')
    key_file = project / '.openhook/participant.key'
    origin = validate_origin(origin)
    files = []
    for path in (project / '.codex/hooks.json', project / '.claude/settings.local.json'):
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError('Refusing to replace a symlinked hook configuration.')
        data = json.loads(path.read_text()) if path.exists() else {}
        runtime = 'codex' if path.parent.name == '.codex' else 'claude'
        prefix = [str(python), '-m', 'openhook.agent_background', 'hook']
        old_prefix = [str(python), '-m', 'openhook.channel_inbox', 'hook']
        command = shlex.join([*prefix, '--runtime', runtime, '--token-file', str(key_file), '--url', origin])
        if runtime == 'codex' and codex_socket is not None:
            command += ' --socket ' + shlex.quote(str(Path(codex_socket).expanduser().absolute()))
        definition = {'type': 'command', 'command': command, 'timeout': 6 if runtime == 'codex' else 2592000}
        if runtime == 'claude':
            definition['asyncRewake'] = True
        for event in ('SessionStart', 'UserPromptSubmit', 'Stop'):
            groups = data.setdefault('hooks', {}).setdefault(event, [])
            owned = [h for group in groups for h in group.get('hooks', [])
                     if shlex.split(h.get('command', ''))[:4] in (prefix, old_prefix)]
            if owned:
                for hook in owned:
                    hook.update(definition)
            else:
                groups.append({'hooks': [dict(definition)]})
        contents = json.dumps(data, indent=2) + '\n'
        if not path.exists() or path.read_text() != contents:
            files.append((path, contents))
    source, target = ROOT / 'skills/openhook', skills / 'openhook'
    legacy = skills / 'openhook-webhook-listener'
    if target.is_symlink() or legacy.is_symlink():
        raise ValueError('Refusing to replace symlinked skills; review their targets first.')
    replace_skill, archive_legacy = not skill_matches(source, target), legacy.exists()
    links, legacy_link = [], None
    if claude_skills is not None:
        claude_skills = Path(claude_skills).expanduser().resolve()
        link = claude_skills / 'openhook'
        if link.is_symlink() and link.resolve() == target:
            pass
        elif link.exists() or link.is_symlink():
            raise ValueError('An unrelated Claude Openhook skill already exists; review it before replacement.')
        else:
            links.append(link)
        old_link = claude_skills / legacy.name
        if old_link.is_symlink() and old_link.resolve() == legacy:
            legacy_link = old_link
        elif old_link.exists() or old_link.is_symlink():
            raise ValueError('An unrelated legacy Claude skill exists; review it before replacement.')
    plan = {'apply': apply, 'project_hook_files': [str(path) for path, _ in files],
            'install_skill': str(target) if replace_skill else None,
            'archive_legacy_skill': str(legacy) if archive_legacy else None,
            'claude_skill_links': [str(link) for link in links],
            'archive_legacy_claude_link': str(legacy_link) if legacy_link else None,
            'member_key_file': str(key_file), 'member_key_configured': key_file.is_file(),
            'listening': False, 'mode': 'Background long-poll; Codex tool output or Claude asyncRewake',
            'codex_hook_trust': 'Review new hooks in /hooks or Settings > Hooks; this script does not grant trust'}
    if not apply or not (files or replace_skill or archive_legacy or links or legacy_link):
        return plan
    backup = backups / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])
    backup.mkdir(mode=0o700, parents=True)
    os.chmod(backups, 0o700)
    for path, contents in files:
        if path.exists():
            saved = backup / (path.parent.name + '-' + path.name)
            shutil.copyfile(path, saved)
            saved.chmod(0o600)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as temporary:
            temporary.write(contents)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary.name, path)
    if replace_skill:
        skills.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.rename(backup / 'openhook')
        shutil.copytree(source, target)
    if archive_legacy:
        legacy.rename(backup / legacy.name)
    if legacy_link:
        legacy_link.rename(backup / 'claude-legacy-skill-link')
    for link in links:
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(target, link.parent), target_is_directory=True)
    plan['backup_directory'] = str(backup)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply the previewed setup and retain backups.')
    parser.add_argument('--url', default='https://openhook.dev', help='Trusted Openhook origin for these project hooks.')
    parser.add_argument('--codex-socket', type=Path, help='Existing owned Codex app-server Unix socket; defaults to the control socket.')
    parser.add_argument('--project', type=Path, default=ROOT)
    parser.add_argument('--skills-directory', type=Path, default=Path.home() / '.agents/skills')
    parser.add_argument('--claude-skills-directory', type=Path, default=Path.home() / '.claude/skills')
    parser.add_argument('--backup-directory', type=Path, default=Path.home() / '.openhook/setup-backups')
    args = parser.parse_args()
    try:
        print(json.dumps(setup(args.project, args.skills_directory, args.backup_directory, args.apply,
                               args.url, args.claude_skills_directory, args.codex_socket), indent=2))
    except (ValueError, OSError, TypeError, AttributeError):
        parser.exit(1, 'Setup failed: inspect project paths, hook JSON and permissions. No credentials are printed.\n')


if __name__ == '__main__':
    main()
