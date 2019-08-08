import os
from unittest.mock import patch
from tests.base import GooglePlatformTest
from System.Platform.Google.Instance import Instance


class TestGoogleInstance(GooglePlatformTest):

    instance_name = "cc-test-instance"

    def test_create_and_destroy_instance(self):
        instance = Instance(
            self.instance_name,
            nr_cpus=1,
            mem=2,
            disk_space=20,
            zone='us-east1-c',
            service_acct="cc-test@davelab-gcloud.iam.gserviceaccount.com",
            disk_image="davelab-image-docker"
        )
        instance.create()
        self.assert_instance(self.instance_name)
        instance.destroy(wait=True)

    def tearDown(self):
        self.delete_instance(self.instance_name)
