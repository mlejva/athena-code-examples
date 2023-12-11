import os
import boto3

session = boto3.Session()

s3 = session.resource('s3')

bucket_name = os.environ['S3_BUCKET_NAME']
bucket = s3.Bucket('e2b-sandbox-bucket')

for obj in bucket.objects.all():
  print(obj.key, obj.last_modified)

def write_file(path, content):
  bucket.put_object(Key=path, Body=content)

def read_file(path):
  obj = bucket.Object(path)
  return obj.get()['Body'].read().decode('utf-8')

def list_dir(path):
  return [obj.key for obj in bucket.objects.filter(Prefix=path)]