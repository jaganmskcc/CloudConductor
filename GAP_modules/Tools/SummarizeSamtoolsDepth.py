from GAP_interfaces import Tool

__main_class__ = "SummarizeSamtoolsDepth"

class SummarizeSamtoolsDepth(Tool):

    def __init__(self, config, sample_data, tool_id):
        super(SummarizeSamtoolsDepth, self).__init__(config, sample_data, tool_id)

        self.can_split      = False

        self.nr_cpus        = 1
        self.mem            = self.config["platform"]["MS_mem"]

        self.input_keys     = ["samtools_depth"]
        self.output_keys    = ["summary_file"]

        self.req_tools      = ["qc_parser"]
        self.req_resources  = []

    def get_command(self, **kwargs):

        # Get options from kwargs
        input           = kwargs.get("samtools_depth",  None)
        cutoffs         = kwargs.get("cutoffs",         [1,5,10,15,25,50,100])

        # Generating command to parse samtools depth output
        cmd = "%s coverage -i %s" % (self.tools["qc_parser"], input)

        # Add options for coverage depth cutoffs to report
        for cutoff in cutoffs:
            cutoff = int(cutoff)
            cmd += " --ct %d" % cutoff

        # Write output to summary file
        cmd += " > %s !LOG2!" % self.output["summary_file"]

        return cmd

    def init_output_file_paths(self, **kwargs):
        self.generate_output_file_path("summary_file", "depth.summary.txt")