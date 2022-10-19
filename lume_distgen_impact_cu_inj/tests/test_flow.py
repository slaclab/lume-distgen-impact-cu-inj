from lume_distgen_impact_cu_inj.flow import flow, impact_output_variables, archive_file_rep
from datetime import datetime
import os
import numpy as np
from lume_distgen_impact_cu_inj import DEFAULT_VCC_ARRAY

def test_flow_execution(tmp_path):
    # format inputs
    dir_path=tmp_path
    vcc_array = DEFAULT_VCC_ARRAY

    distgen_input_values = {
        "vcc_resolution" : 9,
        "vcc_resolution_units" : "um",
        "vcc_size_y" : 480,
        "vcc_size_x": 640,
        "vcc_array": vcc_array.tolist(), # neet to convert to json serializable input for passed data
        "total_charge": 1.51614e+09
    }

    distgen_configuration = {}
    distgen_settings = {
        'n_particle': 10000,
        "t_dist:length:value":  4 * 1.65   #  Inferred pulse stacker FWHM: 4 ps, converted to tukey length
    }


    workdir = tmp_path
    pv_collection_isotime = datetime.now()

    # in this case, will be using conda installation of impact
    command="ImpactTexe"
    command_mpi=""
    use_mpi=False
    mpi_run="mpirun -n {nproc} --use-hwthread-cpus {command_mpi}"

    impact_configuration = {
        "command": command,
        "command_mpi": command_mpi,
        "use_mpi": use_mpi,
        "workdir": str(workdir),
        "mpi_run": mpi_run
    }

    impact_settings = {
        "header:Nx": 32,
        "header:Ny": 32,
        "header:Nz": 32,
        "stop": 16.5,
        #  "stop": 8,
        "numprocs": 1,
        "timeout": 1000,
        "total_charge": 0, # for debugging
    }


    impact_inputs = {"SOL1:solenoid_field_scale": 0.47235,
                    "CQ01:b1_gradient":  -0.00133705,
                    "SQ01:b1_gradient": 0.000769202,
                    "L0A_phase:dtheta0_deg": 0,
                    "L0B_phase:dtheta0_deg": -2.5,
                    "L0A_scale:voltage": 58,
                    "L0B_scale:voltage": 69.9586,
                    "QA01:b1_gradient": -3.25386,
                    "QA02:b1_gradient": 2.5843,
                    "QE01:b1_gradient": -1.54514,
                    "QE02:b1_gradient": -0.671809,
                    "QE03:b1_gradient": 3.22537,
                    "QE04:b1_gradient": -3.20496,
    }

    flow.set_reference_tasks([impact_output_variables])

    flow_run = flow.run(
        dashboard_dir = dir_path, 
        pv_collection_isotime=pv_collection_isotime, 
        impact_configuration=impact_configuration, 
        impact_settings=impact_settings, 
        distgen_output_filename= f"{tmp_path}/distgen.txt",
        distgen_configuration=distgen_configuration, 
        distgen_settings=distgen_settings,
        archive_filesystem_identifier="local",
        dashboard_image_filesystem_identifier="local",
        archive_dir = dir_path,
        **distgen_input_values, **impact_inputs
    )
    assert flow_run.is_successful()
