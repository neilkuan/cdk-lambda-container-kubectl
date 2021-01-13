import * as path from 'path';
import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2';
import * as _lambda_integ from '@aws-cdk/aws-apigatewayv2-integrations';
import * as iam from '@aws-cdk/aws-iam';
import * as _lambda from '@aws-cdk/aws-lambda';
import * as cdk from '@aws-cdk/core';

export class MyStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props: cdk.StackProps = {}) {
    super(scope, id, props);
    const customAlpineECR = new _lambda.DockerImageFunction(this, 'customAlpineECR', {
      code: _lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../images')),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      environment: {
        CLUSTER_ADMIN_ROLE_ARN: this.node.tryGetContext('CLUSTER_ADMIN_ROLE_ARN'),
        CLUSTER_NAME: this.node.tryGetContext('CLUSTER_NAME'),
      },
    });
    customAlpineECR.role?.addToPrincipalPolicy(new iam.PolicyStatement({
      actions: ['eks:DescribeCluster', 'sts:AssumeRole'],
      resources: ['*'],
    }));

    const app2 = new _lambda_integ.LambdaProxyIntegration({ handler: customAlpineECR });
    const api = new apigatewayv2.HttpApi(this, 'API');
    api.addRoutes({
      path: '/app',
      methods: [apigatewayv2.HttpMethod.GET],
      integration: app2,
    });
    api.addRoutes({
      path: '/app/{proxy+}',
      methods: [apigatewayv2.HttpMethod.GET],
      integration: app2,
    });
    new cdk.CfnOutput(this, 'URL', { value: `${api.url!}` });
  }
}

const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new cdk.App();
new MyStack(app, 'imagecode', { env: devEnv });

app.synth();