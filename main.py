import boto3
client = boto3.client('ecs')


def lambda_handler(event, context):
    print('Starting process... ')

    if not check_event_params(event):
        print('Error: Function was invoked with wrong payload')
        return False
    print('... Payload check completed')

    try:
        # First check if provided cluster name already exists
        if not check_if_cluster_exists(event['cluster']):
            # Cluster does not exist, create the it
            client.create_cluster(clusterName=event['cluster'])
            print('... Cluster created')

        # Create a new task definition for each function invocation as it creates
        # a newer version if service and container combination already exists
        task_definition = create_new_task_definition(event)
        print('... Task definition registered')

        # Check if service already exists, as service creation is idempotent and can't be invoked twice
        if check_if_service_exists(event):
            # Service already exists, update it with the newest task definition
            update_existing_service(event, task_definition)
            print('... Service updated')
        else:
            # Create a new service and apply task definition
            create_new_service(event, task_definition)
            print('... Service created')
        print('... DONE!')
        return True

    except Exception as e:
        print('Error: ', str(e))
        return False


def check_event_params(event):
    if 'cluster' not in event or len(event['cluster']) < 1:
        return False
    if 'service' not in event or len(event['service']) < 1:
        return False
    if 'container' not in event or len(event['container']) < 1:
        return False
    if 'image' not in event or len(event['image']) < 1:
        return False

    return True


def check_if_cluster_exists(cluster_name):
    response = client.describe_clusters(clusters=[cluster_name])
    if len(response['failures']) and not len(response['clusters']):
        # Cluster not found
        print('... Cluster not found')
        return False
    print('... Cluster found')
    return True


def check_if_service_exists(event):
    response = client.describe_services(
        cluster=event['cluster'],
        services=[
            event['service']
        ]
    )
    if len(response['failures']) and not len(response['services']):
        # Cluster not found
        print('... Service not found')
        return False
    print('... Service found')
    return True


def create_new_task_definition(event):
    container_definition = [{
        'name': event['container'],
        'image': event['image'],
        'memory': 512  # No spec, so it's hardcoded, but could come from a global/default dict or event payload
    }]
    family_name_prefix = event.get('service_family_prefix', '')  # Just an example of how to customize this lambda
    family_name = family_name_prefix + '_' + event['service'] + '_' + event['container']
    response = client.register_task_definition(
        family=family_name,
        containerDefinitions=container_definition
    )
    return response['taskDefinition']


def create_new_service(event, task_definition):
    client.create_service(
        cluster=event['cluster'],
        serviceName=event['service'],
        taskDefinition=task_definition['taskDefinitionArn'],
        desiredCount=1
    )


def update_existing_service(event, task_definition):
    client.update_service(
        cluster=event['cluster'],
        service=event['service'],
        taskDefinition=task_definition['taskDefinitionArn'],
        desiredCount=1,
        forceNewDeployment=True  # Just in case the Docker image was the same (habitual when using the :latest tag)
    )
