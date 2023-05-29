from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.emr import EmrServerlessHook
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator
from airflow.providers.amazon.aws.sensors.emr import EmrServerlessJobSensor

from some_dags.functions import print_success


@dag(
    dag_id='my_dag',
    schedule_interval="@daily",
    start_date=datetime(2023, 5, 1),
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=10),
        'depends_on_past': True,
    },
    catchup=True,
    tags=["demo"],
)
def taskflow_job():
    @task()
    def start_job(**kwargs):
        start_job_task = EmrServerlessStartJobOperator(
            task_id="start_emr_serverless_job",
            application_id="my_application_id",
            execution_role_arn="my_role_arn",
            job_driver={
                "sparkSubmit": {
                    "sparkSubmitParameters": "--conf spark.submit.pyFiles=s3://artifacts_bucket/artefact/release/"
                    + "my_spark/package/some_modules_to_be_imported_in_your_pyspark_script.zip "
                    + "--conf spark.archives=s3://artifacts_bucket/artefact/release/"
                    + "my_spark/venv/pyspark_venv.tar.gz#environment "
                    + "--conf spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON=./environment/bin/python3 "
                    + "--conf spark.emr-serverless.driverEnv.PYSPARK_PYTHON=./environment/bin/python3 "
                    + "--conf spark.emr-serverless.executorEnv.PYSPARK_PYTHON=./environment/bin/python3",
                    "entryPoint": "s3://artifacts_bucket/artefact/release/my_spark/scripts/cluster_spark.py",
                    "entryPointArguments": [
                        "--input-bucket",
                        "in_bucket",
                        "--input-prefix",
                        "in/prefix/2022/01/04/",
                        "--output-bucket",
                        "out_bucket",
                        "--output-prefix",
                        "out/prefix/2022/01/03/",
                        "--sql-bucket",
                        "sql_bucket",
                        "--sql-key",
                        "sql/wow.sql",
                    ],
                }
            },
            configuration_overrides={
                "monitoringConfiguration": {"s3MonitoringConfiguration": {"logUri": "s3://log_bucket/log_prefix"}}
            },
        )
        job_id = start_job_task.execute(kwargs)
        return {'job_id': job_id}

    @task
    def wait_for_job(result_dict: dict, **kwargs):
        wait_for_job_task = EmrServerlessJobSensor(
            task_id="wait_for_job",
            application_id="my_application_id",
            job_run_id=result_dict['job_id'],
            target_states=EmrServerlessHook.JOB_SUCCESS_STATES,
            on_success_callback=print_success,
        )
        wait_for_job_task.execute(kwargs)

    wait_for_job(start_job())


etl_dag = taskflow_job()
