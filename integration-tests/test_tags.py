"""
:casecomponent: insights-client
:requirement: RHSS-291297
:polarion-project-id: RHELSS
:polarion-include-skipped: false
:polarion-lookup-method: id
:subsystemteam: sst_csi_client_tools
:caseautomation: Automated
:upstream: Yes
"""

import pytest
import conftest
import contextlib
import os
import yaml
from constants import TAGS_FILE

pytestmark = pytest.mark.usefixtures("register_subman")


@pytest.mark.tier1
def test_tags(insights_client, external_inventory, test_config):
    """
    :id: 3e9d5b76-7065-4ade-8397-5854a8fef83b
    :title: Test tags
    :description:
        Test how the tags generated, and check the tags on inventory
    :tags: Tier 1
    :steps:
        1. Register insights-client, and check satellite related tags
            on the inventory if the test env is satellte.
        2. Run insights-client with the --group
        3. Add a new tag in tags.yaml, and run insights-client,
            then check the inventory
    :expectedresults:
        1. System is registered to insights, and there will be
            satellite related tags supported by branch_info with
            satellite env.
        2. tags.yaml will be created with group option, and new tag
            generated by tags.yaml
        3. The new tag shows on inventory by modifying tags.yaml
    """
    # Remove the tags.yaml if it exists
    with contextlib.suppress(FileNotFoundError):
        TAGS_FILE.unlink()

    # Register insights
    insights_client.register()
    assert conftest.loop_until(lambda: insights_client.is_registered)

    # When test env is satellite, check the tags from branch_info
    # the tags from satellite are not generated by tags.yaml
    if "satellite" in test_config.environment:
        insights_client.run()
        system_tags = external_inventory.this_system_tags()
        for tag in system_tags:
            assert tag["namespace"] == "satellite"
    assert not TAGS_FILE.exists()

    with contextlib.ExitStack() as stack:
        # Run insights-client --group
        insights_client.run("--group=first_tag")
        stack.callback(os.remove, TAGS_FILE)
        assert TAGS_FILE.exists()
        with TAGS_FILE.open("r") as tags_yaml:
            data_loaded = yaml.safe_load(tags_yaml)
            assert data_loaded["group"] == "first_tag"

        # Check new tag from inventory
        system_tags = external_inventory.this_system_tags()
        assert {
            "namespace": "insights-client",
            "key": "group",
            "value": "first_tag",
        } in system_tags

        # Add new tag in tags.yaml file and check on inventory
        with TAGS_FILE.open("r") as tags_yaml:
            data_loaded = yaml.safe_load(tags_yaml)
            data_loaded["add_by_file"] = "second_tag"
        with TAGS_FILE.open("w") as tags_yaml:
            yaml.dump(data_loaded, tags_yaml, default_flow_style=False)
        insights_client.run()
        system_tags = external_inventory.this_system_tags()
        assert {
            "namespace": "insights-client",
            "key": "add_by_file",
            "value": "second_tag",
        } in system_tags
