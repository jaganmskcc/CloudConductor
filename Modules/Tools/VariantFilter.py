import os
from Modules import Module

class VariantFilter(Module):
    def __init__(self, module_id, is_docker = False):
        super(VariantFilter, self).__init__(module_id, is_docker)
        self.output_keys = ["filter_variants_text", "filter_variants_json", "subset_filter_variants_text"]

    def define_input(self):
        self.add_argument("sample_name",        is_required=True)
        self.add_argument("recoded_vcf",        is_required=True)
        self.add_argument("mutation_level",     is_required=True, default_value=0.3)
        self.add_argument("wt",                 is_required=True, default_value=(-0.4))
        self.add_argument("filter_script",      is_required=True, is_resource=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2")

    def define_output(self):

        # Get the sample name
        sample_name = self.get_argument("sample_name")

        # Declare unique file name
        filter_variants_text_file_name = self.generate_unique_file_name(extension="{0}.Filtered_variants.txt".format(sample_name))
        filter_variants_json_file_name = self.generate_unique_file_name(extension="{0}.Filtered_variants.json".format(sample_name))
        subset_filter_variants_text_file_name = self.generate_unique_file_name(extension="{0}.Filtered_variants_sel_columns.txt".format(sample_name))

        # Declare unique file name
        self.add_output("filter_variants_text", filter_variants_text_file_name)
        self.add_output("filter_variants_json", filter_variants_json_file_name)
        self.add_output("subset_filter_variants_text", subset_filter_variants_text_file_name)

    def define_command(self):

        # Get arguments
        sample          = self.get_argument("sample_name")
        recoded_vcf     = self.get_argument("recoded_vcf")
        mutation_level  = self.get_argument("mutation_level")
        wt              = self.get_argument("wt")

        #get the classifier script or docker image name
        filter_script      = self.get_argument("filter_script")

        #get the output file and make appropriate path for it
        filter_variants_text_file_name = self.get_output("filter_variants_text")
        filter_variants_json_file_name = self.get_output("filter_variants_json")
        subset_filter_variants_text_file_name = self.get_output("subset_filter_variants_text")

        if not self.is_docker:
            cmd = "sudo Rscript --vanilla {0} -v {1} -s {2} -m {3} -w {4} -f {5} -j {6} -a {7} !LOG3!".format(
                filter_script, recoded_vcf, sample, mutation_level, wt, filter_variants_text_file_name,
                filter_variants_json_file_name, subset_filter_variants_text_file_name)
        else:
            cmd = "Rscript --vanilla {0} -v {1} -s {2} -m {3} -w {4} -f {5} -j {6} -a {7} !LOG3!".format(
                filter_script, recoded_vcf, sample, mutation_level, wt, filter_variants_text_file_name,
                filter_variants_json_file_name, subset_filter_variants_text_file_name)

        return cmd