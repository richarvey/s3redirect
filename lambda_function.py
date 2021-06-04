import boto3, botocore
import base64
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.logging.logger import set_package_logger

set_package_logger()


# POWERTOOLS_SERVICE_NAME defined
tracer = Tracer(service="s3r")

def check_safeurl(url):
    ''' check url to make sure its not on a blocked list'''
    return false;


def get_UUID(url):
    ''' Takes URL encodes and strips'''
    urlSafeEncodedBytes = base64.urlsafe_b64encode(url.encode("utf-8"))
    urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8")
    y = ''.join(e for e in urlSafeEncodedStr if e.isalnum())
    return(y)

@tracer.capture_method
def check_object(s3, bucket, uuid, url, short_len, found_create):
    url_match = "false"
    try:
        response = s3.get_object(Bucket=bucket, Key=uuid[-short_len:])
        if response['WebsiteRedirectLocation'] == url:
            url_match = "true"
            found_create = "true"
            tracer.put_annotation(key="Status", value="HIT")
        else:
            short_len = short_len + 1
            tracer.put_annotation(key="Status", value="MISS")
    except:
        found_create = "true"
    
    return(short_len, url_match, found_create)

def create_redirect(s3, bucket, uuid, url, short_len):
    uuid = uuid[-short_len:]
    s3.put_object(ACL='public-read', Bucket=bucket, Body='0', Key=uuid, WebsiteRedirectLocation=url)

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    short_len = 6
    print(event)
    bucket = event['body-json']['BUCKET']
    is_safe = check_safeurl(event['body-json']['URL'])
    if is_safe == 'true':
      uuid = get_UUID(event['body-json']['URL'])
      found_create = "false"
      while (found_create == 'false'):
          short_len, url_match, found_create = check_object(s3, bucket, uuid, event['body-json']['URL'], short_len, found_create)
      if url_match == 'true':
          tracer.put_annotation(key="RETURN_Status", value="MATCH")
      if url_match == 'false':
          create_redirect(s3, bucket, uuid, event['body-json']['URL'], short_len)
          tracer.put_annotation(key="RETURN_Status", value="CREATE")
      return {
          'URL' : event['body-json']['URL'],
          'UUID' : uuid[-short_len:],
          'SHORT' : short_len,
          'URL_MATCH' : url_match,
          'ERROR' : false
      }
    else:
      tracer.put_annotation(key="RETURN_Status", value="ERROR")  
      return {
          'ERROR' : true
      }
