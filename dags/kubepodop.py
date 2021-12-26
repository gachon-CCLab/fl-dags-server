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
    'start_date': datetime(2021, 12, 3),
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
pod_resources.limit_gpu = '1'


configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='secret')),
]

start = DummyOperator(task_id="start", dag=dag)
port = k8s.V1ContainerPort(container_port=8080)

run = KubernetesPodOperator(
    task_id="kubernetespodoperator",
    namespace='fed-play-ground',
    image='docker.io/hoo0681/airflowkubepodimage:0.1',
    #cmds=["python3"],
    #arguments=["/app/app.py"],
    ports=[port],
    labels={'run':'fl-server'},
    env_vars={'REPO_URL':'https://github.com/hoo0681/portoFLSe.git',
              "GIT_TAG":"master"  },
    #secrets=[
    #    env
    #],
    #image_pull_secrets=[k8s.V1LocalObjectReference('image_credential')],
    name="fl-server",
    is_delete_operator_pod=True,
    get_logs=True,
    resources=pod_resources,
    #env_from=configmaps,
    dag=dag,
)
##################################

pod_resources1 = Resources()
pod_resources1.request_cpu = '1000m'
pod_resources1.request_memory = '2048Mi'
pod_resources1.limit_cpu = '2000m'
pod_resources1.limit_memory = '4096Mi'
env1 = Secret(
    deploy_type='env',
    deploy_target='ACCESS_KEY_ID',
    secret='s3secret',
    key='ACCESS_KEY_ID',
)
env2 = Secret(
    deploy_type='env',
    deploy_target='ACCESS_SECRET_KEY',
    secret='s3secret',
    key='ACCESS_SECRET_KEY',
)
env3 = Secret(
    deploy_type='env',
    deploy_target='BUCKET_NAME',
    secret='s3secret',
    key='BUCKET_NAME',
)
model_init=KubernetesPodOperator(
    task_id="kubernetespodoperator",
    namespace='fed-play-ground',
    image='docker.io/hoo0681/gitclone_python:0.1',
    labels={'run':'fl-server-model-init'},
    env_vars={'REPO_URL':'https://github.com/hoo0681/portoFLClient.git',
              "GIT_TAG":"master",
              "ENV": 'init' },
    name="fl-server-model-init",
    is_delete_operator_pod=True,
    get_logs=True,
    resources=pod_resources1,
    dag=dag,
    secret=[env1,env2,env3]
)

start >>model_init>> run