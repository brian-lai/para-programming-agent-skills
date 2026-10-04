"""Inspect untrusted Git data using a private repository with no supplied config/hooks.

Never execute Git with an agent-owned gitdir. Copy only regular object/ref/index
files, using no-follow directory descriptors. Mutations publish only changed
objects/refs; no config, hooks, attributes, alternates or executable helpers copy.
"""
import contextlib
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from fixtures import FIXED_ENV


@contextlib.contextmanager
def directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        yield fd
    finally:
        os.close(fd)


def read_file(fd, name):
    source = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    try:
        if not stat.S_ISREG(os.fstat(source).st_mode):
            raise ValueError('nonregular Git data')
        with os.fdopen(os.dup(source), 'rb') as stream:
            return stream.read()
    finally:
        os.close(source)


def collect(fd, prefix=''):
    result = {}
    for name in os.listdir(fd):
        rel = prefix + name
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            try:
                result.update(collect(child, rel + '/'))
            finally:
                os.close(child)
        elif stat.S_ISREG(info.st_mode):
            # Object alternates can refer outside the fixture; never load them.
            if rel not in ('objects/info/alternates', 'objects/info/http-alternates'):
                result[rel] = read_file(fd, name)
        else:
            raise ValueError('nonregular Git data: ' + rel)
    return result


def git_paths(repo):
    repo = Path(repo).absolute()
    dot = repo / '.git'
    if dot.is_symlink():
        raise ValueError('symlink gitdir')
    if dot.is_file():
        value = dot.read_text().strip()
        if not value.startswith('gitdir: '):
            raise ValueError('invalid gitdir pointer')
        local = Path(value[8:])
        if not local.is_absolute():
            local = repo / local
        # Linked worktrees are nested in the one mounted fixture checkout.
        primary = next((p for p in repo.parents if (p / '.git').is_dir()), None)
        if primary is None or not local.resolve().is_relative_to(primary / '.git/worktrees'):
            raise ValueError('out-of-fixture gitdir')
        common = primary / '.git'
    elif dot.is_dir():
        local = common = dot
    else:
        local = common = repo  # bare remote
    return repo, local, common


def snapshot(repo, target):
    repo, local, common = git_paths(repo)
    data = {}
    with directory(common) as root:
        for name in ('objects', 'refs', 'worktrees'):
            try:
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
            except FileNotFoundError:
                continue
            try:
                data.update(collect(child, name + '/'))
            finally:
                os.close(child)
        for name in ('packed-refs',):
            try:
                data[name] = read_file(root, name)
            except FileNotFoundError:
                pass
    with directory(local) as root:
        for name in ('HEAD', 'index'):
            try:
                data[name] = read_file(root, name)
            except FileNotFoundError:
                pass
    for name, content in data.items():
        dest = target / name;dest.parent.mkdir(parents=True, exist_ok=True);dest.write_bytes(content)
    (target / 'objects').mkdir(exist_ok=True);(target / 'refs').mkdir(exist_ok=True)
    return common, data


def publish(common, name, content, previous):
    # Descriptor-relative traversal also prevents a concurrent symlink swap.
    with directory(common) as root:
        parent = os.dup(root)
        try:
            parts = Path(name).parts
            for part in parts[:-1]:
                try:
                    os.mkdir(part, dir_fd=parent)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent);parent = child
            leaf = parts[-1];lock = leaf + '.lock'
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o666, dir_fd=parent)
            try:
                try:
                    current = read_file(parent, leaf)
                except FileNotFoundError:
                    current = None
                if current != previous and current != content:
                    raise ValueError('Git data changed during fixture operation')
                with os.fdopen(fd, 'wb') as stream:
                    fd = None;stream.write(content)
                os.rename(lock, leaf, src_dir_fd=parent, dst_dir_fd=parent)
            finally:
                if fd is not None:
                    os.close(fd)
                try:
                    os.unlink(lock, dir_fd=parent)
                except FileNotFoundError:
                    pass
        finally:
            os.close(parent)


def git(repo, *args, input=None):
    with tempfile.TemporaryDirectory(prefix='para-trusted-git-') as tmp:
        target = Path(tmp)
        common, original = snapshot(repo, target)
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.update(FIXED_ENV)
        command = ['git', '--git-dir', str(target), '--work-tree', str(repo), '-c', 'core.hooksPath=/dev/null',
                   '-c', 'core.fsmonitor=false', '-c', 'protocol.allow=never', *args]
        result = subprocess.run(command, input=input, text=True, capture_output=True, check=True, env=env).stdout.strip()
        if args[0] in ('commit-tree', 'update-ref', 'merge-tree'):
            for p in sorted(target.rglob('*')):
                if p.is_file():
                    name = str(p.relative_to(target));content = p.read_bytes()
                    if name.startswith(('objects/', 'refs/')) and content != original.get(name):
                        publish(common, name, content, original.get(name))
        return result


def ancestor(repo, older, newer):
    try:
        git(repo, 'merge-base', '--is-ancestor', str(older), str(newer))
        return True
    except subprocess.CalledProcessError:
        return False
