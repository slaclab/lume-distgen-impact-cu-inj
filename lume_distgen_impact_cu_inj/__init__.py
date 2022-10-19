from lume_distgen_impact_cu_inj.files import IMPACT_VARIABLE_FILE, DISTGEN_VARIABLE_FILE, CU_INJ_MAPPING, DEFAULT_VCC_ARRAY_FILE
from lume_model.utils import variables_from_yaml
import pandas as pd
import numpy as np

CU_INJ_MAPPING_TABLE= pd.read_csv(CU_INJ_MAPPING)
CU_INJ_MAPPING_TABLE.set_index("impact_name")

with open(IMPACT_VARIABLE_FILE, "r") as f:
    IMPACT_INPUT_VARIABLES, IMPACT_OUTPUT_VARIABLES = variables_from_yaml(f)


with open(DISTGEN_VARIABLE_FILE, "r") as f:
    DISTGEN_INPUT_VARIABLES, DISTGEN_OUTPUT_VARIABLES = variables_from_yaml(f)

DEFAULT_VCC_ARRAY = np.load(DEFAULT_VCC_ARRAY_FILE)
DISTGEN_INPUT_VARIABLES["vcc_array"].default = DEFAULT_VCC_ARRAY


from . import _version
__version__ = _version.get_versions()['version']
