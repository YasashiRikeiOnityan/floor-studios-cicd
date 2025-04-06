import boto3
import os
import time
import logging

# AWSリソース
cloudfront = boto3.client('cloudfront')
codepipeline = boto3.client('codepipeline')

# 環境変数
distribution_id = os.environ['DISTRIBUTION_ID']

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Lambda function started.")
    logger.info(f"Event: {event}")

    job_id = event['CodePipeline.job']['id']

    try:
        # キャッシュを削除する
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': str(time.time())
            }
        )

        logger.info("Cache invalidation completed successfully.")

        # CloudFrontのレスポンスを確認
        # キャッシュ削除が完了したかまでは確認しない
        if response['ResponseMetadata']['HTTPStatusCode'] != 201:
            raise Exception("CloudFront invalidation failed.")

        # CodePipelineに完了を伝達する
        codepipeline.put_job_success_result(jobId=job_id)

    except Exception as e:
        logger.error(f"Error during cache invalidation: {str(e)}")

        # CodePipelineに失敗を伝達する
        codepipeline.put_job_failure_result(
            jobId=job_id,
            failureDetails={
                'type': 'JobFailed',
                'message': str(e)
            }
        )
