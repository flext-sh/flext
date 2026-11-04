"""Recover the literal corrupted name from Git HEAD without reverting other edits."""
import argparse
import ast
import collections
import difflib
import json
import pathlib
import re
import subprocess

BAD = b'TestsFlext#1'
NAME = re.compile(rb'TestsFlext[A-Za-z0-9_]+|TestsFlext#1')
ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def normalized(line):
    return NAME.sub(b'@RECOVER_NAME@', line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    found = subprocess.run(['rg', '-l', '-0', '-F', BAD.decode(), '--glob', '*.py', str(ROOT)], capture_output=True, check=False)
    if found.returncode not in (0, 1):
        raise RuntimeError(found.stderr.decode())
    plans = []
    unresolved = []
    names = collections.Counter()
    for raw_path in found.stdout.split(b'\0'):
        if not raw_path:
            continue
        path = pathlib.Path(raw_path.decode())
        if path == pathlib.Path(__file__).resolve():
            continue
        before = path.read_bytes()
        repo = pathlib.Path(git(path.parent, 'rev-parse', '--show-toplevel').decode().strip())
        relative = path.relative_to(repo).as_posix()
        original = git(repo, 'show', f'HEAD:{relative}')
        old_lines = original.splitlines(keepends=True)
        new_lines = before.splitlines(keepends=True)
        old_norm = [normalized(line) for line in old_lines]
        new_norm = [normalized(line) for line in new_lines]
        aligned = {}
        for a, b, count in difflib.SequenceMatcher(None, old_norm, new_norm, autojunk=False).get_matching_blocks():
            aligned.update({b + i: a + i for i in range(count)})
        candidates = collections.defaultdict(list)
        for i, line in enumerate(old_norm):
            candidates[line].append(i)
        after_lines = []
        replacements = 0
        for i, line in enumerate(new_lines):
            if BAD not in line:
                after_lines.append(line)
                continue
            indexes = [aligned[i]] if i in aligned else candidates[new_norm[i]]
            variants = set()
            for index in indexes:
                old_matches = list(NAME.finditer(old_lines[index]))
                new_matches = list(NAME.finditer(line))
                if len(old_matches) != len(new_matches):
                    continue
                pairs = list(zip(old_matches, new_matches))
                if any(n.group() != BAD and n.group() != o.group() for o, n in pairs):
                    continue
                output = line
                for o, n in reversed(pairs):
                    if n.group() == BAD:
                        output = output[:n.start()] + o.group() + output[n.end():]
                variants.add(output)
            if len(variants) != 1:
                unresolved.append(f'{path.relative_to(ROOT)}:{i + 1}')
                after_lines.append(line)
                continue
            result = variants.pop()
            for o, n in zip(NAME.finditer(result), NAME.finditer(line)):
                if n.group() == BAD:
                    names[o.group().decode()] += 1
                    replacements += 1
            after_lines.append(result)
        after = b''.join(after_lines)
        assert normalized(after) == normalized(before), path
        if BAD not in after:
            ast.parse(after, filename=str(path))
        plans.append((path, before, after, replacements))
    print(json.dumps({'apply': args.apply, 'files': len(plans), 'occurrences': sum(p[3] for p in plans), 'distinct_names': len(names), 'unresolved': unresolved, 'names': dict(names)}, indent=2))
    if unresolved:
        raise SystemExit('Ambiguous recovery: no files written')
    if args.apply:
        for path, before, _, _ in plans:
            if path.read_bytes() != before:
                raise SystemExit(f'Input changed: no files written: {path}')
        for path, before, after, count in plans:
            if before != after:
                path.write_bytes(after)
        print('Recovery applied; only corrupted name spans replaced.')


if __name__ == '__main__':
    main()
