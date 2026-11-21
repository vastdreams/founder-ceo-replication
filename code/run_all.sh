#!/bin/bash
# The whole Level 2 pipeline, in order, after redate.py has written out/redate.parquet.
# Stops at the first failure. Usage: bash run_all.sh  (from code/)
set -e
P=${PY:-python}
export FCE_DATA_SOURCE=${FCE_DATA_SOURCE:-files}
for s in build_events event_study paths ops_matched delist_dates coding_final founder_final stats_returns stats_ops board_outcomes referee_checks pre1998_tsr describe calendar_alpha figure_series; do
  echo "== $s"
  $P -W ignore $s.py | tail -3
done
echo RUN_ALL_DONE
