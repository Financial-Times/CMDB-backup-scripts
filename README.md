# Repository containing the script(s) for taking backups of the CMDB database and storing them in S3


## Prerequsites

Heroku toolbelt
python                     (v3 untested, v2 proved)
boto3                      (install using "pip install boto3")


## Configuration

Define AWS requirements (credentials/region/S3 bucket name) and format for backup file name using environment variables: 
- CMDB_BACKUPS_NAMING
- CMDB_BACKUPS_AWS_BUCKET_NAME
- CMDB_BACKUPS_AWS_SECRET_KEY
- CMDB_BACKUPS_AWS_ACCESS_KEY
- CMDB_BACKUPS_AWS_REGION


## Execution

Run as a standalone python script (django is not required) via:


- python database_backup.py


## Output

The script will report the success/failure of the backup process


## CMDBv2

- For more information on CMDBv2 take a look at our [Google Site](https://sites.google.com/a/ft.com/technology/tools/cmdb-v2)
- For more information on how the stream is populated take a look at the [Stream Consumer page](https://sites.google.com/a/ft.com/technology/tools/cmdb-v2/streamed-changes)

--------------------------------------------------------------------

