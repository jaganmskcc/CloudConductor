from Modules import Module

class CoverageStats(Module):
    def __init__(self, module_id, is_docker = False):
        super(CoverageStats, self).__init__(module_id, is_docker)
        self.output_keys = ["coverage_stats", "coverage_plot"]

    def define_input(self):
        self.add_argument("sample_name",                is_required=True)
        self.add_argument("coverage_report",            is_required=True)
        self.add_argument("coverage_stats_script",      is_required=True, is_resource=True)
        self.add_argument("nr_cpus",                    is_required=True, default_value=2)
        self.add_argument("mem",                        is_required=True, default_value="nr_cpus * 2")

    def define_output(self):

        # Declare unique file name for output stat file and output plot file
        coverage_file = self.generate_unique_file_name(extension=".coverage.stats.txt")
        coverage_plot = self.generate_unique_file_name(extension=".coverage.stats.pdf")

        # add output keys
        self.add_output("coverage_stats", coverage_file)
        self.add_output("coverage_plot", coverage_plot)

    def define_command(self):

        # Get arguments
        sample          = self.get_argument("sample_name")
        coverage_report = self.get_argument("coverage_report")

        #get the coverage script or docker image name
        coverage_stats_script = self.get_argument("coverage_stats_script")

        #get the output file and make appropriate path for it
        output_file     = self.get_output("coverage_stats")

        if not self.is_docker:
            cmd = "sudo Rscript --vanilla {0} -s {1} -f {2} -o {3} !LOG3!".format(coverage_stats_script, sample,
                                                                                  coverage_report, output_file)
        else:
            cmd = "Rscript --vanilla {0} -s {1} -f {2} -o {3} !LOG3!".format(coverage_stats_script, sample,
                                                                             coverage_report, output_file)

        return cmd