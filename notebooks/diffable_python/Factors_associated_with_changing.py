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

measures = ["desogestrel","trimethoprim"]
run_name = "first_go"
get_measure_json(measures, run_name)
build_sql(run_name)

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

change.num_cores = 1
change.national_changes()

changes_nat = change.concatenate_outputs("_national")
changes_nat = changes_nat.reset_index(level=1)
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

biggest_change = difference[["is.tfirst.big"]].groupby(level=1).sum()
data_for_stata = biggest_change.join(reg_data,how="left")
data_for_stata.to_csv("../lib/regression/data/data_for_stata.csv")
data_for_stata.head()

# # Explore outcomes

biggest_change.hist()

difference.loc["desogestrel","is.tfirst.big"].hist()

difference.loc["trimethoprim","is.tfirst.big"].hist()

difference.loc["trimethoprim","is.slope.ma.prop"].describe()

difference.loc["trimethoprim","is.intlev.levdprop"].describe()
