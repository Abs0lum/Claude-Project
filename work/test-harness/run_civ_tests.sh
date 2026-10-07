#!/usr/bin/env bash
# Run every CIVITAS suite against a scratch copy of knowledge/tools/bp02_src_228 (the mirror is never modified).
# Usage: work/test-harness/run_civ_tests.sh [SRC_DIR] [GALLERY_DIR]
#   SRC_DIR      default: knowledge/tools/bp02_src_228
#   GALLERY_DIR  a BP-02 pack's scripts/ dir holding the generated pw_gallery_data.js + pw_gallery_text.js
#                (not in the mirror; canopy/fell/hygiene/save need them). Default: none (those 4 suites then fail).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${1:-$ROOT/knowledge/tools/bp02_src_228}"
GAL="${2:-}"
TMP="$(mktemp -d)"
cp -a "$SRC/." "$TMP/"
mkdir -p "$TMP/node_modules"
cp -a "$ROOT/work/test-harness/node_modules_template/." "$TMP/node_modules/"
if [ -n "$GAL" ]; then cp "$GAL/pw_gallery_data.js" "$GAL/pw_gallery_text.js" "$TMP/" ; fi
cd "$TMP"
fail=0
for f in *.js; do node --check "$f" || { echo "SYNTAX FAIL $f"; fail=1; }; done
for t in tests/test_*.mjs; do
  line="$(timeout 300 node "$t" 2>&1 | grep -E 'passed|pass,|[0-9]+/[0-9]+ PASS|Error|FAIL' | tail -1)"
  echo "$(basename "$t" .mjs): $line"
done
echo "scratch copy: $TMP"
exit $fail
