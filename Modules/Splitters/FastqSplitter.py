import math
import logging

from Modules import Splitter

class FastqSplitter(Splitter):

    def __init__(self, module_id, is_docker=False):
        super(FastqSplitter, self).__init__(module_id, is_docker)
        self.output_keys = ["R1", "R2", "nr_cpus"]

        # BWA-MEM aligning speed constant
        self.ALIGN_SPEED = 10 ** 8  # bps/vCPU for 10 mins of processing

    def define_input(self):
        self.add_argument("R1",             is_required=True)
        self.add_argument("R2",             is_required=False)
        self.add_argument("nr_reads",       is_required=True)
        self.add_argument("max_nr_cpus",    is_required=True)
        self.add_argument("read_len",       is_required=True)
        self.add_argument("nr_cpus",        is_required=True,   default_value=4)
        self.add_argument("mem",            is_required=True,   default_value="nr_cpus * 2")

    def define_output(self):
        # Obtaining the arguments
        R1          = self.get_argument("R1")
        R2          = self.get_argument("R2")
        max_nr_cpus = int(self.get_argument("max_nr_cpus"))
        nr_reads    = int(self.get_argument("nr_reads"))
        read_len    = int(self.get_argument("read_len"))

        # Cut nr_reads by half if paired
        nr_reads = nr_reads/2.0 if R2 is not None else nr_reads

        # Computing the number of lines to be split for each file considering:
        #  - The aligning speed which is in bps/vCPU
        #  - The maximum number of vCPUs alloed on the platform
        #  - The difference between read and read pair (divide by 2)
        nr_reads_per_split  = self.ALIGN_SPEED / read_len / 2 * max_nr_cpus
        nr_splits           = int(math.ceil(nr_reads * 1.0 / nr_reads_per_split))

        # Set number of lines per split to be access in get_command()
        self.nr_lines_per_split = nr_reads_per_split * 4

        logging.debug("Num reads: %s" % nr_reads)
        logging.debug("Num reads per split: %s" % nr_reads_per_split)
        logging.debug("Num splits: %s" % nr_splits)
        logging.debug("Num lines per split: %s" % self.nr_lines_per_split)

        # Simply return if input doesn't need to be split
        if nr_splits < 2:
            split_id = "00"
            self.make_split(split_id)
            self.add_output(split_id, "R1", str(R1))
            r2 = str(R2) if R2 is not None else None
            self.add_output(split_id, "R2", r2)
            self.add_output(split_id, "nr_cpus", max_nr_cpus, is_path=False)
            return

        # Create new dictionary for each split
        for i in range(nr_splits - 1):
            # Generate filenames with split names as they'll appear after being generated with unix split function
            split_id = "%02d" % i
            r1_split = self.generate_unique_file_name(split_id=split_id, extension="R1.fastq")
            r2_split = self.generate_unique_file_name(split_id=split_id, extension="R2.fastq") if R2 is not None else None

            logging.debug("We making a split in the loop!")

            # Create next split
            self.make_split(split_id)
            self.add_output(split_id, "R1", r1_split)
            self.add_output(split_id, "nr_cpus", max_nr_cpus, is_path=False)
            self.add_output(split_id, "R2", r2_split)

        logging.debug("We making one final split!")

        # Create final split using remaining CPUs
        # Determine number of CPUs available for last split
        nr_cpus_needed      = int(math.ceil(nr_reads * read_len * 2 * 1.0 / self.ALIGN_SPEED))
        nr_cpus_remaining   = nr_cpus_needed % max_nr_cpus if nr_cpus_needed % max_nr_cpus else max_nr_cpus
        nr_cpus_remaining   += nr_cpus_remaining % 2
        nr_cpus_remaining   = max(nr_cpus_remaining, 4)

        # Make final split
        split_id = "%02d" % int(nr_splits-1)
        r1_split = self.generate_unique_file_name(split_id=split_id, extension="R1.fastq")
        r2_split = self.generate_unique_file_name(split_id=split_id, extension="R2.fastq") if R2 is not None else None
        self.make_split(split_id)
        self.add_output(split_id, "R1", r1_split)
        self.add_output(split_id, "R2", r2_split)
        self.add_output(split_id, "nr_cpus", nr_cpus_remaining, is_path=False)

    def define_command(self):

        # Obtaining the arguments
        # Obtaining the arguments
        R1          = self.get_argument("R1")
        R2          = self.get_argument("R2")
        nr_cpus     = self.get_argument("nr_cpus")

        # Return if no splitting needs to be done
        if len(self.output.keys()) < 2:
            return None

        # Get output file prefix
        # Get output file basename
        split_name = self.output.keys()[0]
        output_basename = self.output[split_name]["R1"].get_path().split(split_name)[0]

        # Generate command for splitting R1
        split_r1_cmd = self.__get_unix_split_cmd(R1, nr_cpus, output_basename, output_suffix=".R1.fastq")

        if R2 is not None:
            # Generate command for splitting R2
            split_r2_cmd = self.__get_unix_split_cmd(R2, nr_cpus, output_basename, output_suffix=".R2.fastq")
            cmd = "%s !LOG2! && %s !LOG2!" % (split_r1_cmd, split_r2_cmd)
        else:
            cmd = "%s !LOG2!" % split_r1_cmd
        return cmd

    def __get_unix_split_cmd(self, fastq_file, nr_cpus, output_prefix, output_suffix):
        # Return command for using the unix 'split' command to split a fastq file into chunks
        # Automatically detects whether to decompress fastq file

        if fastq_file.endswith(".gz"):
            split_cmd = "pigz -p %d -d -k -c %s | split --suffix-length=2 --numeric-suffixes --additional-suffix=%s --lines=%d - %s" \
                     % (nr_cpus, fastq_file, output_suffix, self.nr_lines_per_split, output_prefix)
        else:
            split_cmd = "split --suffix-length=2 --numeric-suffixes --additional-suffix=%s --lines=%d %s %s" \
                     % (output_suffix, self.nr_lines_per_split, fastq_file, output_prefix)
        return split_cmd
