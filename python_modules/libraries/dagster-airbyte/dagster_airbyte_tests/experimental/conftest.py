from typing import Iterator

import pytest
import responses
from dagster_airbyte.resources import (
    AIRBYTE_CONFIGURATION_API_BASE,
    AIRBYTE_CONFIGURATION_API_VERSION,
    AIRBYTE_REST_API_BASE,
    AIRBYTE_REST_API_VERSION,
)
from dagster_airbyte.translator import AirbyteConnectionTableProps

TEST_WORKSPACE_ID = "some_workspace_id"
TEST_CLIENT_ID = "some_client_id"
TEST_CLIENT_SECRET = "some_client_secret"

TEST_ACCESS_TOKEN = "some_access_token"

# Taken from the examples in the Airbyte REST API documentation
TEST_DESTINATION_ID = "18dccc91-0ab1-4f72-9ed7-0b8fc27c5826"
TEST_DESTINATION_TYPE = "postgres"
TEST_DESTINATION_DATABASE = "test_database"
TEST_DESTINATION_SCHEMA = "test_schema"
TEST_CONNECTION_ID = "9924bcd0-99be-453d-ba47-c2c9766f7da5"
TEST_CONNECTION_NAME = "Postgres To Snowflake"
TEST_STREAM_PREFIX = "test_prefix_"
TEST_STREAM_NAME = "test_stream"
TEST_SELECTED = True
TEST_JSON_SCHEMA = {}

TEST_AIRBYTE_CONNECTION_TABLE_PROPS = AirbyteConnectionTableProps(
    table_name=f"{TEST_STREAM_PREFIX}{TEST_STREAM_NAME}",
    stream_prefix=TEST_STREAM_PREFIX,
    stream_name=TEST_STREAM_NAME,
    json_schema=TEST_JSON_SCHEMA,
    connection_id=TEST_CONNECTION_ID,
    connection_name=TEST_CONNECTION_NAME,
    destination_type=TEST_DESTINATION_TYPE,
    database=TEST_DESTINATION_DATABASE,
    schema=TEST_DESTINATION_SCHEMA,
)


# Taken from Airbyte REST API documentation
# https://reference.airbyte.com/reference/createaccesstoken
SAMPLE_ACCESS_TOKEN = {"access_token": TEST_ACCESS_TOKEN}


# Taken from Airbyte REST API documentation
# https://reference.airbyte.com/reference/listconnections
SAMPLE_CONNECTIONS = {
    "next": "https://api.airbyte.com/v1/connections?limit=5&offset=10",
    "previous": "https://api.airbyte.com/v1/connections?limit=5&offset=0",
    "data": [
        {
            "connectionId": TEST_CONNECTION_ID,
            "workspaceId": "744cc0ed-7f05-4949-9e60-2a814f90c035",
            "name": TEST_CONNECTION_NAME,
            "sourceId": "0c31738c-0b2d-4887-b506-e2cd1c39cc35",
            "destinationId": TEST_DESTINATION_ID,
            "status": "active",
            "schedule": {
                "schedule_type": "cron",
            },
        }
    ],
}


