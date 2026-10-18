#!/usr/bin/env bash
# Bootstrap a Linux box so an agent can actually verify its own work.
#
# Why this exists: on the Windows host there is no Rust toolchain and no MSVC to
# get one, so the Hybrid checker can only be run from a release binary that is
# behind main and measurably looser than it (53 corpus files: 32 agree, 21
# disagree, all in the "release accepts, main rejects" direction). That is why no
# soundness report could be submitted honestly. This script removes that excuse.
#
# Verified as far as possible without Linux: `bash -n` clean, embedded Python
# compiles, and the two things that would have broken it were checked against the
# repo — the Cargo workspace root is `compiler/`, not the repository root, and the
# package is `hyb` with `[[bin]] name = "hyb"` (so `compiler/target/release/hyb`).
#
# Assumptions: Ubuntu 22.04/24.04, 2 vCPU, 2 GB RAM, 20 GB disk. No GPU, no
# domain, no inbound ports.
#
# Usage:  bash bootstrap.sh

set -euo pipefail

REPO_DIR="${HOME}/gohybrid"
RUSTUP_HOME="${HOME}/.rustup"
REPO_URL="https://github.com/limitlessprojects/Go-Hybrid.git"

echo "== 1. base packages =="
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential curl git pkg-config libssl-dev \
    python3 python3-pip jq ripgrep unzip >/dev/null

echo "== 2. rust (stable, minimal profile) =="
if [ ! -x "${RUSTUP_HOME}/bin/rustup" ]; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --profile minimal --default-toolchain stable
fi
# shellcheck disable=SC1091
source "${RUSTUP_HOME}/env"
rustc --version
cargo --version

echo "== 3. clone the target (main only) =="
if [ ! -d "${REPO_DIR}/.git" ]; then
  git clone --depth 50 "${REPO_URL}" "${REPO_DIR}"
fi
cd "${REPO_DIR}"
echo "main HEAD: $(git log -1 --format='%h %ci %s')"

echo "== 4. build the checker from source =="
# The Cargo workspace lives in compiler/, NOT at the repository root. Getting this
# wrong fails immediately with "could not find Cargo.toml".
cd "${REPO_DIR}/compiler"
if ! cargo build --release -p hyb 2>/tmp/build.log; then
  echo "release build failed, retrying single-job with no debuginfo"
  RUSTFLAGS="-C debuginfo=0" cargo build --release -p hyb -j 1 2>>/tmp/build.log || {
      echo "BUILD FAILED — last 40 lines:"; tail -40 /tmp/build.log; exit 1; }
fi
HYB="${REPO_DIR}/compiler/target/release/hyb"
test -x "${HYB}" || { echo "expected binary missing at ${HYB}"; exit 1; }
echo "hyb: ${HYB}"
"${HYB}" --help | head -5

echo "== 5. corpus harness (from the repository root) =="
cd "${REPO_DIR}"
if [ -f tools/corpus_harness.py ]; then
  python3 tools/corpus_harness.py 2>&1 | tail -20 || true
else
  echo "tools/corpus_harness.py not present; skipping"
fi

echo "== 6. the calibration that matters =="
# Runs every corpus file against its declared verdict, using the binary built from
# main. This is the measurement the Windows host could only approximate with a
# stale release binary.
HYB="${HYB}" python3 - <<'PY'
import os, pathlib, re, subprocess, sys
hyb = os.environ["HYB"]
root = pathlib.Path('tests/checker-corpus')
rows, errs, agree, disagree = [], [], 0, 0
files = sorted(root.glob('*.hy'))
for f in files:
    src = f.read_text(encoding='utf-8')
    # Uppercase + colon only: corpus prose sometimes says "expected-verdict"
    # in a sentence, and that must not be read as a declaration.
    m = re.search(r'^//\s*EXPECTED-VERDICT:\s*(ACCEPT-MANAGED|ACCEPT|REJECT)\b', src, re.M)
    if not m:
        continue
    exp = m.group(1)
    code = subprocess.run([hyb, 'check', str(f), '--json'],
                          capture_output=True).returncode
    # cmd_check returns ExitCode::from(2) for a usage error. Counting that as a
    # rejection would turn every file into a fake mismatch, so it is reported
    # separately instead of being folded into the score.
    if code == 2:
        errs.append(f'{f.name}: usage error (exit 2) — checker rejected the arguments')
        continue
    got = 'ACCEPT' if code == 0 else 'REJECT'
    ok = (exp == got) or (exp == 'ACCEPT-MANAGED' and got == 'ACCEPT')
    agree += ok
    disagree += (not ok)
    if not ok:
        rows.append(f'{f.name}: expected={exp} got={got} (exit {code})')
print(f'corpus files: {len(files)}')
print(f'agree={agree} disagree={disagree} errored={len(errs)}')
for e in errs:
    print('  ERROR', e)
for r in rows:
    print('  MISMATCH', r)
if errs:
    print('ERRORS mean the invocation is wrong, not the corpus. Fix the command')
    print('before reading anything into the counts above.')
sys.exit(0)
PY

echo
echo "== done =="
echo "Head: $(cd "${REPO_DIR}" && git rev-parse --short HEAD)"
echo "If step 6 printed disagree=0, main is internally consistent and any candidate"
echo "tested from here is being tested against the real checker."
echo "Paste the step-6 lines back — that one measurement decides whether this box"
echo "turns into verified contributions or into another dead end."
