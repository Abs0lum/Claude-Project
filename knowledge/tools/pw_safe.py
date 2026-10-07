#!/usr/bin/env python3
"""pw_safe.py — the RECOVERABLE-DELETE LAW, made structural (his 14:41 10-01 rule "never delete"; his 02:16 10-03:
"treat the garbage folder as your recoverable delete … clear the sandbox into my Drive when necessary").

Installed for EVERY python process through ~/.local/lib/python3.11/site-packages/usercustomize.py, this turns the
destructive calls — shutil.rmtree, os.remove, os.unlink, os.rmdir, pathlib.Path.unlink / .rmdir — into a MOVE into
/home/claude/_garbage/<utc stamp>/<path relative to /home/claude>, logged in _logs/pw_safe_ledger.md, whenever the
target lies inside the workspace. Old build scripts that still say `shutil.rmtree(DST)` therefore discard instead of
destroying. A real deletion still happens (unchanged behaviour) for:
  * anything outside /home/claude (pip / npm / tempfile internals, /tmp, the scratchpad);
  * dot-directories directly under /home/claude (.cache, .npm, .config …);
  * paths already inside _garbage (how tools/garbage_tar_to_drive.py frees space after the Drive copy is md5-verified);
  * any process started with PW_ALLOW_DELETE=1 (his approval, per use).
Self-test: python3 tools/pw_safe.py --selftest. Complexity: O(1) checks per call; a move is a rename on one filesystem."""
import os
import pathlib
import shutil
import sys
import time

ROOT = "/home/claude/"
GARB = ROOT + "_garbage/"
FAILSAFE = ROOT + "_failsafe/"                 # append-only: no delete, no move-out, PW_ALLOW_DELETE included (his 02:21 10-03)
LEDGER = ROOT + "_logs/pw_safe_ledger.md"
_ORIG = {}
_installed = False


class FailsafeError(PermissionError):
    """raised for any attempt to delete from, or move out of, /home/claude/_failsafe"""


def _in_failsafe(path):
    try:
        a = os.path.abspath(os.fspath(path))
    except Exception:
        return False
    return a == FAILSAFE.rstrip("/") or a.startswith(FAILSAFE)


def refuse_if_failsafe(path, what):
    if _in_failsafe(path):
        _log("REFUSED " + what, os.path.abspath(os.fspath(path)), "(the failsafe is append-only)")
        raise FailsafeError(f"{what} refused: {os.fspath(path)} is inside the append-only failsafe (/home/claude/_failsafe)")


def guarded(path, dir_fd=None):
    """True when deleting `path` must become a move into _garbage. A call with dir_fd (shutil.rmtree's internals pass
    ENTRY NAMES relative to an open directory fd) is never guarded: resolving such a name against the CWD named the
    wrong file — on 10-03 02:20 it moved the real /home/claude/_bds while an archive inside _garbage was being removed."""
    if dir_fd is not None:
        return False
    if os.environ.get("PW_ALLOW_DELETE") == "1":
        return False
    try:
        a = os.path.abspath(os.fspath(path))
    except Exception:
        return False
    if not a.startswith(ROOT) or a.startswith(GARB) or a.rstrip("/") == ROOT.rstrip("/"):
        return False
    rel = a[len(ROOT):]
    if rel.startswith("."):
        return False
    return True


def _log(kind, src, dst):
    try:
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        with open(LEDGER, "a") as f:
            f.write(f"- {time.strftime('%Y-%m-%d %H:%M:%S')} {kind} pid {os.getpid()} ({os.path.basename(sys.argv[0]) or 'python'}): {src} -> {dst}\n")
    except Exception:
        pass


def discard(path, kind="delete"):
    """move `path` (file or tree) into _garbage/<stamp>/<rel>; returns the destination"""
    a = os.path.abspath(os.fspath(path))
    rel = a[len(ROOT):]
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    dst = os.path.join(GARB, stamp, rel)
    if os.path.lexists(dst):
        dst = f"{dst}-{os.getpid()}-{time.time_ns()}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    _ORIG["move"](a, dst)
    _log(kind, a, dst)
    return dst


