from typing import Dict

from prefect import Flow, task, case
from prefect import Parameter, DateTimeParameter
import os
import numpy as np
from lume_services.results import Result
from lume_services.tasks import (
    configure_lume_services,
    prepare_lume_model_variables,
    check_local_execution,
    SaveDBResult,
    LoadDBResult,
    LoadFile,
    SaveFile,
)
from lume_services.files import HDF5File, ImageFile, TextFile
from lume_model.variables import InputVariable, OutputVariable
from prefect.storage import Module
from prefect.core.parameter import DateTimeParameter
from lume_distgen_impact_cu_inj.model import ImpactModel, DistgenModel, LUMEConfiguration
from lume_distgen_impact_cu_inj.dashboard import make_dashboard

from lume_distgen_impact_cu_inj.files import IMPACT_ARCHIVE_FILE, DISTGEN_INPUT_FILE

from lume_distgen_impact_cu_inj import (
    CU_INJ_MAPPING_TABLE,
    IMPACT_INPUT_VARIABLES,
    DISTGEN_INPUT_VARIABLES
)

PREFECT__CONTEXT__FLOW_ID = os.environ.get("PREFECT__CONTEXT__FLOW_ID", "local")


@task(log_stdout=True)
def distgen_preprocessing_task(input_variables):

    # scale all values w.r.t. impact factor
    for var_name, variable in input_variables.items():

        # downcast
        if var_name == "vcc_array":
            value = np.array(variable.value)
            value = value.astype(np.int8)

            if value.ptp() == 0:
                raise ValueError(f"EPICS get for vcc_array has zero extent")

            variable.value = value

        # make units consistent
        if var_name == "vcc_resolution_units":
            if variable.value == "um/px":
                variable.value = "um"

        if var_name == "total_charge":
            scaled_val = (
                variable.value
                * CU_INJ_MAPPING_TABLE.loc[
                    CU_INJ_MAPPING_TABLE["impact_name"] == "distgen:total_charge:value", "impact_factor"
                ].item()
            )
            variable.value = scaled_val

    return input_variables


@task(log_stdout=True)
def impact_preprocessing_task(input_variables):

    # scale all values w.r.t. impact factor
    for var_name, variable in input_variables.items():

        if (
            CU_INJ_MAPPING_TABLE["impact_name"]
            .str.contains(var_name, regex=False)
            .any()
        ):
            scaled_val = (
                variable.value
                * CU_INJ_MAPPING_TABLE.loc[
                    CU_INJ_MAPPING_TABLE["impact_name"] == var_name, "impact_factor"
                ].item()
            )

            variable.value = scaled_val

    return input_variables


@task(log_stdout=True, nout=2)
def evaluate_distgen(
    distgen_configuration,
    distgen_input_filename,
    distgen_settings,
    distgen_output_filename,
    distgen_input_variables,
):

    configuration = LUMEConfiguration(**distgen_configuration)
    distgen_model = DistgenModel(
        input_file=DISTGEN_INPUT_FILE,
        configuration=configuration,
        base_settings=distgen_settings,
        distgen_output_filename=distgen_input_filename,
    )

    output_variables = distgen_model.evaluate(distgen_input_variables)

    return (distgen_model.G, output_variables)


@task(log_stdout=True, nout=2)
def evaluate_impact(
    impact_archive_file,
    impact_configuration: dict,
    impact_settings: dict,
    input_variables,
    distgen_model,
):
    particles = distgen_model.particles
    impact_configuration = LUMEConfiguration(**impact_configuration)

    model = ImpactModel(
        archive_file=impact_archive_file,
        configuration=impact_configuration,
        base_settings=impact_settings,
    )
    output_variables = model.evaluate(list(input_variables.values()), particles)

    return (model.I, output_variables)




@task(log_stdout=True)
def create_dashboard(pv_collection_isotime, impact_I):
    DASHBOARD_KWARGS = {
            'screen1': 'YAG02',
            'screen2': 'YAG03',
            'screen3': 'OTR2',
            'ylim' : (0, 2e-6), # Emittance scale                        
            'name' : f"{PREFECT__CONTEXT__FLOW_ID}_{pv_collection_isotime}"
        }

    return make_dashboard(impact_I, itime=pv_collection_isotime, **DASHBOARD_KWARGS)


@task(log_stdout=True)
def format_result(pv_collection_isotime, impact_settings, impact_input_variables, impact_configuration, impact_output_variables, dashboard_file, archive_file):

    impact_settings.update(
        {var_name: var.value for var_name, var in impact_input_variables.items()}
    )

    # output vars second item in tuple
    impact_outputs = {var_name: var.value for var_name, var in impact_output_variables.items()}

    return ImpactResult(
        inputs=impact_settings,
        outputs=impact_outputs,
        plot_file=dashboard_file,
        archive= archive_file,
        pv_collection_isotime= pv_collection_isotime,
        config= impact_configuration
    )

# DEFINE TASK FOR SAVING DB RESULT
# See docs: https://slaclab.github.io/lume-services/api/tasks/#lume_services.tasks.db.SaveDBResult
save_db_result_task = SaveDBResult(timeout=30)

# DEFINE TASK FOR SAVING FILE
# See docs: https://slaclab.github.io/lume-services/api/tasks/#lume_services.tasks.file.SaveFile
save_dashboard_image_task = SaveFile(parameter_base="dashboard_image", timeout=30)
save_archive_file_task = SaveFile(parameter_base="archive")
save_distgen_file_task = SaveFile(parameter_base="distgen")

