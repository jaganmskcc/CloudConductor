import json
import math

from System.Platform import CloudInstance

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class GoogleInstance(CloudInstance):

    def __init__(self, name, nr_cpus, mem, disk_space, **kwargs):

        super(GoogleInstance, self).__init__(name, nr_cpus, mem, disk_space, **kwargs)

        # Initialize the instance credentials
        self.service_account = None
        self.project_id = None
        self.__parse_service_account_json()

        # Create libcloud driver
        driver_class = get_driver(Provider.GCE)
        self.driver = driver_class(self.service_account, self.identity,
                                   datacenter=self.zone,
                                   project=self.project_id)

        # Initialize the extra information
        self.image = kwargs.get("disk_image")

        # Initialize the node variable
        self.node = None

        #super(GoogleInstance, self).__init__(name, nr_cpus, mem, disk_space, **kwargs)

        self.validate()

        self.create_instance()

    def __parse_service_account_json(self):

        # Parse service account file
        with open(self.identity) as json_inp:
            service_account_data = json.load(json_inp)

        # Save data locally
        self.service_account = service_account_data["client_email"]
        self.project_id = service_account_data["project_id"]

    def validate(self):

        # Ensure the memory is withing GCP range:
        if self.mem/self.nr_cpus < 0.9:
            self.mem = self.nr_cpus * 0.9
        elif self.mem/self.nr_cpus > 6.5:
            self.nr_cpus = math.ceil(self.mem / 6.5)

        # Ensure number of CPUs is an even number or 1
        if self.nr_cpus != 1 and self.nr_cpus % 2 == 1:
            self.nr_cpus += 1

    def create(self):

        # Generate NodeSize for instance
        size_name = f"custom-{self.nr_cpus}-{self.mem*1024}"
        node_size = self.driver.ex_get_size(size_name)

        # Read the public key content
        with open(f"{self.ssh_private_key}.pub") as inp:
            ssh_key_content = inp.read()

        # Create instance
        self.node = self.driver.create_node(name=self.name,
                                            image=self.image,
                                            size=node_size,
                                            ex_metadata={
                                                "ssh-keys": f"{self.ssh_connection_user}:"
                                                            f"{ssh_key_content} {self.ssh_connection_user}"
                                            })

        # Return the external IP from node
        return self.node.public_ips[0]

    def destroy(self):
        self.driver.destroy_node(self.node)

    def start(self):
        self.driver.ex_start_node(self.node)

    def stop(self):
        self.driver.ex_stop_node(self.node)

    def get_status(self):
        self.node = self.driver.ex_get_node(self.name)

        # Define mapping between the cloud status and the current class status
        status_map = {
            "PROVISIONING": CloudInstance.CREATING,
            "STAGING":      CloudInstance.CREATING,
            "RUNNING":      CloudInstance.AVAILABLE,
            "STOPPING":     CloudInstance.DESTROYING,
            "SUSPENDED":    CloudInstance.OFF,
            "TERMINATED":   CloudInstance.OFF,
            "UNKNOWN":      CloudInstance.OFF
        }

        return status_map[self.node.extra["status"]]

    def get_compute_price(self):
        return 0

    def get_storage_price(self):
        return 0