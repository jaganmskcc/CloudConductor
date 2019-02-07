from Modules import Module

class Coverage(Module):
    def __init__(self, module_id, is_docker = False):
        super(Coverage, self).__init__(module_id, is_docker)
        self.output_keys = ["coverage_report"]

    def define_input(self):
        self.add_argument("bam",        is_required=True)
        self.add_argument("bam_idx",    is_required=True)
        self.add_argument("bed",        is_required=True, is_resource=True)
        self.add_argument("bedtools",   is_required=True, is_resource=True)
        self.add_argument("nr_cpus",    is_required=True, default_value=2)
        self.add_argument("mem",        is_required=True, default_value=8)

    def define_output(self):

        # Declare coverage report output filename
        coverage_report = self.generate_unique_file_name(".coverage.txt")
        self.add_output("coverage_report", coverage_report)

    def define_command(self):
        # Define command for running bedtools coverage from a platform
        bam         = self.get_argument("bam")
        bed         = self.get_argument("bed")
        bedtools    = self.get_argument("bedtools")

        # get the output file name to store coverage stats
        coverage_report = self.get_output("coverage_report")

        # Generating coverage command
        cmd = "{0} coverage -a {1} -b {2} > {3} !LOG2!".format(bedtools, bed, bam, coverage_report)

        return cmd