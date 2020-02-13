import json
import os
import sys


# This is adapted from frontend/management/commands/import_measures.py
def build_num_or_denom_fields(measure_def, num_or_denom):
    def full_attr_name(attr):
        return num_or_denom + "_" + attr

    def get_measure_value(attr):
        value = measure_def[full_attr_name(attr)]
        if isinstance(value, list):
            value = " ".join(value)
        value = value.replace("{", "")
        value = value.replace("}", "")
        return value

    type_ = measure_def[num_or_denom + "_type"]

    if type_ == "custom":
        columns = get_measure_value("columns")
        from_ = get_measure_value("from")
        where = get_measure_value("where")

    elif type_ == "bnf_items":
        columns = "SUM(items) AS {}".format(num_or_denom)
        from_ = "hscic.normalised_prescribing_standard"
        where = get_measure_value("where")

    elif type_ == "bnf_quantity":
        columns = "SUM(quantity) AS {}".format(num_or_denom)
        from_ = "hscic.normalised_prescribing_standard"
        where = get_measure_value("where")

    elif type_ == "bnf_cost":
        columns = "SUM(actual_cost) AS {}".format(num_or_denom)
        from_ = "hscic.normalised_prescribing_standard"
        where = get_measure_value("where")

    elif type_ == "list_size":
        assert num_or_denom == "denominator"
        columns = "SUM(total_list_size / 1000.0) AS denominator"
        from_ = "hscic.practice_statistics"
        where = "1 = 1"

    elif type_ == "star_pu_antibiotics":
        assert num_or_denom == "denominator"
        columns = "CAST(JSON_EXTRACT(MAX(star_pu), '$.oral_antibacterials_item') AS FLOAT64) AS denominator"
        from_ = "hscic.practice_statistics"
        where = "1 = 1"

    else:
        assert False, type_

    return {
        full_attr_name("columns"): columns,
        full_attr_name("from"): from_,
        full_attr_name("where"): where,
    }


output_dir = "measure_sql"

os.makedirs(output_dir, exist_ok=True)

measure_def_paths = sys.argv[1:]

with open("template.sql") as f:
    template = f.read()

for path in measure_def_paths:
    measure_id = os.path.basename(path).split(".")[0]
    with open(path) as f:
        measure_def = json.load(f)

    context = {}
    context.update(build_num_or_denom_fields(measure_def, "numerator"))
    context.update(build_num_or_denom_fields(measure_def, "denominator"))

    print(measure_id)

    with open(os.path.join(output_dir, measure_id + ".sql"), "w") as f:
        f.write(template.format(**context))
