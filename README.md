# Bluecard

Bluecard is a a prototype ID scanning system.

It's designed to replace manual registration workflows, where a clerk is handed a license, and hand-types information contained on it.

##### Note: this is a prototype.  Portions of it are non-functional.  It is not ready for production use.

This project was created to:

1. Learn [Django](https://www.djangoproject.com/)
2. Explore Amazon's [AWS Lambda processing framework](http://aws.amazon.com/lambda/)
3. Experiment with the [Captricity](http://captricity.com) document processing API

### Workflow

Typically registration processes involve a clerk reading a license, and typing the information into an EHR or other proprietary system.

Instead the general workflow is:

1. The license is scanned or photographed by the clerk, or even by a provider or other care-giver
2. The license image is stored (in this case in an Amazon S3 bucket)
3. A program notices the new image and sends it to Captricity (Amazon Lambda)
4. Data is extracted and stored (Amazon RDS)

Ideally, the data would be extracted and stored by a seperate Lambda process, currently that is partially implemented in the Django layer.

The compute intensive portions of the app are almost entirely offloaded to Amazon and Captricity.

### Setup notes

Django expects a config file in config/config.cnf.  

Here's an example:

```
[django]
secret_key = mydjangosecret

[mysql]
database = bluecard
user = bluecard
password = mypassword
default-character-set = utf8
host = my-datastore-or-rds
port = 3306

[aws]
keyid = myamazon
key = key
bucket = 'bluecard'

[captricity]
apitoken = myapitoken
```

### Deploying the Lamda worker

The AWS lambda worker lives in the `aws-lambda` directory.

Deploying the lambda worker requires building and uploading a ZIP of the aws-lambda directory.  See the shell script `create-aws-package.sh`.  This would ideally be automated to avoid having to use the AWS GUI.

The script depends on `aws-lambda/config/config.cnf`, which can be identical to whats in the main config directory.
