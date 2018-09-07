import logging
import os

from Modules import Module

class DemuxTNA (Module):
    def __init__(self, module_id, is_docker = False):
        super(DemuxTNA, self).__init__(module_id, is_docker)
        self.output_keys    = ["R1", "R2", "demux_stats", "f1_log", "f2_log"]

    def define_input(self):
        self.add_argument("sample_name",    is_required=True)
        self.add_argument("R1",             is_required=True)
        self.add_argument("R2",             is_required=True)
        self.add_argument("assay_to_keep",  is_required=True)
        self.add_argument("barcode",        is_required=True, default_value="TCGACA")
        self.add_argument("nr_cpus",        is_required=True, default_value=2)
        self.add_argument("mem",            is_required=True, default_value=8)

        # Optional cutadapt arguments
        self.add_argument("max_error_rate", is_required=True, default_value=0.2)

        self.add_argument("cutadapt",           is_resource=True, is_required=True)
        self.add_argument("tna_demux_script",   is_resource=True, is_required=True)


    def define_output(self):

        sample_name = self.get_argument("sample_name")

        if self.get_argument("assay_to_keep") == "RNA":
            r1 = os.path.join(self.get_output_dir(), "{0}.RNA.R1.fastq.gz".format(sample_name))
            r2 = os.path.join(self.get_output_dir(), "{0}.RNA.R2.fastq.gz".format(sample_name))
        else:
            r1 = os.path.join(self.get_output_dir(), "{0}.non-RNA.R1.fastq.gz".format(sample_name))
            r2 = os.path.join(self.get_output_dir(), "{0}.non-RNA.R2.fastq.gz".format(sample_name))

        demux_stats = os.path.join(self.get_output_dir(), "adapter_stats.csv")
        log_1 = os.path.join(self.get_output_dir(), "{0}-f1-log.log".format(sample_name))
        log_2 = os.path.join(self.get_output_dir(), "{0}-f2-log.log".format(sample_name))

        self.add_output("R1", r1)
        self.add_output("R2", r2)
        self.add_output("demux_stats", demux_stats)
        self.add_output("f1_log", log_1)
        self.add_output("f2_log", log_2)

    def define_command(self):

        # Get program options
        sample_name     = self.get_argument("sample_name")
        R1              = self.get_argument("R1")
        R2              = self.get_argument("R2")
        barcode         = self.get_argument("barcode")
        max_error_rate  = self.get_argument("max_error_rate")
        demux_script    = self.get_argument("tna_demux_script")

        cmd = "{0} {1} {2} {3} {4} {5} {6} !LOG2!".format(demux_script, R1, R2, max_error_rate, barcode, sample_name,
                                                   self.get_output_dir())

        return cmd

        # f1_r1 = "{0}-f1.R1.fastq.gz".format(sample_name)
        # f1_r2 = "{0}-f1.R2.fastq.gz".format(sample_name)
        # f1_unknown = "{0}-f1.R2.fastq.gz"
        # f2_r1 = "{0}-f2.R1.fastq.gz".format(sample_name)
        # f2_r2 = "{0}-f2.R2.fastq.gz".format(sample_name)
        #
        # cmd1 = "cutadapt -e {0} -g first=^{1} --no-trim -o {2} -p {3} {4} {5} 1> {5}".format(max_error_rate, barcode,
        #                                                                                     f1_r1, f1_r2, R1, R2,
        #                                                                                     log_file)
        #
        # cmd2 = "cutadapt -e {0} -g first=^{1} --no-trim -o {2} -p {3} {4} {5} 1> {5}".format(max_error_rate, barcode,
        #                                                                                     f2_r1, f2_r2, R1, R2,
        #                                                                                     log_file)
        #
        # cmd = '; '.join(cmd1, cmd2)