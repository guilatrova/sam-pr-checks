import logging

import boto3

logger = logging.getLogger()

# CodeFreeze
CODE_FREEZE_TABLE = "CodeFreezeConfig"
FREEZE_CONFIG = "FreezeStatus"
DEFAULT_CODEFREEZE_STATUS = {
    "ConfigName": FREEZE_CONFIG,
    "Status": "disabled",
    "Author": "",
}

# Quality
QUALITY_TABLE = "QualityReports"


def _get_table(name):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(name)
    return table


# CodeFreeze
def write_config(key, **kwargs):
    table = _get_table(CODE_FREEZE_TABLE)
    table.put_item(Item={"ConfigName": key, **kwargs})


def get_code_freeze_config():
    table = _get_table(CODE_FREEZE_TABLE)
    response = table.get_item(Key={"ConfigName": FREEZE_CONFIG})

    if "Item" in response:
        return response["Item"]

    return DEFAULT_CODEFREEZE_STATUS


# Quality
def save_reports(cov_report, quality_report, quality_tool, **kwargs):
    table = _get_table(QUALITY_TABLE)

    # Below line is just to be obvious and show the Key, it's not really required
    commit_sha = kwargs.pop("commit_sha")
    kwargs.pop("pr_link", False)
    item = {
        "commit_sha": commit_sha,
        "cov_report": cov_report,
        "quality_report": quality_report,
        "quality_tool": quality_tool,
        **kwargs,
    }

    print(f"Saving data to dynamodb {item}")

    table.put_item(Item=item)


def get_report(commit_sha):
    table = _get_table(QUALITY_TABLE)
    response = table.get_item(Key={"commit_sha": commit_sha})

    if "Item" in response:
        return response["Item"]

    return False
