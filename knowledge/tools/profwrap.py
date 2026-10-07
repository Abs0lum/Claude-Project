"""wrap a module's top-level `system.runInterval(() => { ... }, N);` (the one at a given line) in prof(name, ...)."""
import sys, re
def wrap(text, line_no, name):
    lines = text.split("\n")
    start = sum(len(l) + 1 for l in lines[:line_no - 1])
    head = "system.runInterval(() => {"
    assert text[start:start + len(head)] == head, (name, text[start:start + 40])
    i = start + len(head) - 1          # the '{'
    depth = 0; j = i; instr = None; esc = False
    while True:
        c = text[j]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == instr: instr = None
        elif c in "\"'`": instr = c
        elif c == "/" and text[j+1] == "/": j = text.index("\n", j); continue
        elif c == "/" and text[j+1] == "*": j = text.index("*/", j) + 2; continue
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: break
        j += 1
    # text[j] is the closing brace of the arrow body; expect ", N);" after
    m = re.match(r"\}, ([A-Za-z_0-9]+)\);", text[j:j + 40])
    assert m, (name, text[j:j + 40])
    new = "system.runInterval(prof(\"%s\", () => {" % name + text[start + len(head):j] + "}), %s);" % m.group(1) + text[j + len(m.group(0)):]
    return text[:start] + new
if __name__ == "__main__":
    p = sys.argv[1]; t = open(p).read()
    pairs = sys.argv[2:]
    # process from the bottom up so line numbers stay valid
    items = sorted([(int(pairs[k]), pairs[k + 1]) for k in range(0, len(pairs), 2)], reverse=True)
    for ln, nm in items: t = wrap(t, ln, nm)
    helper = 'const PROF = (globalThis.__civProf = globalThis.__civProf || {});\nconst prof = (name, fn) => () => { const t0 = Date.now(); try { fn(); } finally { PROF[name] = (PROF[name] || 0) + Date.now() - t0; } };\n'
    open(p, "w").write(t)
    print("wrapped", items)
