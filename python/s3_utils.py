import boto3

def get_role_unsafe():
    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    return identity["Arn"]

def get_role():
    try:
        return get_role_unsafe()
    except:
        return "Not found"

# connect to S3
def s3_client():
    role = get_role()
    # print(role)

    return boto3.client('s3')