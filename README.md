# Python Lambda AWS - ECS manager
AWS ECS deploying lambda function

## Project purpose
Simple boilerplate for deploying an ECS project modeled by a JSON object payload.
This is a base code and more options can be added to the JSON payload to fit the deployment needs
as commented in the code.

Given a cluster, service, container and image, it automatically detects the existence (or not) of any of them
and creates the needed changes to achieve the desired state, versioning the service's task definitions.


## Installation and local testing

Clone this project:
``` 
git clone 
```

Install python requirements for local testing if needed (it's better idea to have a Python venv for each project):
``` 
pip install -r requirements
```

With an AWS account configured in your actual user, run the function:
``` 
sh local_test.sh
```

As this is a simple boilerplate, and final code will depend on the event source implementation (S3 event, API Gateway, etc)
The handled exceptions and errors are printed via console and function is terminated with a return value of _**False**_


## Deployment

As Lambda EC2 AMIs in AWS already have Python and _boto3_ package,
you just need to upload the python code and make sure that function handler
is set to `lambda_handler` and grant the Lambda's execution role enough [permissions][1] to access ECS
(and related) services



[1]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_managed_policies.html#AmazonECS_FullAccess