@task
def format_archive_filename(pv_collection_isotime, archive_dir):
    return f"{archive_dir}/{PREFECT__CONTEXT__FLOW_ID}_{pv_collection_isotime}.h5"


@task
def format_dashboard_filename(pv_collection_isotime, dashboard_dir):
    return f"{dashboard_dir}/{PREFECT__CONTEXT__FLOW_ID}_{pv_collection_isotime}.png"


with Flow("lume-distgen-impact-cu-inj", storage=Module(__name__)) as flow:

    # CONFIGURE LUME-SERVICES
    # see https://slaclab.github.io/lume-services/workflows/#configuring-flows-for-use-with-lume-services
    configure = configure_lume_services()

    # CHECK WHETHER THE FLOW IS RUNNING LOCALLY
    # If the flow runs using a local backend, the results service will not be available
    running_local = check_local_execution()

    # SET UP INPUT VARIABLE PARAMETERS.
    distgen_input_variable_parameter_dict = {
        var_name: Parameter(var_name, default=var.default.tolist()) if isinstance(var.default, np.ndarray) else Parameter(var_name, default=var.default)
        for var_name, var in DISTGEN_INPUT_VARIABLES.items()
    }

    impact_input_variable_parameter_dict = {
        var_name: Parameter(var_name, default=var.default)
        for var_name, var in IMPACT_INPUT_VARIABLES.items()
    }

    # other parameters

    # This could be parsed out to be two distinct models, but here we're assuming distgen output/input not saved globally
    distgen_input_filename = Parameter("distgen_input_filename", default=DISTGEN_INPUT_FILE)

    distgen_output_filename = Parameter("distgen_output_filename", default="/tmp/laser.txt")

    # The impact init from archive in the model.py could be completely substituted 
    # if file was saved with the updated 
    # LUME-base serializer https://github.com/slaclab/lume-base/blob/8c548e11672abce3a0cfc22b970b343d46ddba42/lume/serializers/hdf5.py#L15
    # In this case, we could load the entire model using:
    #  h5_file = HDF5File(filename="/Users/jacquelinegarrahan/sandbox/lume-distgen-impact-cu-inj/lume_distgen_impact_cu_inj/files/archive.h5", filesystem_identifier="local")
    #I = h5_file.load_file()
    # and pass I during ImpactModel init

    impact_init_archive_filename = Parameter("impact_archive_filename", default=IMPACT_ARCHIVE_FILE)


    dashboard_dir = Parameter("dashboard_dir")
    archive_dir = Parameter("archive_dir")

    distgen_settings = Parameter("distgen_settings")
    distgen_configuration = Parameter("distgen_configuration")
    impact_configuration = Parameter("impact_configuration")
    impact_settings = Parameter("impact_settings")
    pv_collection_isotime = DateTimeParameter("pv_collection_isotime")

    # ORGANIZE INPUT VARIABLE VALUES LUME-MODEL VARIABLES
    formatted_distgen_input_vars = prepare_lume_model_variables(
        distgen_input_variable_parameter_dict, DISTGEN_INPUT_VARIABLES
    )

    prepared_distgen_input_vars = distgen_preprocessing_task(formatted_distgen_input_vars)

    formatted_impact_input_vars = prepare_lume_model_variables(
        impact_input_variable_parameter_dict, IMPACT_INPUT_VARIABLES
    )

    prepared_impact_input_vars = impact_preprocessing_task(formatted_impact_input_vars)

    distgen_G, distgen_output_variables = evaluate_distgen(
        distgen_configuration,
        distgen_input_filename,
        distgen_settings,
        distgen_output_filename,
        prepared_distgen_input_vars
    )

    impact_I, impact_output_variables = evaluate_impact(
        impact_init_archive_filename,
        impact_configuration,
        impact_settings,
        prepared_impact_input_vars,
        distgen_G
    )

    # dashbard file
    dashboard_file_parameters = save_dashboard_image_task.parameters
    dashboard_img = create_dashboard(pv_collection_isotime, impact_I)
    dashboard_filename = format_dashboard_filename(pv_collection_isotime, dashboard_dir)
    dashboard_file_rep = save_dashboard_image_task(dashboard_img, file_type=ImageFile, filename=dashboard_filename, filesystem_identifier=dashboard_file_parameters["filesystem_identifier"])
    dashboard_file_rep.set_upstream(configure)

    # archive file
    archive_file_parameters = save_archive_file_task.parameters
    archive_filename = format_archive_filename(pv_collection_isotime, archive_dir)
    archive_file_rep = save_archive_file_task(impact_I, file_type=HDF5File,
    filename=archive_filename, filesystem_identifier=archive_file_parameters["filesystem_identifier"])
    archive_file_rep.set_upstream(configure)

    # SAVE RESULTS TO RESULTS DATABASE, requires LUME-services results backend 
    with case(running_local, False):
        # CREATE LUME-services Result object
        formatted_result = format_result(pv_collection_isotime, impact_settings, prepared_impact_input_vars, impact_configuration, impact_output_variables, dashboard_file_rep, archive_file_rep
        )

        # RUN DATABASE_SAVE_TASK
        saved_model_rep = save_db_result_task(formatted_result)
        saved_model_rep.set_upstream(configure)


def get_flow():
    return flow
