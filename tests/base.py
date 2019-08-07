import os
import json
import base64
import logging
from importlib.machinery import SourceFileLoader
from unittest import TestCase
import googleapiclient
from googleapiclient import discovery
logger = logging.getLogger(__name__)


class CloudConductorTest(TestCase):
    TESTS_DIR = os.path.dirname(__file__)

    def setUp(self):
        cc = SourceFileLoader(
            "CloudConductor",
            os.path.join(os.path.dirname(self.TESTS_DIR), "CloudConductor")
        ).load_module()
        cc.configure_import_paths()
        DEBUG = 3
        cc.configure_logging(DEBUG)


class GooglePlatformTest(CloudConductorTest):
    TEST_PROJECT = "davelab-gcloud"
    TEST_ZONE = "us-east1-c"

    __compute = None

    @property
    def compute_engine(self):
        if self.__compute is None:
            self.__compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
        return self.__compute

    def setUp(self):
        super().setUp()
        key_file = os.path.join(CloudConductorTest.TESTS_DIR, "fixtures", "GoogleKey.json")
        if not os.path.exists(key_file):
            if "GoogleKey" not in os.environ:
                encoded_key_file = os.path.join(CloudConductorTest.TESTS_DIR, "fixtures", "test-key.json")
                if os.path.exists(encoded_key_file):
                    with open(encoded_key_file) as f:
                        b64_key = json.load(f).get("GoogleKey")
                        os.environ["GoogleKey"] = b64_key
            if "GoogleKey" in os.environ:
                with open(key_file, 'w') as f:
                    f.write(base64.b64decode(os.environ["GoogleKey"]).decode().replace("\n", "\\n"))
            os.system("gcloud auth activate-service-account --key-file %s" % key_file)

        if not os.path.exists(key_file):
            raise FileNotFoundError(
                "Google Service Account Credentials not found.\n"
                "Please save the json credentials to 'tests/fixtures/GoogleKey.json'."
                "Or, save the Base64 encoded json file content as environment variable named 'GoogleKey'\n"
            )

    def get_instance_names(self):
        result = self.compute_engine.instances().list(project=self.TEST_PROJECT, zone=self.TEST_ZONE).execute()
        if result.get("items"):
            return [item.get("name") for item in result.get("items")]
        return []

    def delete_instance(self, instance_name):
        instances = self.get_instance_names()
        if instance_name in instances:
            self.compute_engine.instances().delete(
                project=self.TEST_PROJECT,
                zone=self.TEST_ZONE,
                instance=instance_name
            ).execute()

    def assert_instance(self, instance_name):
        result = self.compute_engine.instances().list(project=self.TEST_PROJECT, zone=self.TEST_ZONE).execute()
        if result.get("items"):
            instances = [item.get("name") for item in result.get("items")]
            if instance_name in instances:
                return True
        return False