def _is_file_target(path):
    """remove / unlink act on files and symlinks only; a directory keeps the original call (which raises)"""
    return os.path.lexists(path) and not (os.path.isdir(path) and not os.path.islink(path))


def _rmtree(path, *args, **kwargs):
    if (locals().get('dir_fd') is None and (kwargs.get('dir_fd') is None)):
        refuse_if_failsafe(path, 'rmtree')
    if guarded(path, kwargs.get("dir_fd")) and os.path.lexists(path):
        discard(path, "rmtree")
        return None
    return _ORIG["rmtree"](path, *args, **kwargs)


def _remove(path, *args, dir_fd=None, **kwargs):
    if (locals().get('dir_fd') is None and (kwargs.get('dir_fd') is None)):
        refuse_if_failsafe(path, 'remove')
    if guarded(path, dir_fd) and _is_file_target(path):
        discard(path, "remove")
        return None
    return _ORIG["remove"](path, *args, dir_fd=dir_fd, **kwargs)


def _unlink(path, *args, dir_fd=None, **kwargs):
    if (locals().get('dir_fd') is None and (kwargs.get('dir_fd') is None)):
        refuse_if_failsafe(path, 'unlink')
    if guarded(path, dir_fd) and _is_file_target(path):
        discard(path, "unlink")
        return None
    return _ORIG["unlink"](path, *args, dir_fd=dir_fd, **kwargs)


def _rmdir(path, *args, dir_fd=None, **kwargs):
    if (locals().get('dir_fd') is None and (kwargs.get('dir_fd') is None)):
        refuse_if_failsafe(path, 'rmdir')
    # an EMPTY directory holds nothing to recover: always the original call (a non-empty one raises, as it should)
    return _ORIG["rmdir"](path, *args, dir_fd=dir_fd, **kwargs)


def _path_unlink(self, missing_ok=False):
    refuse_if_failsafe(self, "Path.unlink")
    if guarded(self) and self.exists():
        discard(self, "Path.unlink")
        return None
    return _ORIG["Path.unlink"](self, missing_ok=missing_ok)


def _path_rmdir(self):
    refuse_if_failsafe(self, "Path.rmdir")
    if guarded(self) and self.exists():
        discard(self, "Path.rmdir")
        return None
    return _ORIG["Path.rmdir"](self)


def _rename(src, dst, *args, **kwargs):
    if kwargs.get("src_dir_fd") is None:
        refuse_if_failsafe(src, "rename")
    return _ORIG["rename"](src, dst, *args, **kwargs)


def _replace(src, dst, *args, **kwargs):
    if kwargs.get("src_dir_fd") is None:
        refuse_if_failsafe(src, "replace")
    return _ORIG["replace"](src, dst, *args, **kwargs)


def _move(src, dst, *args, **kwargs):
    refuse_if_failsafe(src, "move")
    return _ORIG["move"](src, dst, *args, **kwargs)


def install():
    global _installed
    if _installed:
        return
    _ORIG["move"] = shutil.move
    _ORIG["rename"] = os.rename
    _ORIG["replace"] = os.replace
    os.rename = _rename
    os.replace = _replace
    shutil.move = _move
    _ORIG["rmtree"] = shutil.rmtree
    _ORIG["remove"] = os.remove
    _ORIG["unlink"] = os.unlink
    _ORIG["rmdir"] = os.rmdir
    _ORIG["Path.unlink"] = pathlib.Path.unlink
    _ORIG["Path.rmdir"] = pathlib.Path.rmdir
    shutil.rmtree = _rmtree
    os.remove = _remove
    os.unlink = _unlink
    os.rmdir = _rmdir
    pathlib.Path.unlink = _path_unlink
    pathlib.Path.rmdir = _path_rmdir
    _installed = True


