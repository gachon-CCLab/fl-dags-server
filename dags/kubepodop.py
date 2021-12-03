from datetime import datetime, timedelta

from kubernetes.client import models as k8s
from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.kubernetes.secret import Secret
from airflow.kubernetes.pod import Resources
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

dag_id = 'kubernetes-dag'

task_default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2020, 11, 21),
    'depends_on_past': False,
    'email': ['hoo0681@naver.com'],
    'email_on_retry': False,
    'email_on_failure': False,
    'execution_timeout': timedelta(hours=1)
}

dag = DAG(
    dag_id=dag_id,
    description='kubernetes pod operator',
    default_args=task_default_args,
    schedule_interval='5 16 * * *',
    max_active_runs=1
)

env = Secret(
    'env',
    'TEST',
    'test_env',
    'TEST',
)

pod_resources = Resources()
pod_resources.request_cpu = '1000m'
pod_resources.request_memory = '2048Mi'
pod_resources.limit_cpu = '2000m'
pod_resources.limit_memory = '4096Mi'


configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='secret')),
]

start = DummyOperator(task_id="start", dag=dag)

run = KubernetesPodOperator(
    task_id="kubernetespodoperator",
    namespace='fed-play-ground',
    image="ubuntu:16.04",
    cmds=["bash", "-cx"],
    arguments=["echo", "10", "echo pwd"],
    #secrets=[
    #    env
    #],
    #image_pull_secrets=[k8s.V1LocalObjectReference('image_credential')],
    name="job",
    is_delete_operator_pod=True,
    get_logs=True,
    resources=pod_resources,
    #env_from=configmaps,
    dag=dag,
)

start >> run