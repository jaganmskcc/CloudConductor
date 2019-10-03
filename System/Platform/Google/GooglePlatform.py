
from System.Platform import CloudPlatform
from System.Platform.Google import GoogleInstance


class GooglePlatform(CloudPlatform):

    def authenticate_platform(self):
        pass

    @staticmethod
    def standardize_instance_name(inst_name):
        return inst_name.replace("_", "-").lower()

    def publish_report(self, report):
        pass

    def validate(self):
        pass

    def clean_up(self):
        pass

    def get_random_zone(self):
        return "us-east1-c"

    def get_cloud_instance_class(self):
        return GoogleInstance
