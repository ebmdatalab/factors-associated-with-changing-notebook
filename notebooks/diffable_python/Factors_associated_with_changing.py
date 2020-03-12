# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Import libraries

# NBVAL_IGNORE_OUTPUT
# ^this is a magic comment to work around this issue https://github.com/ebmdatalab/custom-docker/issues/10
import pandas as pd
from lib.generate_measure_sql import get_measure_json, build_sql
from change_detection import functions as chg
from lib.regression import rd

# +
## When not using cached data, this needs to be run first time
## after set up of docker environment (to authenticate BigQuery)
#from ebmdatalab import bq
#bq.cached_read("nothing",csv_path="nothing")
# -

# # Define measures and build measure SQL

# NBVAL_IGNORE_OUTPUT
#measures = ["desogestrel","trimethoprim"]
run_name = "custom_des_trim"
#get_measure_json(measures, run_name)
#build_sql(run_name)

# # Run change detection on all measures

change = chg.ChangeDetection(
    name=run_name,
    measure=True,
    custom_measure=True,
    direction="down",
    use_cache=True,
    overwrite=False,
    verbose=False,
    draw_figures="no")
change.run()

changes = change.concatenate_outputs()
changes.head()

# # Determine changes at national level for comparison
# - 1st decile of practice level changes

changes_nat = changes.groupby('measure').quantile(0.1)
changes_nat

# # Compare practice level changes with national changes

difference = changes - changes_nat
difference.head()

# # Get other regression variables

reg_data = rd.get_data()
reg_data.head()

# # Merge outcome(s) with regression variables and export to Stata
# - Stata code currently run separately
# - Future: convert to use R

# +
measures = difference.index.get_level_values(0).unique()
for m in measures:
    reg_data[m] = difference.loc[m,"is.tfirst.big"]

reg_data.to_csv("../lib/regression/data/data_for_stata.csv")
reg_data.head()
# -

# # Explore outcomes

difference.loc["desogestrel","is.tfirst.big"].hist()

difference.loc["trimethoprim","is.tfirst.big"].hist()