def selftest():
    install()
    import tempfile
    base = pathlib.Path(ROOT + "_pw_safe_selftest")
    if base.exists():
        _ORIG["move"](str(base), str(base) + f"-old-{time.time_ns()}")
    ok = 0
    (base / "a").mkdir(parents=True)
    (base / "a/b.txt").write_text("b")
    shutil.rmtree(base / "a")
    moved = [p for p in pathlib.Path(GARB).glob("*/_pw_safe_selftest/a/b.txt")]
    assert not (base / "a").exists() and moved, "rmtree inside the workspace must move into _garbage"
    ok += 1
    f = base / "c.txt"
    f.write_text("c")
    os.remove(f)
    assert not f.exists() and list(pathlib.Path(GARB).glob("*/_pw_safe_selftest/c.txt")), "os.remove must move"
    ok += 1
    f = base / "d.txt"
    f.write_text("d")
    f.unlink()
    assert not f.exists() and list(pathlib.Path(GARB).glob("*/_pw_safe_selftest/d.txt")), "Path.unlink must move"
    ok += 1
    td = pathlib.Path(tempfile.mkdtemp())
    (td / "x.txt").write_text("x")
    os.remove(td / "x.txt")
    shutil.rmtree(td)
    assert not td.exists() and not list(pathlib.Path(GARB).glob("*" + str(td))), "outside the workspace: a real delete"
    ok += 1
    g = pathlib.Path(GARB) / "_pw_safe_selftest_inner"
    g.mkdir(exist_ok=True)
    (g / "y.txt").write_text("y")
    shutil.rmtree(g)
    assert not g.exists(), "inside _garbage: a real delete (the Drive archiver frees space)"
    ok += 1
    os.environ["PW_ALLOW_DELETE"] = "1"
    f = base / "e.txt"
    f.write_text("e")
    os.remove(f)
    del os.environ["PW_ALLOW_DELETE"]
    assert not f.exists() and not list(pathlib.Path(GARB).glob("*/_pw_safe_selftest/e.txt")), "PW_ALLOW_DELETE=1: a real delete"
    ok += 1
    shutil.rmtree(base)                                   # the test folder itself goes to _garbage
    assert not base.exists()
    ok += 1
    # REGRESSION (02:20 10-03): removing an archive inside _garbage must never touch a same-named entry in the CWD
    cwd0 = os.getcwd()
    os.chdir(ROOT)
    twin = pathlib.Path(ROOT + "_pw_safe_twin")
    (twin / "inner").mkdir(parents=True)
    (twin / "inner/keep.txt").write_text("keep")
    arch = pathlib.Path(GARB) / "_pw_safe_arch"
    (arch / "_pw_safe_twin" / "inner").mkdir(parents=True)
    (arch / "_pw_safe_twin" / "inner/keep.txt").write_text("gone")
    shutil.rmtree(arch)
    os.chdir(cwd0)
    assert not arch.exists() and (twin / "inner/keep.txt").read_text() == "keep", "fd-relative names inside rmtree must not resolve against the CWD"
    ok += 1
    _ORIG["rmtree"](twin)
    nonempty = base.parent / "_pw_safe_nonempty"
    (nonempty / "x").mkdir(parents=True)
    try:
        os.rmdir(nonempty)
        raise AssertionError("rmdir of a non-empty workspace dir must raise, never move")
    except OSError:
        pass
    assert (nonempty / "x").exists()
    ok += 1
    _ORIG["rmtree"](nonempty)
    # the FAILSAFE is append-only: delete, unlink, rmtree, move-out and rename all refuse — PW_ALLOW_DELETE included
    fs = pathlib.Path(FAILSAFE) / "_pw_safe_probe"
    fs.mkdir(parents=True, exist_ok=True)
    probe = fs / "keep.txt"
    probe.write_text("keep")
    os.environ["PW_ALLOW_DELETE"] = "1"
    refused = 0
    for call in (lambda: os.remove(probe), lambda: probe.unlink(), lambda: shutil.rmtree(fs), lambda: shutil.move(str(probe), ROOT + "_pw_safe_moved.txt"),
                 lambda: os.rename(probe, ROOT + "_pw_safe_moved.txt"), lambda: os.rmdir(fs)):
        try:
            call()
        except FailsafeError:
            refused += 1
    del os.environ["PW_ALLOW_DELETE"]
    assert refused == 6 and probe.read_text() == "keep", f"failsafe refusals {refused}/6"
    ok += 1
    print(f"pw_safe selftest: {ok}/10 passed (moves logged in {LEDGER})")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        print(__doc__)
