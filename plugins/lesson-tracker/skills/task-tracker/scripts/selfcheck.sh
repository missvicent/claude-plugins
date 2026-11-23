#!/usr/bin/env bash
# Script checks for vault.py (lookup order, setup from obsidian.json, find),
# build.py (log cap, tries count) and insights.py (active filter).
# Runs in a temp dir with a fake vault and config; touches nothing real.
set -eu
S="$(cd "$(dirname "$0")" && pwd)"; T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
unset TRACKER_VAULT
export LESSON_TRACKER_CONFIG="$T/config.json" OBSIDIAN_JSON="$T/obsidian.json"
mkdir -p "$T/vault/.obsidian" "$T/vault/projects/p/trackers/demo" "$T/vault/projects/p/insights" "$T/other"

# no config -> one-line error, non-zero exit
if python3 "$S/vault.py" where >"$T/out" 2>&1; then echo "FAIL: where without config should fail"; exit 1; fi
grep -q "No vault set" "$T/out"

# setup reads obsidian.json, rejects a non-vault, saves the pick
printf '{"vaults":{"a":{"path":"%s"},"b":{"path":"%s"}}}' "$T/vault" "$T/other" > "$OBSIDIAN_JSON"
python3 "$S/vault.py" setup | grep -q "1. vault"
if python3 "$S/vault.py" setup 2 >/dev/null 2>&1; then echo "FAIL: non-vault accepted"; exit 1; fi
python3 "$S/vault.py" setup 1 >/dev/null
[ "$(python3 "$S/vault.py" where)" = "$T/vault" ]

# env beats config
[ "$(TRACKER_VAULT="$T/other" python3 "$S/vault.py" where)" = "$T/other" ]

# project per repo
python3 "$S/vault.py" set-project repo projects/p >/dev/null
[ "$(python3 "$S/vault.py" project repo)" = "projects/p" ]

# find + build: log cap and tries
cat > "$T/vault/projects/p/trackers/demo/tracker.json" <<'J'
{"feature":"demo","title":"Demo","as_of":"2026-11-23",
 "tasks":[{"task":"t","status":"wip","log":[
 {"result":"fail","note":"a"},{"result":"fail","note":"b"},{"result":"pass","note":"c"},
 {"result":"fail","note":"d"},{"result":"fail","note":"e"},{"result":"pass","note":"f"},{"result":"pass","note":"g"}]}]}
J
[ "$(python3 "$S/vault.py" find demo)" = "$T/vault/projects/p/trackers/demo" ]
python3 "$S/build.py" "$T/vault/projects/p/trackers/demo/tracker.json" >/dev/null

# insights: active only
printf -- '---\ntopic: crewai\napplies_to: [coding]\nstatus: active\n---\nA.\n' > "$T/vault/projects/p/insights/a.md"
printf -- '---\ntopic: crewai\napplies_to: [coding]\nstatus: retired\n---\nB.\n' > "$T/vault/projects/p/insights/b.md"

python3 - "$T" "$S" <<'P'
import json, subprocess, sys
from pathlib import Path
T, S = Path(sys.argv[1]), sys.argv[2]
d = T / "vault/projects/p/trackers/demo"
t = json.loads((d / "tracker.json").read_text())["tasks"][0]
assert [e["note"] for e in t["log"]] == list("cdefg"), t["log"]
assert t["log_summary"] == "2 earlier checks, 2 failed (last: b)", t["log_summary"]
assert "7 tries" in (d / "tracker.md").read_text()
out = subprocess.run([sys.executable, f"{S}/insights.py", "projects/p", "--topic", "crewai"],
                     capture_output=True, text=True, check=True).stdout
assert "## a " in out and "## b " not in out, out
print("selfcheck OK")
P
