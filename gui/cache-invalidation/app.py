import boto3
import os
import time

# AWSリソース
cloudfront = boto3.client('cloudfront')
codepipeline = boto3.client('codepipeline')

# 環境変数
distribution_id = os.environ['DISTRIBUTION_ID']

def lambda_handler(event, context):    
    try:
        # キャッシュを削除する
        cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': str(time.time())
            }
        )

        # CodePipelineに完了を伝達する
        codepipeline.put_job_success_result(jobId = event['CodePipeline.job']['id'])

        return {'statusCode': 200}

    except Exception:
        # CodePipelineに失敗を伝達する
        codepipeline.put_job_failure_result(jobId = event['CodePipeline.job']['id'])

        return {'statusCode': 500}
