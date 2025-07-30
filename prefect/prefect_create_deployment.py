"""
Prefect Deployment YAML Generator

This script recursively searches through a local project directory structure for any folders named 'src'
and generates Prefect deployment YAML files for each Python module found within.

Each deployment YAML file includes:
- Project and deployment metadata
- Entry point to the flow (`module.py:function`)
- Work pool and scheduling configuration
- Source path mapping for deployment context

It supports templated scheduling and entrypoint formatting to match Prefect 2/3 conventions.

Generated YAML files are written to:
    d:/exports/prefect_jobs/

Environment Assumptions:
- Prefect version is hardcoded (default: 3.0.1)
- Source directory mappings between local and containerized paths are hardcoded
- Each `.py` file in a `src/` folder is treated as a flow module

"""

import os
import re
from pathlib import Path

prefect_version = "3.0.1"  # ie. '3.0.1' # str

src_root = "/prefect/src"  # str
local_root = "d:/Git/thinkstack_data_etl/src"  # str
src_folder = f"{local_root}/src"  # str
output_folder = "d:/exports/prefect_jobs"  # str


def create_deployment_yaml(
        project_name: str = "undefined",
        project_dir: str = "staging/api/undefined",
        deployment_name: str = "undefined",
        entrypoint: str = "module.py:function",
        worker_pool: str = "default-worker-pool",
        schedule_interval: float = 3600.0,
        schedule_timezone: str = "UTC",
        schedule_active: str = 'true'
) -> None:
    """
    Generates a Prefect deployment YAML file based on given project parameters.

    Args:
        project_name (str): Name of the project (used as the top-level identifier in Prefect Cloud).
        project_dir (str): Relative project directory path (used for build context if needed).
        deployment_name (str): Name of the deployment (also used in the filename).
        entrypoint (str): Python file and function defining the flow (e.g., 'main.py:flow_fn').
        worker_pool (str): Name of the Prefect work pool for executing flows.
        schedule_interval (float): Interval in seconds between flow runs.
        schedule_timezone (str): Timezone string for the schedule (e.g., 'UTC').
        schedule_active (str): Whether the schedule is active ('true' or 'false').

    Behavior:
        - Creates a directory for exporting YAML if it doesn't exist.
        - Builds a Prefect-compliant deployment file with the schedule and work pool settings.
        - Writes the YAML to the output folder using the deployment name.

    Output:
        A YAML file written to: {output_folder}/{deployment_name}-deploy.yaml
    """

    # prefect.yaml body template
    yaml_body = f"""# Welcome to your prefect.yaml file! You can use this file for storing and managing
# configuration for deploying your flows. We recommend committing this file to source
# control along with your flow code.

# Generic metadata about this project
name: {project_name}
prefect-version: {prefect_version}

# build section allows you to manage and build docker images
build: null

# push section allows you to manage if and how this project is uploaded to remote locations
push: null

# pull section allows you to provide instructions for cloning this project in remote locations
pull:
- prefect.deployments.steps.set_working_directory:
    directory: {src_root}

# the deployments section allows you to provide configuration for deploying flows
deployments:
- name: {deployment_name}
  version: null
  tags: []
  concurrency_limit: null
  description: null
  entrypoint: {entrypoint}
  parameters: {{ }}
  work_pool:
    name: {worker_pool}
    work_queue_name: null
    job_variables: {{ }}
enforce_parameter_schema: true
schedules:
- interval: {schedule_interval}
  anchor_date: '2024-01-01T01:00:00+00:00'
  timezone: {schedule_timezone}
  active: {schedule_active}
  max_active_runs: null
  catchup: false
""".lstrip()

    # Create the directory if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    # Create the deployment directory if it doesn't exist
    # Path(f"{output_folder}/{deployment_name}").mkdir(parents=True, exist_ok=True)

    # Write the yaml file    
    with open(f"{output_folder}/{deployment_name}-deploy.yaml", "w") as f:
        f.write(yaml_body)


for root, dirs, files in os.walk(local_root):
    for d in dirs:
        if d == 'src':
            for file in os.listdir(f"{root}/{d}"):
                if file.endswith(".py"):
                    deployment = file.split(".")[0]
                    print(f"Creating deployment for {deployment}")
                    create_deployment_yaml(
                        project_name=os.path.basename(root),
                        project_dir=f"{root}/{d}".replace("\\", "/").replace(local_root, src_root),
                        deployment_name=deployment,
                        entrypoint= \
                            f"{root}/{d}/{deployment}.py:{deployment}".replace("\\", "/").replace(local_root, src_root),
                        worker_pool="default-worker-pool",
                        schedule_interval=3600.0,  # 1 hour
                        schedule_timezone="UTC",  # UTC timezone
                        schedule_active='true'  # Active schedule
                    )
        else:
            # print(f'{d} is not src!')
            continue
