import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime

from umbrella.aws.constants import (
    AWS_CREDENTIALS,
    AWSConfig,
    DDBNumberValue,
    DDBStringValue,
    DDBTable,
    ServerTableItem,
    UserTableItem,
)
from umbrella.constants import TimeConfig
from umbrella.log import get_logger
from umbrella.utils.exceptions import ValidationError


class DynamoDB:
    """DynamoDB handler for umbrella."""

    USER_TABLE_NAME = DDBTable.userdata.value

    def __init__(self, aws_credentials: dict[str, str]):
        """
        Parameters
        ------------
        aws_credentials: :class:`dict`
            AWS Credentials needed to successfully connect to DynamoDB.
        """
        self.dynamodb_client = boto3.client(AWSConfig.dynamodb_name, **aws_credentials)
        self.logger = get_logger()

    def create_table(self, table: DDBTable, table_definition: dict) -> None:
        """
        `boto3.client.create_table` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to be created.
        table_definition: :class:`str`
            The DynamoDB table definition specific to this table.
        """
        try:
            response = self.dynamodb_client.create_table(
                TableName=table.value, **table_definition
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                # table already exists
                print(e.response)
            else:
                # other errors
                self.logger.error(
                    "Couldn't create table %s. Here's why: %s: %s",
                    table.value,
                    e.response["Error"]["Code"],
                    e.response["Error"]["Message"],
                )
                raise e
        else:
            table_description = response["TableDescription"]
            self.logger.info(
                "Table '%s' successfully created on %s. Current table status is '%s'",
                table_description["TableName"],
                (
                    TimeConfig.datetime_format_full
                    % table_description["CreationDateTime"]
                ),
                table_description["TableStatus"],
            )
            return table_description["TableName"]

    def scan_table(self, table: str, filter_exp):
        Key().between()
        self.dynamodb_client.scan()
        self.dynamodb_client

    def get_item(
        self,
        table: DDBTable,
        pskey: dict[str, DDBNumberValue | DDBStringValue],
        projection_exp: str = None,
        exp_attribute_names: dict[str, str] = None,
    ) -> dict:
        """
        `boto3.client.get_item` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to be created.
        pskey: :class:`dict`
            The Partition Key and Sort Key(if exists) needed to retrieve an item from the table.
        projection_exp: :class:`str`
            An optional Projection Expression used to retrieve a subset of data from an item.
        exp_attribute_names: :class:`dict`
            An optional expression attribute names to support a projection expression.
        """
        try:
            get_item_params = {"TableName": table.value, "Key": pskey}
            if projection_exp:
                get_item_params["ProjectionExpression"] = projection_exp
            if exp_attribute_names:
                get_item_params["ExpressionAttributeNames"] = exp_attribute_names

            response = self.dynamodb_client.get_item(**get_item_params)
        except ClientError as e:
            self.logger.error(
                "Couldn't get item with key(s) %s from table %s. Here's why: %s: %s",
                pskey,
                table.value,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e
        else:
            item = response.get("Item")
            return item if item else {}

    def put_item(
        self,
        table: DDBTable,
        item_definition: UserTableItem | ServerTableItem,
    ) -> None:
        try:
            self._validate_table_item_match(table, item_definition)

            item = item_definition.model_dump()
            response = self.dynamodb_client.put_item(TableName=table.value, Item=item)
        except ValidationError as e:
            raise e
        except ClientError as e:
            self.logger.error(
                "Couldn't put item %s to table %s. Here's why: %s: %s",
                item_definition,
                table.value,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e
        else:
            self.logger.info(
                "Item '%s' successfully created on table %s.",
                item_definition.model_dump(),
                table.value,
            )
            return response

    def update_item(
        self,
        table: DDBTable,
        pskey: dict[str, DDBNumberValue | DDBStringValue],
        update_exp: str,
        exp_attribute_names: dict[str, str] = None,
    ) -> dict:
        pass

    @staticmethod
    def _validate_table_item_match(
        table: DDBTable,
        item_definition: UserTableItem | ServerTableItem,
    ) -> None:
        """
        A static helper method to validate matching table name to item definition.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to be created.
        item_definition: :class:`pydantic.BaseModel`
            The model definition of item attributes for a table.
        """
        validation_error_message = (
            "Table name and item definition mismatch. Please check again."
        )
        if table == DDBTable.userdata and not isinstance(
            item_definition, UserTableItem
        ):
            raise ValidationError(validation_error_message)
        if table == DDBTable.serverdata and not isinstance(
            item_definition, ServerTableItem
        ):
            raise ValidationError(validation_error_message)


if __name__ == "__main__":
    # ResourceInUseException -> table already created
    s = DynamoDB(aws_credentials=AWS_CREDENTIALS)

    r = s.put_item(
        DDBTable.userdata,
        UserTableItem(
            server_id={"N": "123123"},
            user_id={"N": "123123"},
            registered={"S": datetime.now().strftime(TimeConfig.datetime_format_full)},
            minecraft_user_id={"S": "whatsup"},
        ),
    )
    print("Item added to DynamoDB.", r)

    # # Retrieve the item from DynamoDB
    retrieved_item = s.get_item(
        DDBTable.userdata,
        {"server_id": {"N": "123"}, "user_id": {"N": "123"}},
        "server_id, user_id, #xx",
        {"#xx": "registered"},
    )
    if retrieved_item:
        print("Retrieved Item:", retrieved_item)
