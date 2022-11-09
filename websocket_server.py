
from google.cloud import speech
import os
import traceback


os.environ["GOOGLE_CLOUD_PROJECT"] ='' #The GCP project ID
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ='./gcp_config.json' #configuration file
from google.auth import aws
import logging


LOG = logging.getLogger(__name__)

json_config_info = {
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/337957535543/locations/global/workloadIdentityPools/awspool/providers/awsdata",
  "subject_token_type": "urn:ietf:params:aws:token-type:aws4_request",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "environment_id": "aws1",
    "region_url": "http://169.254.169.254/latest/meta-data/placement/availability-zone",
    "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials",
    "regional_cred_verification_url": "https://sts.{region}.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15"
  },
  "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/test-king@gcp-subtitles.iam.gserviceaccount.com:generateAccessToken"
}

credentials = aws.Credentials.from_info(json_config_info)
print("Start init")
client = None
try:
    client = speech.SpeechClient(credentials=credentials)

    print("Finish init 0")

    gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
except Exception as ex:
    print("exception")
    print(ex.args)
    print(traceback.format_exc())
print("Finish init")
print("----------------------------------------------------")

