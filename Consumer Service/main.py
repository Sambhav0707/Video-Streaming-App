import boto3
import json
import urllib.parse
from secret_keys import Settings


"""
The main idea of this service is to poll from the SQS queue and based 
on that send something to ECS
"""
# creating the setting instance of Settings class
settings = Settings()
# creating a sqs client
sqs_client = boto3.client("sqs", region_name=settings.REGION_NAME)
# creating a ecs client
ecs_client = boto3.client("ecs", region_name=settings.REGION_NAME)

"""
Function to poll
"""


def poll_sqs():
    # creating a infinite loop to poll from the sqs queue
    print("Starting SQS Poller...")
    while True:
        response = sqs_client.receive_message(
            QueueUrl=settings.AWS_SQS_VIDEO_PROCESSING_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )
        if "Messages" not in response:
            continue
            
        print(f"Received {len(response['Messages'])} messages")
        # looping through Messages list in the reponse
        for message in response.get("Messages", []):
            try:
                # extracting the Body parameter
                raw_body = message.get("Body")
                print(f"Raw message body: {raw_body}")
                message_body = json.loads(raw_body)
                
                # S3 event notifications from EventBridge might be wrapped differently than direct S3 to SQS
                if "Message" in message_body and isinstance(message_body["Message"], str):
                    print("Unwrapping SNS/EventBridge message...")
                    message_body = json.loads(message_body["Message"])

                # deleting the test event
                if (
                    "Service" in message_body
                    and "Event" in message_body
                    and message_body.get("Event") == "s3:TestEvent"
                ):
                    print("Deleting test event")
                    sqs_client.delete_message(
                        QueueUrl=settings.AWS_SQS_VIDEO_PROCESSING_QUEUE_URL,
                        ReceiptHandle=message[
                            "ReceiptHandle"
                        ],  # ReceiptHandle is essential for identifying which message to delete
                    )
    
                    continue
    
                # extracting bucket name and s3_key from the original event
                if "Records" in message_body:
                    s3_record = message_body["Records"][0][
                        "s3"
                    ]  # we are checking the first element in Records bcz there will be only one element in that
    
                    bucket_name = s3_record["bucket"]["name"]
                    raw_s3_key = s3_record["object"]["key"]
                    s3_key = urllib.parse.unquote_plus(raw_s3_key)
                    
                    print(f"Extracted bucket: {bucket_name}, raw key: {raw_s3_key}, decoded key: {s3_key}. Launching ECS task...")
    
                    # spinning up a docker container on ECS Fargate
                response = ecs_client.run_task(
                    cluster=settings.ECS_CLUSTER_ARN,
                    launchType="FARGATE",
                    taskDefinition=settings.ECS_TASK_DEFINETION,
                    overrides={
                        # containerOverrides is used to pass dynamic data to the container at launch time.
                        # Here, we inject the specific S3_BUCKET_NAME and S3_KEY from the SQS message
                        # so the transcoder container knows exactly which video file it needs to process.
                        "containerOverrides": [
                            {
                                "name": "Video-Transcoder",
                                "environment": [
                                    {"name": "S3_BUCKET_NAME", "value": bucket_name},
                                    {"name": "S3_KEY", "value": s3_key},
                                ],
                            }
                        ]
                    },
                    # networkConfiguration is required for Fargate tasks because AWS needs to know
                    # where in your VPC to provision the underlying compute resources.
                    networkConfiguration={
                        "awsvpcConfiguration": {
                            # Subnets dictate which isolated network blocks the task runs in.
                            "subnets": [
                                "subnet-0e80ba9f9e87de4b1",
                                "subnet-024a74b6705722e09",
                                "subnet-04d7b47ee1835af1b",
                            ],
                            # assignPublicIp ENABLED is needed if using public subnets so the container
                            # can reach the internet (e.g., to pull the Docker image, talk to S3/SQS).
                            "assignPublicIp": "ENABLED",
                            # Security Groups act as a firewall, controlling inbound/outbound traffic.
                            "securityGroups": ["sg-0de299120d8347552"],
                        }
                    },
                )

                print(response)
                sqs_client.delete_message(
                    QueueUrl=settings.AWS_SQS_VIDEO_PROCESSING_QUEUE_URL,
                    ReceiptHandle=message[
                        "ReceiptHandle"
                    ],  # ReceiptHandle is essential for identifying which message to delete
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                # Don't delete the message so it can be retried or put in a DLQ
                continue

poll_sqs()
