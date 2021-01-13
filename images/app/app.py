import json
import logging
import os
import subprocess
import time

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
  argsVers = ['get']
  try:
      print(event['rawPath'])
      getnamespaceList = event['rawPath'].split('/')
      if len(getnamespaceList) > 2:
         args = ['-n',getnamespaceList[2]] + argsVers + [trygetResource(getnamespaceList)]
         output = kubectl(args).decode('utf-8')[1:-1]
         return output
      elif len(getnamespaceList) <= 2:
         args = ['get' , 'pod' , '-A']
         output = kubectl(args).decode('utf-8')[1:-1]
         return output
  except:
      args = ['get' , 'pod' , '-A']
      output = kubectl(args).decode('utf-8')[1:-1]
      return output

  

def kubectl(args):
    retry = 3
    while retry > 0:
        try:
            cmd = [ 'kubectl', '--kubeconfig', kubeconfig ] + args
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            output = exc.output
            if b'i/o timeout' in output and retry > 0:
                logger.info("kubectl timed out, retries left: %s" % retry)
                retry = retry - 1
            else:
                raise Exception(output)
        else:
            logger.info(output)
            return output

def trygetResource(resourceList):
    resource = ['pod', 'svc', 'ns', 'deploy', 'namespaces', 'namespace', 'services', 'service']
    try:
        finalresource =  resourceList[3] if resourceList[3] in  resource  else 'pod'
        return finalresource
    except:
        print('not resource default pod')
        return 'pod'


def htmlHelper(x):
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
      <meta http-equiv="refresh" content="3">
    </head>
    <body>
    
    <h1>My EKS Cluster</h1>
    <p>{output}</p>
    
    </body>
    </html>
    '''.format(output=x)
    return html