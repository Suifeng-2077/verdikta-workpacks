# Fill-in checklist — 20 minutes from job post to submitted repo

Verdikta code bounties are won by whoever first posts something that passes. On job 255 the
winner submitted **21 minutes** after the job opened and that single pass locked the bounty.
So the target here is a complete, tested, honest deliverable fast — not a polished one.

## Order of work

1. `node new.mjs <jobId> <slug>` — copies the template to `../../workpacks/job-<jobId>/` and
   substitutes the job name. Two minutes.
2. **Read the rubric table and the grading notes first.** Copy the CLI option table verbatim into
   `analyze.py`'s `argparse` block and into `README.md`. Defaults must match exactly; a default that
   differs costs the "runs as specified" points outright.
3. **Map the input columns.** Put every column the job lists into `REQUIRED` or into the loader, and
   handle the empty-string cases the job calls out (`vs_best_bps` empty, `stale` empty). The template
   already coerces numerics and drops unparseable rows; keep the skip counter and print it.
4. **Edit only `find_runs` / `summarise`.** That is where the job's own logic goes. Everything else —
   CLI, loading, report assembly, duration formatting — should not need touching.
5. **Add a test per rubric bullet that says "exactly"** (boundaries, tie-breaking, exclusion rules).
   The template's nine tests already cover the generic edges; add the job-specific ones beside them.
6. `pytest -q` then `python analyze.py sample.csv --threshold <job default>` — paste the real output
   into `README.md`'s example section. Do not paste aspirational output.
7. **Check the automatic-fail list** in the job text (network calls, hardcoded results, missing tests,
   not using the named library) before pushing. Those fail the whole submission.
8. Push to a public repo, then submit. Do this even if a section feels thin: a passing minimal
   deliverable beats a perfect one that arrives after the lock.

## What the template already gives you

- `analyze.py` — argparse CLI matching the shape of most of these jobs, robust loader with a skip
  counter, per-group run detection broken by gap or by a low scan, markdown report with a header,
  summary table, runs table and plain-language findings.
- `tests/test_analyze.py` — nine passing tests on synthetic fixtures, including every generic edge
  case these rubrics tend to ask for.
- `README.md`, `requirements.txt`, `sample.csv`.

## What it deliberately does not do

It does not know the job's specific rules, and it must not pretend to. Anything the rubric names
exactly — a tie-break, an exclusion rule, a column that is repeated per scan — has to be written out
and tested, not approximated. If a rule cannot be implemented honestly in the time available, say so
in the README rather than faking it: the jury reads the code.
