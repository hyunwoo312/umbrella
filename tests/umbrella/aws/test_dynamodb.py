import unittest

from umbrella.aws.dynamodb import DynamoDB
from umbrella.aws.constants import AWS_CREDENTIALS, DDBTable


class TestDynamoDB(unittest.TestCase):
    s = DynamoDB(aws_credentials=AWS_CREDENTIALS)

    # r = s.put_item(
    #     DDBTable.userdata,
    #     UserTableItem(
    #         server_id={"N": "123123"},
    #         user_id={"N": "12324123"},
    #         registered={"S": datetime.now().strftime(TimeConfig.datetime_format_full)},
    #         minecraft_user_id={"S": "whatsup"},
    #     ),
    # )
    # print("Item added to DynamoDB.", r)

    # # # Retrieve the item from DynamoDB
    # retrieved_item = s.get_item(
    #     DDBTable.userdata,
    #     {"server_id": {"N": "123"}, "user_id": {"N": "123"}},
    #     "server_id, user_id, #xx",
    #     {"#xx": "registered"},
    # )
    # if retrieved_item:
    #     print("Retrieved Item:", retrieved_item)
    # print(Key("server_id").eq("1").get_expression())
    # st = s.read_table(
    #     DDBTable.userdata,
    #     key_condition_exp="server_id = :val",
    #     exp_attribute_values={":val": {"N": "1"}}
    # )
    # print(st)

    # sss = s.update_item(
    #     DDBTable.userdata,
    #     {"server_id": {"N": "123"}, "user_id": {"N": "123"}},
    #     "set minecraft_user_id = :val",
    #     {":val": {"S": "updated_name"}}
    # )
    # print(sss)
    rrrr = s.delete_item(
        DDBTable.userdata, {"server_id": {"N": "1"}, "user_id": {"N": "34"}}
    )
    pass
