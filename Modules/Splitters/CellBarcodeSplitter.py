from Modules import Splitter


class CellBarcodeSplitter(Splitter):

    def __init__(self, module_id, is_docker=False):
        super(CellBarcodeSplitter, self).__init__(module_id, is_docker)
        self.output_keys = ["barcode"]

    def define_input(self):
        self.add_argument("barcode_list", is_required=True)

        # Set tool specific arguments
        self.add_argument("nr_cpus",       is_required=True,   default_value=2)
        self.add_argument("mem",           is_required=True,   default_value=2)

    def define_output(self):
        # Add a split for each barcode
        barcode_list = self.get_argument("barcode_list")

        for barcode in barcode_list:
            self.make_split(split_id=barcode)
            self.add_output(split_id=barcode, key="barcode", value=barcode, is_path=False)

    def define_command(self):
        # The point of this module is to split the Cloud Conductor graph, not to perform a command, so we do nothing
        return None
