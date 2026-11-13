#!/usr/bin/env python3
"""Pull project updates before a search, without ever risking the user's files.

  update.py        fetch, then fast-forward if the checkout is simply behind; prints one or two lines

Only fast-forwards. It skips (and says why) when offline, when there are local commits,
or when a locally edited shared file is also changed upstream. Personal folders are
gitignored, so a pull never touches them. Never prompts for credentials.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FETCH_TIMEOUT = 20


def git(*args, timeout=10):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    env.setdefault('GIT_SSH_COMMAND', 'ssh -o BatchMode=yes -o ConnectTimeout=10')
    return subprocess.run(['git', *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)


def out(*args):
    return git(*args).stdout.strip()


def main():
    if git('rev-parse', '--abbrev-ref', '@{u}').returncode != 0:
        return 'update: skipped (no upstream branch to pull from)'
    try:
        fetched = git('fetch', '--quiet', timeout=FETCH_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "update: skipped (couldn't reach the repo, timed out)"
    if fetched.returncode != 0:
        return "update: skipped (couldn't reach the repo)"

    behind = int(out('rev-list', '--count', 'HEAD..@{u}'))
    ahead = int(out('rev-list', '--count', '@{u}..HEAD'))
    if behind == 0:
        return 'update: up to date'
    if ahead:
        return f'update: skipped ({ahead} local commit(s); {behind} update(s) to pull by hand)'

    incoming = set(out('diff', '--name-only', 'HEAD', '@{u}').splitlines())
    edited = set(out('diff', '--name-only', 'HEAD').splitlines())
    clash = sorted(incoming & edited)
    if clash:
        return f"update: skipped ({behind} update(s), but these locally edited files also changed upstream: {', '.join(clash)})"

    subjects = out('log', '--format=%s', 'HEAD..@{u}').splitlines()
    merged = git('merge', '--ff-only', '--quiet', '@{u}')
    if merged.returncode != 0:
        reason = (merged.stderr.strip().splitlines() or ['merge failed'])[0]
        return f'update: skipped (git: {reason})'

    lines = [f"update: pulled {behind} update(s): {'; '.join(subjects)}"]
    if 'CLAUDE.md' in incoming:
        lines.append('update: CLAUDE.md changed, re-read it before continuing')
    return '\n'.join(lines)


if __name__ == '__main__':
    try:
        print(main())
    except Exception as e:  # never block a search over an update problem
        print(f'update: skipped ({e})')
    sys.exit(0)
