from epics import PV, dbr
import click
import time
from datetime import datetime
import os
import numpy as np
from functools import partial
from lume_services.models import Model
from lume_services.config import configure


PVNAME_TO_INPUT_MAP = {
    "SOLN:IN20:121:BACT": "SOL1:solenoid_field_scale",
    "QUAD:IN20:121:BACT": "CQ01:b1_gradient",
    "QUAD:IN20:122:BACT": "SQ01:b1_gradient",
    "ACCL:IN20:300:L0A_PDES": "L0A_phase:dtheta0_deg",
    "ACCL:IN20:400:L0B_PDES": "L0B_phase:dtheta0_deg",
    "ACCL:IN20:300:L0A_ADES": "L0A_scale:voltage",
    "ACCL:IN20:400:L0B_ADES": "L0B_scale:voltage",
    "QUAD:IN20:361:BACT": "QA01:b1_gradient",
    "QUAD:IN20:371:BACT": "QA02:b1_gradient",
    "QUAD:IN20:425:BACT": "QE01:b1_gradient",
    "QUAD:IN20:441:BACT": "QE02:b1_gradient",
    "QUAD:IN20:511:BACT": "QE03:b1_gradient",
    "QUAD:IN20:525:BACT": "QE04:b1_gradient",
    "CAMR:IN20:186:RESOLUTION" : "vcc_resolution",
    "CAMR:IN20:186:RESOLUTION.EGU" : "vcc_resolution_units",
    "CAMR:IN20:186:N_OF_ROW" : "vcc_size_y",
    "CAMR:IN20:186:N_OF_COL": "vcc_size_x",
    "CAMR:IN20:186:IMAGE": "vcc_array",
    "BPMS:IN20:221:TMIT":"total_charge"
}

IMPACT_CONFIGURATION = {
    "command": "ImpactTexe",
    "command_mpi": "",
    "use_mpi": False,
    "workdir": str(os.getcwd()),
    "mpi_run": "mpirun -n {nproc} --use-hwthread-cpus {command_mpi}"
}


DISTGEN_CONFIGURATION = {}
DISTGEN_SETTINGS = {
    'n_particle': 10000,
    "t_dist:length:value":  4 * 1.65   #  Inferred pulse stacker FWHM: 4 ps, converted to tukey length
}

IMPACT_SETTINGS = {
    "header:Nx": 32,
    "header:Ny": 32,
    "header:Nz": 32,
    "stop": 16.5,
    #  "stop": 8,
    "numprocs": 1,
    "timeout": 1000,
    "total_charge": 0, # for debugging
}


def monitor_callback(parameter_values, pv_collection_time, pvname, value, timestamp, **kwargs):
    pv_collection_time = timestamp
    if isinstance(value, np.ndarray):
        parameter_values[pvname] = value.tolist()

    else:
        parameter_values[pvname] = value


@click.command()
@click.argument("model_id")
@click.argument("deployment_id")
@click.argument("dashboard_dir")
@click.argument("archive_dir")
def main(model_id, deployment_id, dashboard_dir, archive_dir):
    global PVNAME_TO_INPUT_MAP, IMPACT_SETTINGS, DISTGEN_CONFIGURATION, IMPACT_CONFIGURATION, DISTGEN_SETTINGS

    configure()

    pvs = {}
    parameter_values = {
        "impact_configuration": IMPACT_CONFIGURATION, 
        "impact_settings": IMPACT_SETTINGS, 
        "distgen_configuration": DISTGEN_CONFIGURATION, 
        "distgen_settings": DISTGEN_SETTINGS,
        "archive_filesystem_identifier": "mounted",
        "dashboard_image_filesystem_identifier": "mounted",
        "archive_dir": archive_dir,
        "dashboard_dir": dashboard_dir, 
    }
    pv_collection_isotime = None

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        parameter_values[pvname] = None

    model = Model(model_id = model_id, deployment_id=deployment_id)

    pv_collection_isotime = datetime.now()

    for pvname in PVNAME_TO_INPUT_MAP.keys():
        pvs[pvname] = PV(pvname, auto_monitor=dbr.DBE_VALUE)
        pvs[pvname].add_callback(partial(monitor_callback, parameter_values,pv_collection_isotime))

    try:
        while True:
            time.sleep(0.1)
            print("Evaluating model...")
            # only queue model once all have values
            if not any([parameter_val is None for parameter_val in parameter_values.values()]):

                parameter_values["pv_collection_isotime"] = pv_collection_isotime.isoformat()

                # blocking call
                model.run_and_return(
                    parameters = parameter_values
                )
    except KeyboardInterrupt:
        for pv in pvs.values():
            pv.clear_auto_monitor()



if __name__ == "__main__":
    main()
