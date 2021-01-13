import json
import logging
import os
import subprocess
import time
from kubernetes import client, config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


outdir = os.environ.get('TEST_OUTDIR', '/tmp')
kubeconfig = os.path.join(outdir, 'kubeconfig')
role_arn= os.environ.get('CLUSTER_ADMIN_ROLE_ARN')
cluster_name = os.environ.get('CLUSTER_NAME')
def handler(event, context):
  logger.info(json.dumps(event))
  # "log in" to the cluster
  subprocess.check_call([ 'aws', 'eks', 'update-kubeconfig',
      '--role-arn', role_arn,
      '--name', cluster_name,
      '--kubeconfig', kubeconfig
  ])
  config.load_kube_config(config_file=kubeconfig)
  output = kubectlgetall()
  return output

def kubectlgetall():
    v1 = client.CoreV1Api()
    ouput = "Listing pods with their IPs:"
    print(ouput)
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        tempoutput = "%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)
        print(tempoutput)
        ouput = ouput + '\n' + tempoutput
    return ouput