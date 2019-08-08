import os
from unittest.mock import patch
from tests.base import GooglePlatformTest
from System import GAPipeline


class TestSystemPipeline(GooglePlatformTest):

    pipeline_dir = os.path.join(GooglePlatformTest.TESTS_DIR, "fixtures", "pipeline")
    graph_config = os.path.join(pipeline_dir, "graph.config")
    resource_config = os.path.join(pipeline_dir, "resource.config")
    platform_config = os.path.join(pipeline_dir, "platform.config")
    sample_config = os.path.join(pipeline_dir, "sample.json")
    pipeline_name = "test-pipeline"

    def test_load_and_validate_pipeline(self):
        g = GAPipeline(
            self.pipeline_name,
            graph_config=self.graph_config,
            resource_kit_config=self.resource_config,
            sample_data_config=self.sample_config,
            platform_config=self.platform_config,
            platform_module="GooglePlatform",
            final_output_dir="gs://davelab_public/cloudconductor_test/"
        )
        g.load()
        g.validate()

    def tearDown(self):
        self.delete_instance("helper-%s" % self.pipeline_name)
