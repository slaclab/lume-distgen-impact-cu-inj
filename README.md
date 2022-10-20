# LUME Distgen Impact Cu Inj

This repository packages the `LumeDistgenImpactCuInj` in `lume_distgen_impact_cu_inj/model.py ` for execution with [Prefect](https://docs.prefect.io/) using the flow described in `lume_distgen_impact_cu_inj/flow/flow.py` using the variables:

<!--- The input and output variable tables are replaced when generating the project in template/hooks/post_gen_project.py-->
# input_variables
|      variable name      | type |default|
|-------------------------|------|------:|
|SOL1:solenoid_field_scale|scalar|      0|
|CQ01:b1_gradient         |scalar|      0|
|SQ01:b1_gradient         |scalar|      0|
|L0A_phase:dtheta0_deg    |scalar|      0|
|L0B_phase:dtheta0_deg    |scalar|      0|
|L0A_scale:voltage        |scalar|      0|
|L0B_scale:voltage        |scalar|      0|
|QA01:b1_gradient         |scalar|      0|
|QA02:b1_gradient         |scalar|      0|
|QE01:b1_gradient         |scalar|      0|
|QE02:b1_gradient         |scalar|      0|
|QE03:b1_gradient         |scalar|      0|
|QE04:b1_gradient         |scalar|      0|


# output_variables
|        variable_name         | type |
|------------------------------|------|
|end_t                         |scalar|
|end_mean_z                    |scalar|
|end_moment4_x                 |scalar|
|end_moment4_y                 |scalar|
|end_moment4_z                 |scalar|
|end_loadbalance_min_n_particle|scalar|
|end_loadbalance_max_n_particle|scalar|
|end_n_particle                |scalar|
|end_norm_emit_z               |scalar|
|end_moment3_x                 |scalar|
|end_moment3_y                 |scalar|
|end_moment3_z                 |scalar|
|end_mean_y                    |scalar|
|end_sigma_y                   |scalar|
|end_norm_emit_y               |scalar|
|end_mean_x                    |scalar|
|end_sigma_x                   |scalar|
|end_norm_emit_x               |scalar|
|end_max_amplitude_x           |scalar|
|end_max_amplitude_y           |scalar|
|end_max_amplitude_z           |scalar|
|end_mean_gamma                |scalar|
|end_mean_beta                 |scalar|
|end_max_r                     |scalar|
|end_sigma_gamma               |scalar|
|end_moment4_px                |scalar|
|end_moment4_py                |scalar|
|end_moment4_pz                |scalar|
|end_mean_pz                   |scalar|
|end_sigma_pz                  |scalar|
|end_cov_z__pz                 |scalar|
|end_moment3_px                |scalar|
|end_moment3_py                |scalar|
|end_moment3_pz                |scalar|
|end_mean_py                   |scalar|
|end_sigma_py                  |scalar|
|end_cov_y__py                 |scalar|
|end_mean_px                   |scalar|
|end_sigma_px                  |scalar|
|end_cov_x__px                 |scalar|
|end_max_amplitude_px          |scalar|
|end_max_amplitude_py          |scalar|
|end_max_amplitude_pz          |scalar|
|end_mean_kinetic_energy       |scalar|
|run_time                      |scalar|
|end_n_particle_loss           |scalar|
|end_total_charge              |scalar|
|end_higher_order_energy_spread|scalar|
|end_norm_emit_xy              |scalar|
|end_norm_emit_4d              |scalar|



## Installation

This package may be installed using pip:
```
pip install git+https://github.com/jacquelinegarrahan/lume-distgen-impact-cu-inj
```


## Dev

Install dev environment:
```
conda env create -f dev-environment.yml
```

Activate your environment:
```
conda activate lume-distgen-impact-cu-inj-dev
```

Install package:
```
pip install -e .
```

Tests can be executed from the root directory using:
```
pytest .
```

### Note
This README was automatically generated using the template defined in https://github.com/slaclab/lume-services-model-template with the following configuration:

```json
{
    "author": "Jacqueline Garrahan",
    "email": "jacquelinegarrahan@gmail.com",
    "github_username": "jacquelinegarrahan",
    "github_url": "https://github.com/slaclab/lume-distgen-impact-cu-inj",
    "project_name": "LUME Distgen Impact Cu Inj", 
    "repo_name": "lume-distgen-impact-cu-inj", 
    "package": "lume_distgen_impact_cu_inj",
    "model_class": "ImpactModel"
}
```
