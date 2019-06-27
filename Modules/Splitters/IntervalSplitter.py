from Modules import Splitter


class IntervalSplitter(Splitter):

    def __init__(self, module_id, is_docker=False):
        super(IntervalSplitter, self).__init__(module_id, is_docker)
        self.output_keys = ["interval_list"]

    def define_input(self):
        # Set GATK executable arguments
        self.add_argument("java",           is_required=True, is_resource=True)
        self.add_argument("gatk",           is_required=True, is_resource=True)
        self.add_argument("gatk_version",   is_required=True)

        # Set reference specific arguments
        self.add_argument("ref",            is_required=True, is_resource=True)
        self.add_argument("ref_idx",        is_required=True, is_resource=True)
        self.add_argument("ref_dict",       is_required=True, is_resource=True)

        # Set tool specific arguments
        self.add_argument("interval_list",      is_required=True)
        self.add_argument("nr_splits",          is_required=True,   default_value=50)
        self.add_argument("nr_cpus",            is_required=True,   default_value=2)
        self.add_argument("mem",                is_required=True,   default_value=2)

    def define_output(self):
        # Obtain number of splits
        nr_splits       = int(self.get_argument("nr_splits"))

        # Add split for each split_interval
        for split_id in range(nr_splits):
            self.make_split(split_id=split_id)
            self.add_output(split_id=split_id, key="interval_list",
                            value="{0}/{1}-scattered.intervals".format(self.output_dir, str(split_id).zfill(4)))

    def define_command(self):
        # Obtain necessary arguments
        interval_list = self.get_argument("interval_list")
        nr_splits = int(self.get_argument("nr_splits"))
        gatk = self.get_argument("gatk")
        mem = self.get_argument("mem")
        java = self.get_argument("java")
        ref = self.get_argument("ref")

        # Set up java options and command
        jvm_options = "-Xmx{0}G -Djava.io.tmpdir={1}".format(mem * 4 // 5, "/tmp/")
        gatk_cmd = "{0} {1} -jar {2}".format(java, jvm_options, gatk)

        # Generate command and return it
        return "{0} SplitIntervals -R {1} -L {2} --scatter-count {3} -O {4} !LOG3!".format(
            gatk_cmd, ref, interval_list, nr_splits, self.output_dir)
