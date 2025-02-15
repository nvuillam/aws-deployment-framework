# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Creates or updates an ALIAS for an account
"""

import os
from sts import STS
from aws_xray_sdk.core import patch_all
from logger import configure_logger

patch_all()

LOGGER = configure_logger(__name__)
ADF_ROLE_NAME = os.getenv("ADF_ROLE_NAME")


def create_account_alias(account, iam_client):
    LOGGER.info(
        "Ensuring Account: %s has alias %s",
        account.get('account_full_name'),
        account.get('alias'),
    )
    try:
        iam_client.create_account_alias(AccountAlias=account.get("alias"))
    except iam_client.exceptions.EntityAlreadyExistsException as error:
        LOGGER.error(
            f"The account alias {account.get('alias')} already exists."
            "The account alias must be unique across all Amazon Web Services products."
            "Refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html#AboutAccountAlias"
        )
        raise error
    return account


def lambda_handler(event, _):
    if event.get("alias"):
        sts = STS()
        account_id = event.get("account_id")
        role = sts.assume_cross_account_role(
            f"arn:aws:iam::{account_id}:role/{ADF_ROLE_NAME}",
            "adf_account_alias_config",
        )
        create_account_alias(event, role.client("iam"))
    else:
        LOGGER.info(
            "Account: %s does not need an alias",
            event.get('account_full_name'),
        )
    return event
