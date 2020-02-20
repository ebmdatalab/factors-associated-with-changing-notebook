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

# +
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
# import R's "base" package
base = importr('base')

# import R's "utils" package
utils = importr('utils')
# -

robjects.r('''
        # create a function `f`
        f <- function(r, verbose=FALSE) {
            if (verbose) {
                cat("I am calling f().\n")
            }
            2 * pi * r
        }
        # call the function `f` with argument value 3
        f(3)
        ''')

robjects.r['f'](3,verbose='TRUE')

from rpy2.robjects import pandas2ri
pandas2ri.activate()
robjects.globalenv['dataframe'] = reg_data[['dispensing_patients']]
robjects.globalenv['dataframe']

# +
import pandas as pd
from rpy2 import robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()
R = ro.r

M = R.lm('dispensing_patients~list_size', data=reg_data[['dispensing_patients','list_size']])
print(R.summary(M).rx2('coefficients'))


# +
def r_matrix_to_data_frame(r_matrix):
    """Convert an R matrix into a Pandas DataFrame"""
    import pandas as pd
    from rpy2.robjects import pandas2ri
    array = pandas2ri.ri2py(r_matrix)
    return pd.DataFrame(array,
                        index=r_matrix.names[0],
                        columns=r_matrix.names[1])

# Let's start from unutbu's line retrieving the coefficients:
coeffs = R.summary(M).rx2('coefficients')
df = r_matrix_to_data_frame(coeffs)
# -

from rpy2.robjects import pandas2ri
dir(pandas2ri)
