PY ?= python

# Level 1: rebuild every statistic, table and figure from the published event-level files (no licence needed)
check:
	$(PY) check.py

# Free inputs
inputs-free:
	cd code && $(PY) -m adapters.gentry && $(PY) -m adapters.french

# Level 2 with your own licensed data (see DATA.md); set SHARADAR_DIR or WRDS_DIR
inputs-sharadar: inputs-free
	cd code && $(PY) -m adapters.sharadar $(SHARADAR_DIR)

inputs-crsp: inputs-free
	cd code && $(PY) -m adapters.crsp_compustat $(WRDS_DIR)

level2:
	$(PY) run_level2.py

.PHONY: check inputs-free inputs-sharadar inputs-crsp level2
