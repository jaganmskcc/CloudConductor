import logging

from Modules import Module
from System.Platform import Platform

class _GATKBase(Module):

    def __init__(self, module_id, is_docker=False):
        super(_GATKBase, self).__init__(module_id, is_docker)

    def define_base_args(self):

        # Set GATK executable arguments
        self.add_argument("java",           is_required=True, is_resource=True)
        self.add_argument("gatk",           is_required=True, is_resource=True)
        self.add_argument("gatk_version",   is_required=True)

        # Set reference specific arguments
        self.add_argument("ref",            is_required=True, is_resource=True)
        self.add_argument("ref_idx",        is_required=True, is_resource=True)
        self.add_argument("ref_dict",       is_required=True, is_resource=True)

        # Set chromosome interval specific arguments
        self.add_argument("location")
        self.add_argument("excluded_location")
        self.add_argument("interval_list")
        self.add_argument("bed", is_resource=True)

    def get_gatk_command(self):
        # Get input arguments
        gatk    = self.get_argument("gatk")
        mem     = self.get_argument("mem")
        java = self.get_argument("java")
        jvm_options = "-Xmx{0}G -Djava.io.tmpdir={1}".format(mem * 4 / 5, "/tmp/")

        # Determine numeric version of GATK
        gatk_version = self.get_argument("gatk_version")
        gatk_version = str(gatk_version).lower().replace("gatk","")
        gatk_version = gatk_version.strip()
        gatk_version = int(gatk_version.split(".")[0])

        if gatk_version < 4:
            return "{0} {1} -jar {2} -T".format(java, jvm_options, gatk)

        # Generate base command with endpoint provided by docker
        else:
            return "{0} {1} -jar {2}".format(java, jvm_options, gatk)

    def get_output_file_flag(self):
        """
        Function returns an appropriate output file flag for GATK tools based on GATK version
        Returns: Output file flag in Str format

        """

        # Determine numeric version of GATK
        gatk_version = self.get_argument("gatk_version")
        gatk_version = str(gatk_version).lower().replace("gatk", "")
        gatk_version = gatk_version.strip()
        gatk_version = int(gatk_version.split(".")[0])

        if gatk_version < 4:
            return "-o"

        return "-O"

