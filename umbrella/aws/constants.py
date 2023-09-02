from enum import Enum

from pydantic import BaseModel

from umbrella.constants import BaseConfig

DEFAULT_READ_CAPACITY_UNIT = 10
DEFAULT_WRITE_CAPACITY_UNIT = 10

PARTITION_KEY_TYPE = "HASH"
SORT_KEY_TYPE = "RANGE"


class _AWSConfig(BaseConfig):
    """
    Default config values needed for AWS integration.
    """

    aws_access_key_id: str = None  # Loaded from '.env' file
    aws_secret_access_key: str = None  # Loaded from '.env' file
    region: str = "us-east-1"

    dynamodb_name: str = "dynamodb"


AWSConfig = _AWSConfig()

AWS_CREDENTIALS = {
    "aws_access_key_id": AWSConfig.aws_access_key_id,
    "aws_secret_access_key": AWSConfig.aws_secret_access_key,
    "region_name": AWSConfig.region,
}


class DDBTable(Enum):
    """
    DynamoDB table names.
    """

    userdata: str = "UserData"
    serverdata: str = "ServerData"


class DDBNumberValue(BaseModel):
    N: str


class DDBStringValue(BaseModel):
    S: str


class DDBBooleanValue(BaseModel):
    BOOL: bool = False


SERVER_TABLE_DEFINITION = {
    "KeySchema": [
        {"AttributeName": "server_id", "KeyType": PARTITION_KEY_TYPE}  # Partition Key
    ],
    "AttributeDefinitions": [{"AttributeName": "server_id", "AttributeType": "N"}],
    "ProvisionedThroughput": {
        "ReadCapacityUnits": DEFAULT_READ_CAPACITY_UNIT,
        "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY_UNIT,
    },
    "DeletionProtectionEnabled": True,
}


class ServerTableItem(BaseModel):
    """
    DynamoDB `ServerData` table's item constructor.
    """

    server_id: DDBNumberValue
    server_status_channel_id: DDBNumberValue


class ServerTableKey(BaseModel):
    """
    DynamoDB `ServerData` table's partition/sort key constructor.
    """

    server_id: DDBNumberValue


USER_TABLE_DEFINITION = {
    "KeySchema": [
        {"AttributeName": "server_id", "KeyType": PARTITION_KEY_TYPE},  # Partition Key
        {"AttributeName": "user_id", "KeyType": SORT_KEY_TYPE},  # Sort Key
    ],
    "AttributeDefinitions": [
        {"AttributeName": "server_id", "AttributeType": "N"},
        {"AttributeName": "user_id", "AttributeType": "N"},
    ],
    "ProvisionedThroughput": {
        "ReadCapacityUnits": DEFAULT_READ_CAPACITY_UNIT,
        "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY_UNIT,
    },
    "DeletionProtectionEnabled": True,
}


class UserTableItem(BaseModel):
    """
    DynamoDB `UserData` table's item constructor.
    """

    server_id: DDBNumberValue
    user_id: DDBNumberValue
    registered: DDBStringValue
    minecraft_user_id: DDBStringValue


class UserTableKey(BaseModel):
    """
    DynamoDB `UserData` table's partision/sort key constructor.
    """

    server_id: DDBNumberValue
    user_id: DDBNumberValue
