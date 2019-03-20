import os
from Modules import Module

class ABCGCBClassifier(Module):
    def __init__(self, module_id, is_docker = False):
        super(ABCGCBClassifier, self).__init__(module_id, is_docker)
        self.output_keys = ["classification_report", "gene_expr_subset_txt", "gene_expr_subset_json", "cell_of_origin_subtypes"]

    def define_input(self):
        self.add_argument("sample_name",        is_required=True)
        self.add_argument("annotated_expression_file",       is_required=True)
        self.add_argument("ref",                is_required=True, is_resource=True)
        self.add_argument("classifier",         is_required=True, is_resource=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2")

    def define_output(self):

        # Get the sample name to use it in file name creation
        sample_name = self.get_argument("sample_name")

        # Declare unique file name for output files
        classification_report = self.generate_unique_file_name(extension="{0}.ABC_GCB_gene_expr.pdf".format(sample_name))
        gene_expression_subset_txt_file = self.generate_unique_file_name(extension="{0}.Gene_expr_subset.txt".format(sample_name))
        gene_expression_subset_json_file = self.generate_unique_file_name(extension="{0}.Gene_expr_subset.json".format(sample_name))
        cell_of_origin_subtypes_file = self.generate_unique_file_name(extension="{0}.Cell_of_origin_subtypes.json".format(sample_name))

        # Declare unique file name
        self.add_output("classification_report", classification_report)
        self.add_output("gene_expr_subset_txt", gene_expression_subset_txt_file)
        self.add_output("gene_expr_subset_json", gene_expression_subset_json_file)
        self.add_output("cell_of_origin_subtypes", cell_of_origin_subtypes_file)

    def define_command(self):

        # Get arguments
        sample          = self.get_argument("sample_name")
        ref             = self.get_argument("ref")
        expression_file = self.get_argument("annotated_expression_file")

        # Get the classifier script or docker image name
        classifier      = self.get_argument("classifier")

        #get the output file and make appropriate path for it
        classification_report = self.get_output("classification_report")
        gene_expression_subset_txt_file = self.get_output("gene_expr_subset_txt")
        gene_expression_subset_json_file = self.get_output("gene_expr_subset_json")
        cell_of_origin_subtypes_file = self.get_output("cell_of_origin_subtypes")

        if not self.is_docker:
            cmd = "sudo Rscript --vanilla {0} -e {1} -s {2} -r {3} -p {4} -t {5} -j {6} -c {7} !LOG3!".format(
                classifier, expression_file, sample, ref, classification_report, gene_expression_subset_txt_file,
                gene_expression_subset_json_file, cell_of_origin_subtypes_file)
        else:
            cmd = "Rscript --vanilla {0} -e {1} -s {2} -r {3} -p {4} -t {5} -j {6} -c {7} !LOG3!".format(
                classifier, expression_file, sample, ref, classification_report, gene_expression_subset_txt_file,
                gene_expression_subset_json_file, cell_of_origin_subtypes_file)

        return cmd