class HaplotypeCaller(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(HaplotypeCaller, self).__init__(module_id, is_docker)
        self.output_keys = ["gvcf", "gvcf_idx", "vcf", "vcf_idx"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                    is_required=True)
        self.add_argument("bam_idx",                is_required=True)
        self.add_argument("BQSR_report",            is_required=False)
        self.add_argument("use_bqsr",               is_required=True, default_value=True)
        self.add_argument("output_type",            is_required=True, default_value="gvcf")
        self.add_argument("nr_cpus",                is_required=True, default_value=8)
        self.add_argument("mem",                    is_required=True, default_value=48)
        self.add_argument("use_soft_clipped_bases", is_required=True, default_value=True)

    def define_output(self):
        # Declare GVCF output filename
        randomer = Platform.generate_unique_id()
        # generate uniques file name based on the output mode set for the Haplotypecaller
        if self.get_argument("output_type") == "gvcf":
            gvcf = self.generate_unique_file_name(extension="{0}.g.vcf".format(randomer))
            self.add_output("gvcf", gvcf)
            # Declare GVCF index output filename
            gvcf_idx = self.generate_unique_file_name(extension="{0}.g.vcf.idx".format(randomer))
            self.add_output("gvcf_idx", gvcf_idx)
        else:
            vcf = self.generate_unique_file_name(extension="{0}.vcf".format(randomer))
            self.add_output("vcf", vcf)
            # Declare VCF index output filename
            vcf_idx = self.generate_unique_file_name(extension="{0}.vcf.idx".format(randomer))
            self.add_output("vcf_idx", vcf_idx)

    def define_command(self):
        # Get input arguments
        bam                    = self.get_argument("bam")
        BQSR                   = self.get_argument("BQSR_report")
        output_type            = self.get_argument("output_type")
        ref                    = self.get_argument("ref")
        L                      = self.get_argument("location")
        XL                     = self.get_argument("excluded_location")
        interval               = self.get_argument("interval_list")
        bed                    = self.get_argument("bed")

        gatk_cmd               = self.get_gatk_command()
        gatk_version           = self.get_argument("gatk_version")
        use_bqsr               = self.get_argument("use_bqsr")
        use_soft_clipped_bases = self.get_argument("use_soft_clipped_bases")
        nr_cpus                = self.get_argument("nr_cpus")

        output_file_flag = self.get_output_file_flag()

        # Generating the haplotype caller options
        opts = list()
        opts.append("-I {0}".format(bam))
        opts.append("-R {0}".format(ref))

        # Setting the output file based on the output mode
        if output_type == "gvcf":
            opts.append("{0} {1}".format(output_file_flag, self.get_output("gvcf")))
        else:
            opts.append("{0} {1}".format(output_file_flag, self.get_output("vcf")))

        # Setting the output mode
        if output_type == "gvcf":
            opts.append("-ERC GVCF")

        # Adding the BQSR for lower version of the GATK
        if BQSR is not None and gatk_version < 4 and use_bqsr:
            opts.append("-BQSR {0}".format(BQSR))

        # Set the parallelism method
        if gatk_version < 4:
            opts.append("-nct {0}".format(nr_cpus))
        else:
            opts.append("--native-pair-hmm-threads {0}".format(nr_cpus))

        # Limit the locations to be processed
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    if included != "unmapped":
                        opts.append("-L \"{0}\"".format(included))
            else:
                opts.append("-L \"{0}\"".format(L))
        if XL is not None:
            if isinstance(XL, list):
                for excluded in XL:
                    opts.append("-XL \"{0}\"".format(excluded))
            else:
                opts.append("-XL \"{0}\"".format(XL))

        # Check if an interval list was provided and if yes, place it
        if interval is not None:
            opts.append("-L {0}".format(interval))

        # Check if a BED file was provided and if yes, place it
        if bed is not None:
            opts.append("-L {0}".format(bed))

        # Add on flag for not using soft clipped bases if defined (used in RNAseq variant calling)
        if use_soft_clipped_bases == "False":
            opts.append("--dont-use-soft-clipped-bases")

        # Generating command for HaplotypeCaller
        return "{0} HaplotypeCaller {1} !LOG3!".format(gatk_cmd, " ".join(opts))

class PrintReads(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(PrintReads, self).__init__(module_id, is_docker)
        self.output_keys            = ["bam"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                is_required=True)
        self.add_argument("bam_idx",            is_required=True)
        self.add_argument("BQSR_report",        is_required=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2.5")

    def define_output(self):
        # Declare bam output filename
        bam = self.generate_unique_file_name(extension=".recalibrated.bam")
        self.add_output("bam", bam)

    def define_command(self):
        # Obtaining the arguments
        bam     = self.get_argument("bam")
        BQSR    = self.get_argument("BQSR_report")
        ref     = self.get_argument("ref")
        L       = self.get_argument("location")
        XL      = self.get_argument("excluded_location")
        nr_cpus = self.get_argument("nr_cpus")
        output_bam = self.get_output("bam")
        gatk_cmd = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Generating the PrintReads caller options
        opts = list()
        opts.append("-I %s" % bam)
        opts.append("{0} {1}".format(output_file_flag, output_bam))
        opts.append("-nct %d" % nr_cpus)
        opts.append("-R %s" % ref)
        opts.append("-BQSR %s" % BQSR)

        # Limit the locations to be processed
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    opts.append("-L \"%s\"" % included)
            else:
                opts.append("-L \"%s\"" % L)
        if XL is not None:
            if isinstance(XL, list):
                for excluded in XL:
                    opts.append("-XL \"%s\"" % excluded)
            else:
                opts.append("-XL \"%s\"" % XL)

        # Generating command for GATK PrintReads
        return "%s PrintReads %s !LOG3!" % (gatk_cmd, " ".join(opts))

class ApplyBQSR(_GATKBase):
    # GATK 4 replacement for PrintReads
    def __init__(self, module_id, is_docker=False):
        super(ApplyBQSR, self).__init__(module_id, is_docker)
        self.output_keys            = ["bam", "bam_idx"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                is_required=True)
        self.add_argument("bam_idx",            is_required=True)
        self.add_argument("BQSR_report",        is_required=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2.5")

    def define_output(self):
        # Declare bam output filename
        bam = self.generate_unique_file_name(extension=".recalibrated.bam")
        bam_idx = "{0}.bai".format(bam)
        self.add_output("bam", bam)
        self.add_output("bam_idx", bam_idx)

    def define_command(self):
        # Obtaining the arguments
        bam     = self.get_argument("bam")
        BQSR    = self.get_argument("BQSR_report")
        ref     = self.get_argument("ref")
        L       = self.get_argument("location")
        XL      = self.get_argument("excluded_location")
        output_bam      = self.get_output("bam")
        output_bam_idx  = self.get_output("bam_idx")
        tmp_bam_idx     = str(output_bam_idx).replace(".bam.bai", ".bai")
        gatk_cmd        = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Generating the ApplyBQSR caller options
        opts = list()
        opts.append("-I %s" % bam)
        opts.append("{0} {1}".format(output_file_flag, output_bam))
        opts.append("-R %s" % ref)
        opts.append("--bqsr-recal-file %s" % BQSR)

        # Limit the locations to be processed
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    opts.append("-L \"%s\"" % included)
            else:
                opts.append("-L \"%s\"" % L)
        if XL is not None:
            if isinstance(XL, list):
                for excluded in XL:
                    opts.append("-XL \"%s\"" % excluded)
            else:
                opts.append("-XL \"%s\"" % XL)

        # Generating command for GATK PrintReads
        bqsr_cmd = "%s ApplyBQSR %s !LOG3!" % (gatk_cmd, " ".join(opts))
        mv_cmd = "mv %s %s !LOG2!" % (tmp_bam_idx, output_bam_idx)
        return "%s ; %s" % (bqsr_cmd, mv_cmd)

class BaseRecalibrator(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(BaseRecalibrator, self).__init__(module_id, is_docker)
        self.output_keys    = ["BQSR_report"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                is_required=True)
        self.add_argument("bam_idx",            is_required=True)
        self.add_argument("dbsnp",              is_required=True, is_resource=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=4)
        self.add_argument("mem",                is_required=True, default_value=12)

    def define_output(self):
        # Declare BQSR report file
        bqsr_report = self.generate_unique_file_name(extension=".grp")
        self.add_output("BQSR_report", bqsr_report)

    def define_command(self):
        # Get arguments needed to generate GATK BQSR command
        bam             = self.get_argument("bam")
        ref             = self.get_argument("ref")
        dbsnp           = self.get_argument("dbsnp")
        L               = self.get_argument("location")
        XL              = self.get_argument("excluded_location")
        nr_cpus         = self.get_argument("nr_cpus")
        gatk_version    = self.get_argument("gatk_version")
        bqsr_report     = self.get_output("BQSR_report")

        gatk_cmd        = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Generating the base recalibration options
        opts = list()
        opts.append("-I %s" % bam)
        opts.append("{0} {1}".format(output_file_flag, bqsr_report))
        opts.append("-R %s" % ref)
        if gatk_version >= 4:
            opts.append("--known-sites %s" % dbsnp)
        else:
            opts.append("-knownSites %s" % dbsnp)
            opts.append("-nct %d" % nr_cpus)
            opts.append("-cov ReadGroupCovariate")
            opts.append("-cov QualityScoreCovariate")
            opts.append("-cov CycleCovariate")
            opts.append("-cov ContextCovariate")

        # Limit the locations to be processed
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    opts.append("-L \"%s\"" % included)
            else:
                opts.append("-L \"%s\"" % L)
        if XL is not None:
            if isinstance(XL, list):
                for excluded in XL:
                    opts.append("-XL \"%s\"" % excluded)
            else:
                opts.append("-XL \"%s\"" % XL)

        # Generating command for base recalibration
        return "{0} BaseRecalibrator {1} !LOG3!".format(gatk_cmd, " ".join(opts))

class IndexVCF(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(IndexVCF, self).__init__(module_id, is_docker)
        self.output_keys  = ["vcf", "vcf_idx"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("vcf",               is_required=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value=13)

    def define_output(self):
        # Declare merged GVCF output filename
        vcf = self.generate_unique_file_name(extension=".vcf")
        self.add_output("vcf", vcf)
        # Declare GVCF index output filename
        vcf_idx = vcf + ".idx"
        self.add_output("vcf_idx", vcf_idx)

    def define_command(self):
        # Obtaining the arguments
        vcf_in  = self.get_argument("vcf")
        gatk    = self.get_argument("gatk")
        ref     = self.get_argument("ref")
        mem     = self.get_argument("mem")
        vcf_out = self.get_output("vcf")

        # Generate command with java if not running on docker
        java = self.get_argument("java")
        jvm_options = "-Xmx%dG -Djava.io.tmpdir=%s" % (mem * 4 / 5, "/tmp/")
        cmd = "%s %s -cp %s org.broadinstitute.gatk.tools.CatVariants" % (java, jvm_options, gatk)

        # Generating the CatVariants options
        opts = list()
        opts.append("-out {0}".format(vcf_out))
        opts.append("-R %s" % ref)
        opts.append("-V %s" % vcf_in)

        # Generating the IndexVCF cmd
        return "%s %s !LOG3!" % (cmd, " ".join(opts))

class FilterMutectCalls(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(FilterMutectCalls, self).__init__(module_id, is_docker)
        self.output_keys    = ["vcf"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("vcf",        is_required=True)
        self.add_argument("nr_cpus",    is_required=True,   default_value=1)
        self.add_argument("mem",        is_required=True,   default_value=2)

    def define_output(self):
        # Declare recoded VCF output filename
        vcf_out = self.generate_unique_file_name(extension=".vcf")
        self.add_output("vcf", vcf_out)

    def define_command(self):
        # Get input arguments
        vcf_in      = self.get_argument("vcf")
        gatk_cmd    = self.get_gatk_command()
        vcf_out     = self.get_output("vcf")

        output_file_flag = self.get_output_file_flag()

        return "{0} FilterMutectCalls -V {1} {3} {2} !LOG3!".format(gatk_cmd, vcf_in, vcf_out, output_file_flag)

class CollectReadCounts(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(CollectReadCounts, self).__init__(module_id, is_docker)
        self.output_keys = ["read_count_out"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",            is_required=True)
        self.add_argument("bam_idx",        is_required=True)
        self.add_argument("nr_cpus",        is_required=True,   default_value=1)
        self.add_argument("mem",            is_required=True,   default_value=2)

    def define_output(self):
        # Declare recoded VCF output filename
        read_count_out = self.generate_unique_file_name(extension=".read_count.txt")
        self.add_output("read_count_out", read_count_out)

    def define_command(self):
        # Get input arguments
        bam             = self.get_argument("bam")
        gatk_cmd        = self.get_gatk_command()
        read_count_out  = self.get_output("read_count_out")
        interval_list   = self.get_argument("interval_list")

        output_file_flag = self.get_output_file_flag()

        cmd = "{0} CollectReadCounts -I {1} {3} {2} --format TSV ".format(gatk_cmd, bam, read_count_out, output_file_flag)

        if interval_list is not None:
            cmd = "{0} -L {1} --interval-merging-rule OVERLAPPING_ONLY".format(cmd, interval_list)

        return "{0} !LOG3!".format(cmd)

class BedToIntervalList(_GATKBase):
    def __init__(self, module_id, is_docker=False):
        super(BedToIntervalList, self).__init__(module_id, is_docker)
        self.output_keys = ["interval_list"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bed",        is_required=True, is_resource=True)
        self.add_argument("nr_cpus",    is_required=True, default_value=1)
        self.add_argument("mem",        is_required=True, default_value=2)

    def define_output(self):
        # Declare recoded VCF output filename
        interval_list = self.generate_unique_file_name(extension=".interval.list")
        self.add_output("interval_list", interval_list)

    def define_command(self):

        # Get input arguments
        bed             = self.get_argument("bed")
        dict_file       = self.get_argument("ref_dict")
        gatk_cmd        = self.get_gatk_command()
        interval_list   = self.get_output("interval_list")

        output_file_flag = self.get_output_file_flag()

        return "{0} BedToIntervalList -I {1} {4} {2} -SD {3} !LOG3!".format(gatk_cmd, bed, interval_list, dict_file,
                                                                            output_file_flag)

class GenotypeGenomicsDB(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(GenotypeGenomicsDB, self).__init__(module_id, is_docker)
        self.output_keys = ["vcf", "vcf_idx"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("genomicsDB", is_required=True)
        self.add_argument("nr_cpus",    is_required=True, default_value=4)
        self.add_argument("mem",        is_required=True, default_value=16)

    def define_output(self):
        # Declare VCF output filename
        vcf = self.generate_unique_file_name(extension=".vcf")
        self.add_output("vcf", vcf)
        # Declare VCF index output filename
        vcf_idx = self.generate_unique_file_name(extension=".vcf.idx")
        self.add_output("vcf_idx", vcf_idx)

    def define_command(self):
        # Get input arguments
        genomics_db = self.get_argument("genomicsDB")
        ref         = self.get_argument("ref")
        L           = self.get_argument("location")
        vcf         = self.get_output("vcf")

        # Make JVM options and GATK command
        gatk_cmd = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Generating the haplotype caller options
        opts = list()

        if isinstance(genomics_db, list):
            for gdb in genomics_db:
                opts.append("-V gendb://{0}".format(gdb))
        else:
            opts.append("-V gendb://{0}".format(genomics_db))

        opts.append("{1} {0}".format(vcf, output_file_flag))
        opts.append("-R {0}".format(ref))

        # Limit the locations to be processes
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    opts.append("-L \"%s\"" % included)
            else:
                opts.append("-L \"%s\"" % L)

            # Add option to restrict vcf to intervals
            opts.append("--only-output-calls-starting-in-intervals")

        # Generating command for base recalibration
        return "{0} GenotypeGVCFs {1} !LOG3!".format(gatk_cmd, " ".join(opts))

class SplitNCigarReads(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(SplitNCigarReads, self).__init__(module_id, is_docker)
        self.output_keys  = ["bam"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                is_required=True)
        self.add_argument("bam_idx",            is_required=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2.5")

    def define_output(self):
        # Declare BAM output filename
        bam = self.generate_unique_file_name(extension=".split.bam")
        self.add_output("bam", bam)

    def define_command(self):
        # Get arguments needed to generated a SplitNCigarReads command
        bam        = self.get_argument("bam")
        output_bam = self.get_output("bam")
        ref        = self.get_argument("ref")
        gatk_version = self.get_argument("gatk_version")

        # Get JVM options and GATK command
        gatk_cmd = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Generating the options for splitting reads with N in cigar string
        opts = list()
        opts.append("-R {0}".format(ref))
        opts.append("-I {0}".format(bam))
        opts.append("{0} {1}".format(output_file_flag, output_bam))

        # Determine numeric version of GATK to see if GATK3 options should be added
        gatk_version = str(gatk_version).lower().replace("gatk","")
        gatk_version = gatk_version.strip()
        gatk_version = int(gatk_version.split(".")[0])

        if gatk_version < 4:
            opts.append("-rf ReassignOneMappingQuality")
            opts.append("-RMQF 255")
            opts.append("-RMQT 60")
            opts.append("-U ALLOW_N_CIGAR_READS")

        # Generate command for splitting reads
        return "{0} SplitNCigarReads {1} !LOG3!".format(gatk_cmd, " ".join(opts))

class Mutect2(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(Mutect2, self).__init__(module_id, is_docker)
        self.output_keys = ["vcf", "vcf_idx"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bam",                is_required=True)
        self.add_argument("bam_idx",            is_required=True)
        self.add_argument("sample_name",        is_required=True)
        self.add_argument("is_tumor",           is_required=True)
        self.add_argument("germline_vcf",       is_required=False,  is_resource=True)
        self.add_argument("nr_cpus",            is_required=True,   default_value=8)
        self.add_argument("mem",                is_required=True,   default_value=30)

    def define_output(self):
        # Declare VCF output filename
        vcf = self.generate_unique_file_name(extension=".vcf")
        self.add_output("vcf", vcf)
        # Declare VCF index output filename
        vcf_idx = self.generate_unique_file_name(extension=".vcf.idx")
        self.add_output("vcf_idx", vcf_idx)

    def define_command(self):
        # Get input arguments
        bams            = self.get_argument("bam")
        ref             = self.get_argument("ref")
        germline_vcf    = self.get_argument("germline_vcf")
        L               = self.get_argument("location")
        XL              = self.get_argument("excluded_location")
        nr_cpus         = self.get_argument("nr_cpus")
        interval        = self.get_argument("interval_list")
        bed             = self.get_argument("bed")

        vcf = self.get_output("vcf")

        gatk_cmd        = self.get_gatk_command()

        output_file_flag = self.get_output_file_flag()

        # Get sample names and tumor status
        sample_names, is_tumor = self.__process_samples()

        # Generating the Mutect2 options
        opts = list()

        # Add Tumor/Normal sample names
        if is_tumor[0]:
            opts.append("-tumor %s" % sample_names[0])
            opts.append("-normal %s" % sample_names[1])
        else:
            opts.append("-tumor %s" % sample_names[1])
            opts.append("-normal %s" % sample_names[0])

        def flatten(lis):
            """Given a list, possibly nested to any level, return it flattened."""
            new_lis = []
            for item in lis:
                if type(item) == type([]):
                    new_lis.extend(flatten(item))
                else:
                    new_lis.append(item)
            return new_lis

        # Add arguments for bams
        bams = flatten(bams)
        opts.extend(["-I %s" % bam for bam in bams])

        opts.append("{0} {1}".format(output_file_flag, vcf))
        opts.append("-R %s" % ref)
        opts.append("--native-pair-hmm-threads %s" % nr_cpus)

        if germline_vcf is not None:
            opts.append("--germline-resource %s" % germline_vcf)

        # Limit the locations to be processes
        if L is not None:
            if isinstance(L, list):
                for included in L:
                    if included != "unmapped":
                        opts.append("-L \"%s\"" % included)
            else:
                opts.append("-L \"%s\"" % L)
        if XL is not None:
            if isinstance(XL, list):
                for excluded in XL:
                    opts.append("-XL \"%s\"" % excluded)
            else:
                opts.append("-XL \"%s\"" % XL)

        # Check if an interval list was provided and if yes, place it
        if interval is not None:
            opts.append("-L {0}".format(interval))

        # Check if a BED file was provided and if yes, place it
        if bed is not None:
            opts.append("-L {0}".format(bed))

        # Generating command for Mutect2
        return "{0} Mutect2 {1} !LOG3!".format(gatk_cmd, " ".join(opts))

    def __process_samples(self):

        # Generate a dictionary that will contain the samples and their tumor status
        tumor_status = {}

        # Get samples and tumor status
        sample_names = self.get_argument("sample_name")
        is_tumor = self.get_argument("is_tumor")

        # Add each sample to the tumor status dictionary
        for _name, _tumor in zip(sample_names, is_tumor):

            # Extract the sample ID
            _id = _name.rsplit("_", 1)[0]

            # Check if the current sample id has already been introduced but with a different tumor status
            if _id in tumor_status and tumor_status[_id] != _tumor:
                logging.error("Same sample ID '%s' was provided as different tumor statuses!" % _id)
                raise RuntimeError("Same sample ID '%s' was provided as different tumor statuses!" % _id)

            # If we have not stopped, just added it (possibly again) in the dictionary
            tumor_status[_id] = _tumor

        return tumor_status.keys(), tumor_status.values()

class PreprocessIntervals(_GATKBase):

    def __init__(self, module_id, is_docker=False):
        super(PreprocessIntervals, self).__init__(module_id, is_docker)
        self.output_keys = ["interval_list"]

    def define_input(self):
        self.define_base_args()
        self.add_argument("bin_length",             is_required=True, default_value=0)
        self.add_argument("nr_cpus",                is_required=True, default_value=1)
        self.add_argument("mem",                    is_required=True, default_value=2)

    def define_output(self):
        # Declare interval list output filename
        interval_list = self.generate_unique_file_name(extension=".interval.list")
        self.add_output("interval_list", interval_list)

    def define_command(self):
        # Get input arguments
        L                       = self.get_argument("location")
        bin_length              = self.get_argument("bin_length")
        ref                     = self.get_argument("ref")

        # Get output arguments
        interval_list = self.get_output("interval_list")

        # Get the output file flag depends on GATK version
        output_file_flag = self.get_output_file_flag()

        # Get GATK base command
        gatk_cmd = self.get_gatk_command()

        # Generate the command line for PreProcessIntervals
        cmd = "{0} PreprocessIntervals -R {1} --bin-length {2} {3} {4}".format(gatk_cmd, ref, bin_length,
                                                                               output_file_flag, interval_list)

        # pass the location to include in the processing
        if L is not None:
            cmd = "{0} -L {1} --interval-merging-rule OVERLAPPING_ONLY".format(cmd, L)

        return "{0} !LOG3!".format(cmd)