#!/bin/bash
# The whole pipeline on the authors' server, in order, after redate.py has written out/redate.parquet.
# Stops at the first failure. Usage: bash run_all.sh  (from analysis/)
set -e
P=${PY:-$HOME/fce-venv/bin/python}
export FCE_DATA_SOURCE=${FCE_DATA_SOURCE:-postgres}
for s in build_events event_study controls paths ops_matched delist_dates coding_final screen founder_final stats_returns stats_ops board_outcomes referee_checks founder_reason founder_value founder_growth founder_alpha founder_appendix d44_compare pre1998_tsr describe calendar_alpha figure_series; do
  echo "== $s"
  $P -W ignore $s.py | tail -3
done
echo "== founder_value (screened, D-38)"
FV_SCREEN=1 FV_STATS_FILE=founder_value_stats_screen.json $P -W ignore founder_value.py | tail -3
echo RUN_ALL_DONE
