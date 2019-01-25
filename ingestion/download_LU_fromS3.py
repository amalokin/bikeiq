import boto3


s3 = boto3.resource('s3')

content_object = s3.Object('sharedbikedata', 'Land_use/Tracts_Block_Groups_Only.tar')
file_content = content_object.get()['Body'].read()
tar = tarfile.open(file_content)