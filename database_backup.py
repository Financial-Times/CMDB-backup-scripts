"""
    Simple script to enable CMDB database backups to be stored in S3
"""

#
# Import required modules
import boto3
import time
import os
import subprocess

def initEnvironment():
    """
        Initialise the environment
    """

    errorLocation = None
    errorReason = None
    dump_file_name = None
    missingVariables = []

    aws_access_key = os.getenv('CMDB_BACKUPS_AWS_ACCESS_KEY', None)
    aws_secret_key = os.getenv('CMDB_BACKUPS_AWS_SECRET_KEY', None)
    aws_bucket_name = os.getenv('CMDB_BACKUPS_AWS_BUCKET_NAME', None)
    aws_bucket_region = os.getenv('CMDB_BACKUPS_AWS_REGION', None)
    dump_file_name = os.getenv('CMDB_BACKUPS_NAMING', None)

    if aws_access_key != None and aws_secret_key != None and aws_bucket_name != None and aws_bucket_region != None and dump_file_name != None:
        local_file_name = dump_file_name.replace('{datetime}', 'LOCAL_BACKUP').replace('{extension}', 'psql')
    else:
        if aws_access_key == None:
            missingVariables.append('CMDB_BACKUPS_AWS_ACCESS_KEY')

        if aws_secret_key == None:
            missingVariables.append('CMDB_BACKUPS_AWS_SECRET_KEY')

        if aws_bucket_name == None:
            missingVariables.append('CMDB_BACKUPS_AWS_BUCKET_NAME')

        if aws_bucket_region == None:
            missingVariables.append('CMDB_BACKUPS_AWS_REGION')

        if backup_name == None:
            missingVariables.append('CMDB_BACKUPS_NAMING')

        errorLocation = 'Environment initialisation'
        errorReason = 'Missing/empty environment variables: ' + ', '.join(missingVariables)

    return errorLocation, {'aws_access_key' : aws_access_key,
                           'aws_secret_key' : aws_secret_key,
                           'aws_bucket_name' : aws_bucket_name,
                           'aws_bucket_region' : aws_bucket_region,
                           'dump_file_name' : dump_file_name,
                           'local_file_name' : local_file_name,
                           'errorReason' : errorReason}
# End - initEnvironment()

def createBackup(local_file_name):
    """
        Create backup and download to a local file
    """

    errorLocation = None
    errorReason = None

    dump_command = 'curl -o {local_file_name} `heroku pg:backups capture --app cmdb-test >/dev/null 2>&1 && heroku pg:backups public-url --app cmdb-test`'.replace('{local_file_name}', local_file_name)
    dump_proc = subprocess.Popen(dump_command, shell=True, stdout=subprocess.PIPE)
    (whoKnowsWhat, errors) = dump_proc.communicate()
    whoKnowsWhat = str(whoKnowsWhat).rstrip()
    dump_rc = dump_proc.returncode

    if dump_rc == 0:
        pass
    else:
        errorLocation = 'Backup creation'
        errorReason = 'Dump command ended with rc=' + str(dump_rc)

    return errorLocation, {'errorReason' : errorReason,
                           'local_file_name' : local_file_name}
# End - createBackup()

def uploadToS3(dump_file_name):
    """
        Upload file to S3
    """

    errorLocation = None
    errorReason = None

    backup_client = boto3.client(
        's3',
        aws_bucket_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    try:
         backup_client.upload_file(local_file_name, aws_bucket_name, dump_file_name)
    except Exception as exceptionDetails:
        errorLocation = 'Upload to S3'
        errorReason = 'AWS error code: ' + exceptionDetails.response['Error']['Code']
        
    return errorLocation, {'errorReason' : errorReason}
# End - uploadToS3()

if __name__ == '__main__':
    errorLocation, initEnvironment_values = initEnvironment()

    if errorLocation == None:
        #
        # Initialisation successful - create the backup
        local_file_name = initEnvironment_values['local_file_name']

        errorLocation, createBackup_values = createBackup(local_file_name)
        
        if errorLocation == None:
            #
            # Backup creation/download successful - upload the file to S3
            aws_access_key = initEnvironment_values['aws_access_key']
            aws_secret_key = initEnvironment_values['aws_secret_key']
            aws_bucket_name = initEnvironment_values['aws_bucket_name']
            aws_bucket_region = initEnvironment_values['aws_bucket_region']
            dump_file_name = initEnvironment_values['dump_file_name']

            dump_file_name = dump_file_name.replace('{datetime}', str(time.strftime("%Y-%m-%d-%H%M%S"))).replace('{extension}', 'psql')

            errorLocation, uploadToS3_values = uploadToS3(dump_file_name)

            if errorLocation == None:
                print('INFO: Database backup/upload completed successfully ('+dump_file_name+' in S3 bucket "'+aws_bucket_name+'")')
            else:
                errorReason = uploadToS3_values['errorReason']
        else:
            errorReason = createBackup_values['errorReason']
    else:
        errorReason = initEnvironment_values['errorReason']

    if errorLocation != None:
        #
        # Error has occurred - print details
        print('Error occurred during "%s" (%s)' % (errorLocation, errorReason))
