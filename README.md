# Critical Patches Alert

## Overview
The repository hold manifest for critical patches release alerts lambda. It will generate alert on slack if a new critical patch is relased and we haven't patched our instances.


## Details
1. Create an IAM role that will allow lambda to access ssm and ec2 permisions.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ssm:DescribeInstancePatchStates",
                "ssm:DescribeAvailablePatches"
            ],
            "Resource": "*"
        }
    ]
}
```
2. Create a lambda and assign that role to it.

```
NOTE

Do assign BasicLambdaExecution Policy, so that lambda can write it logs in cloudwatch.
```

3. Package this lambda by following these commands:

```bash
sudo pip3 install virtualenv 

# I have used python3.8, other versions can also be used that are supported by lambda
virtualenv -p python3.8 venv

# activate the virtual environment
source venv/bin/activate

# install packages
pip3 install -r requirements.txt

# deactivate the virtual environment
deactivate

# copy lambda_function.py to virtual environment's packages section
cp lambda_function.py venv/lib/<python-version>/site-packages/

# move inside virtual environment's packages section
cd venv/lib/<python-version>/site-packages

# archive the library contents
zip -r9 ${OLDPWD}/ssm-login-alerts.zip .

# move back to the directory
cd $OLDPWD
```

4. Upload the archive save it, there are two ways to do it

    1. direct upload(not recommended)
    2. upload to s3 and specify the path in the lambda.

5. Setup retention period for the cloudwatch logs

6. Configure these environment variables on lambda console

| Environment Variable | Description |
|---|---|
| SLACK_WEBHOOK | Slack channel webhook |


## Lambda Trigger
This Lambda will be triggered daily by CloudWatch EventBridge. To add it:
1. Click on Add Trigger
2. Under Trigger configuration select EventBridge (CloudWatch Events)
3. Then select a new Create a new rule
4. Then under Rule type select Schedule expression
5. Add this cron expression to trigger Lmabda function daily on weekdays at 9 AM UTC 
    * cron(0 9 ? * MON-FRI *)



