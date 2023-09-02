from typing import List

import boto3
from botocore.exceptions import ClientError

from umbrella.aws.constants import (
    AWSConfig,
    DDBBooleanValue,
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

    DEFAULT_RETURN_CONSUMED_CAPACITY = "INDEXES"

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
                TableName="tesssdfdftinggg", **table_definition
            )

            waiter = self.dynamodb_client.get_waiter("table_exists")
            waiter.wait(TableName=table.value, WaiterConfig={"Delay": 5})
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
                table_description["CreationDateTime"].strftime(
                    TimeConfig.datetime_format_full
                ),
                table_description["TableStatus"],
            )

            return

    def read_table(
        self,
        table: DDBTable,
        key_condition_exp: str = None,
        filter_exp: str = None,
        projection_exp: str = None,
        exp_attribute_names: dict[str, str] = None,
        exp_attribute_values: dict[str, DDBNumberValue, DDBStringValue] = None,
    ) -> List[dict[str, DDBNumberValue | DDBStringValue | DDBBooleanValue]]:
        """
        `boto3.client.scan` and `boto3.client.query` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to be read.
        key_condition_exp: :class:`str`
            An optional Key Condition Expression which switches the API call to query if exists.
        filter_exp: :class:`str`
            An optional Filter Expression used to filter items.
        projection_exp: :class:`str`
            An optional Projection Expression used to retrieve a subset of data from items.
        exp_attribute_names: :class:`dict`
            An optional expression attribute names to support other expressions supplied in param.
        exp_attribute_values: :class:`dict`
            An optional expression attribute values to support other expressions supplied in param.
        """
        items = []
        total_retrieved = 0
        read_table_params = {
            "TableName": table.value,
            "ReturnConsumedCapacity": self.DEFAULT_RETURN_CONSUMED_CAPACITY,
        }
        if filter_exp:
            read_table_params["FilterExpression"] = filter_exp
        if projection_exp:
            read_table_params["ProjectionExpression"] = projection_exp
        if exp_attribute_names:
            read_table_params["ExpressionAttributeNames"] = exp_attribute_names
        if exp_attribute_values:
            read_table_params["ExpressionAttributeValues"] = exp_attribute_values

        if key_condition_exp:
            read_table_params["KeyConditionExpression"] = key_condition_exp
            _read_table = self.dynamodb_client.query
        else:
            _read_table = self.dynamodb_client.scan

        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    read_table_params["ExclusiveStartKey"] = start_key
                response = _read_table(**read_table_params)

                items.extend(response.get("Items", []))
                total_retrieved += response.get("ScannedCount")
                start_key = response.get("LastEvaluatedKey", None)
                done = start_key is None
        except ClientError as e:
            self.logger.error(
                "Couldn't %s table %s. Here's why: %s: %s",
                _read_table.__name__,
                table.value,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e
        else:
            self.logger.info(
                "A total of %s items were retrieved from table %s using %s operation",
                total_retrieved,
                table.value,
                _read_table.__name__,
            )
            return items

    def delete_item(
        self,
        table: DDBTable,
        pskey: dict[str, DDBNumberValue | DDBStringValue],
    ) -> None:
        """
        `boto3.client.delete_item` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to delete an item from.
        pskey: :class:`dict`
            The Partition Key and Sort Key(if exists) needed to delete an item from the table.
        """
        try:
            response = self.dynamodb_client.delete_item(
                TableName=table.value,
                Key=pskey,
                ReturnValues="ALL_OLD",
            )
        except ClientError as e:
            self.logger.error(
                "Couldn't delete item with key(s) %s from table %s. Here's why: %s: %s",
                pskey,
                table.value,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e
        else:
            self.logger.info(
                "Item '%s' successfully deleted on table %s.",
                response.get("Attributes"),
                table.value,
            )
            return

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
            The enum of the table name to retrieve an item from.
        pskey: :class:`dict`
            The Partition Key and Sort Key(if exists) needed to retrieve an item from the table.
        projection_exp: :class:`str`
            An optional Projection Expression used to retrieve a subset of data from an item.
        exp_attribute_names: :class:`dict`
            An optional expression attribute names to support a projection expression.
        """
        get_item_params = {"TableName": table.value, "Key": pskey}
        if projection_exp:
            get_item_params["ProjectionExpression"] = projection_exp
        if exp_attribute_names:
            get_item_params["ExpressionAttributeNames"] = exp_attribute_names

        try:
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
        """
        `boto3.client.put_item` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to put an item in.
        item_definition: :class:`pydantic.BaseModel`
            The model definition of item attributes for a table.
        """
        try:
            self._validate_table_item_match(table, item_definition)

            item = item_definition.model_dump()
            self.dynamodb_client.put_item(TableName=table.value, Item=item)
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
            return

    def update_item(
        self,
        table: DDBTable,
        pskey: dict[str, DDBNumberValue | DDBStringValue],
        update_exp: str,
        exp_attribute_values: dict[str, DDBNumberValue, DDBStringValue],
    ) -> dict:
        """
        `boto3.client.update_item` wrapper.

        Parameters
        ------------
        table: :class:`enum`
            The enum of the table name to to update an item from.
        pskey: :class:`dict`
            The Partition Key and Sort Key(if exists) needed to update an item from the table.
        update_exp: :class:`str`
            An Update Expression used to update specific values for an item.
        exp_attribute_values: :class:`dict`
            An expression attribute values to support the update expression.
        """
        update_item_params = {
            "TableName": table.value,
            "Key": pskey,
            "UpdateExpression": update_exp,
            "ExpressionAttributeValues": exp_attribute_values,
            "ReturnValues": "ALL_NEW",
        }

        try:
            response = self.dynamodb_client.update_item(**update_item_params)
        except ClientError as e:
            self.logger.error(
                "Couldn't update item with key(s) %s on table %s. Here's why: %s: %s",
                pskey,
                table.value,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e
        else:
            self.logger.info(
                "Item '%s' successfully updated on table %s.",
                response.get("Attributes"),
                table.value,
            )
            return response.get("Attributes")

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
