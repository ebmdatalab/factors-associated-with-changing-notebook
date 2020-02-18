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

# NBVAL_IGNORE_OUTPUT
# ^this is a magic comment to work around this issue https://github.com/ebmdatalab/custom-docker/issues/10
import pandas as pd
from change_detection import functions as chg
from lib.regression import rd

change = chg.ChangeDetection('practice_data%',
                                    measure=True,
                                    direction='down',
                                    use_cache=True,
                                    overwrite=False,
                                    verbose=False,
                                    draw_figures='no',
                                    measure_folder='alex')
change.run()

change.get_measure_list()

changes = change.concatenate_outputs()
changes.head()

change.num_cores = 1
change.national_changes()

changes_nat = change.concatenate_outputs('_national')
changes_nat = changes_nat.reset_index(level=1)
changes_nat

difference = changes - changes_nat
difference

reg_data = rd.get_data()
reg_data.head()
