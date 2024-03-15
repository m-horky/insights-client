import time
import os.path

import pytest

pytestmark = pytest.mark.usefixtures("register_subman")


class InsightsInventory:
    def __init__(self):
        pass

    def get_systems(self, machine_id: str) -> dict:
        # curl --cert /etc/pki/consumer/cert.pem --key /etc/pki/consumer/key.pem -X GET https://cert.cloud.stage.redhat.com/api/inventory/v1/hosts?insights_id={machine_id}
        pass

    def delete_system(self, machine_id: str):
        systems = self.get_systems(machine_id)
        system_id = systems["results"][0]["id"]
        # curl --cert /etc/pki/consumer/cert.pem --key /etc/pki/consumer/key.pem -X DELETE https://cert.cloud.stage.redhat.com/api/inventory/v1/hosts/{system_id}
        pass


def test_inventory_deletion(insights_client):
    """Test unregistration via Inventory.

    It is possible to delete an existing system in Inventory by clicking the
    [Delete] button in GUI, or by calling an API endpoint.
    """
    insights_client.register()
    assert insights_client.is_registered
    assert os.path.exists("/etc/insights-client/.registered")

    # TODO Call Insights API and delete the system there
    time.sleep(30)

    res = insights_client.run()
    assert not insights_client.is_registered
    assert "Insights API says this machine is NOT registered." in res.stdout
    assert "System unregistered locally via .unregistered file" in res.stdout
    assert os.path.exists("/etc/insights-client/.unregistered")
