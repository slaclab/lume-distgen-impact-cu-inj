from pkg_resources import resource_filename
from lume_model.utils import variables_from_yaml
import pandas as pd

IMPACT_VARIABLE_FILE =resource_filename(
    "lume_distgen_impact_cu_inj.files", "variables.yml"
)

DISTGEN_VARIABLE_FILE =resource_filename(
    "lume_distgen_impact_cu_inj.files", "distgen_variables.yml"
)

DEFAULT_VCC_ARRAY_FILE =resource_filename(
    "lume_distgen_impact_cu_inj.files", "default_vcc_array.npy"
)


DISTGEN_INPUT_FILE = resource_filename(
    "lume_distgen_impact_cu_inj.files", "distgen.yml"
)

IMPACT_ARCHIVE_FILE =  resource_filename(
    "lume_distgen_impact_cu_inj.files", "archive.h5"
)


CU_INJ_MAPPING = resource_filename(
    "lume_distgen_impact_cu_inj.files", "cu_inj_impact.csv"
)