# Taken from Airbyte Configuration API documentation
# https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html#post-/v1/connections/get
# https://github.com/airbytehq/airbyte-platform/blob/v1.0.0/airbyte-api/server-api/src/main/openapi/config.yaml
SAMPLE_CONNECTION_DETAILS = {
    "connectionId": TEST_CONNECTION_ID,
    "name": TEST_CONNECTION_NAME,
    "namespaceDefinition": "source",
    "namespaceFormat": "${SOURCE_NAMESPACE}",
    "prefix": TEST_STREAM_PREFIX,
    "sourceId": "0c31738c-0b2d-4887-b506-e2cd1c39cc35",
    "destinationId": TEST_DESTINATION_ID,
    "operationIds": ["1938d12e-b540-4000-8c46-1be33f00ab01"],
    "syncCatalog": {
        "streams": [
            {
                "stream": {
                    "name": TEST_STREAM_NAME,
                    "jsonSchema": TEST_JSON_SCHEMA,
                    "supportedSyncModes": ["full_refresh"],
                    "sourceDefinedCursor": False,
                    "defaultCursorField": ["string"],
                    "sourceDefinedPrimaryKey": [["string"]],
                    "namespace": "string",
                    "isResumable": False,
                },
                "config": {
                    "syncMode": "full_refresh",
                    "cursorField": ["string"],
                    "destinationSyncMode": "append",
                    "primaryKey": [["string"]],
                    "aliasName": "string",
                    "selected": TEST_SELECTED,
                    "suggested": False,
                    "fieldSelectionEnabled": False,
                    "selectedFields": [{"fieldPath": ["string"]}],
                    "hashedFields": [{"fieldPath": ["string"]}],
                    "mappers": [
                        {
                            "id": "1938d12e-b540-4000-8ff0-46231e18f301",
                            "type": "hashing",
                            "mapperConfiguration": {},
                        }
                    ],
                    "minimumGenerationId": 0,
                    "generationId": 0,
                    "syncId": 0,
                },
            }
        ]
    },
    "schedule": {"units": 0, "timeUnit": "minutes"},
    "scheduleType": "manual",
    "scheduleData": {
        "basicSchedule": {"timeUnit": "minutes", "units": 0},
        "cron": {"cronExpression": "string", "cronTimeZone": "string"},
    },
    "status": "active",
    "resourceRequirements": {
        "cpu_request": "string",
        "cpu_limit": "string",
        "memory_request": "string",
        "memory_limit": "string",
        "ephemeral_storage_request": "string",
        "ephemeral_storage_limit": "string",
    },
    "sourceCatalogId": "1938d12e-b540-4000-85a4-7ecc2445a901",
    "geography": "auto",
    "breakingChange": False,
    "notifySchemaChanges": False,
    "notifySchemaChangesByEmail": False,
    "nonBreakingChangesPreference": "ignore",
    "created_at": 0,
    "backfillPreference": "enabled",
    "workspaceId": "744cc0ed-7f05-4949-9e60-2a814f90c035",
}


# Taken from Airbyte API documentation
# https://reference.airbyte.com/reference/getdestination
SAMPLE_DESTINATION_DETAILS = {
    "destinationId": TEST_DESTINATION_ID,
    "name": "My Destination",
    "destinationType": TEST_DESTINATION_TYPE,
    "workspaceId": "744cc0ed-7f05-4949-9e60-2a814f90c035",
    "configuration": {
        "conversion_window_days": 14,
        "customer_id": "1234567890",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "database": TEST_DESTINATION_DATABASE,
        "schema": TEST_DESTINATION_SCHEMA,
    },
}


@pytest.fixture(
    name="base_api_mocks",
)
def base_api_mocks_fixture() -> Iterator[responses.RequestsMock]:
    with responses.RequestsMock() as response:
        response.add(
            method=responses.POST,
            url=f"{AIRBYTE_REST_API_BASE}/{AIRBYTE_REST_API_VERSION}/applications/token",
            json=SAMPLE_ACCESS_TOKEN,
            status=201,
        )
        yield response


@pytest.fixture(
    name="fetch_workspace_data_api_mocks",
)
def fetch_workspace_data_api_mocks_fixture(
    base_api_mocks: responses.RequestsMock,
) -> Iterator[responses.RequestsMock]:
    base_api_mocks.add(
        method=responses.GET,
        url=f"{AIRBYTE_REST_API_BASE}/{AIRBYTE_REST_API_VERSION}/connections",
        json=SAMPLE_CONNECTIONS,
        status=200,
    )
    base_api_mocks.add(
        method=responses.POST,
        url=f"{AIRBYTE_CONFIGURATION_API_BASE}/{AIRBYTE_CONFIGURATION_API_VERSION}/connections/get",
        json=SAMPLE_CONNECTION_DETAILS,
        status=200,
    )
    base_api_mocks.add(
        method=responses.GET,
        url=f"{AIRBYTE_REST_API_BASE}/{AIRBYTE_REST_API_VERSION}/destinations/{TEST_DESTINATION_ID}",
        json=SAMPLE_DESTINATION_DETAILS,
        status=200,
    )
    yield base_api_mocks
