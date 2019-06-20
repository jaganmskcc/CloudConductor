import os.path
from Modules import Module

class MultiOmicsResults(Module):
    def __init__(self, module_id, is_docker = False):
        super(MultiOmicsResults, self).__init__(module_id, is_docker)
        self.output_keys = ["all_variants", "filter_variants_text", "filter_variants_json",
                            "subset_filter_variants_text", "expr_subset", "coo_genes", "expr_subset_coo",
                            "coo_classification", "myc_bcl2_expr", "input_features", "input_combos",
                            "dist_hist_similar_patients", "survival_similar_risk"]

    def define_input(self):
        self.add_argument("sample_name",                is_required=True)
        self.add_argument("annotated_expression_file",  is_required=True)
        self.add_argument("ref_expr",                   is_required=False, is_resource=True, default_value=None)
        self.add_argument("ref_cell_model",             is_required=False, is_resource=True, default_value=None)
        self.add_argument("recoded_vcf",                is_required=True)
        self.add_argument("mutation_level",             is_required=False, default_value=0.3)
        self.add_argument("wt",                         is_required=False, default_value=-0.4)
        self.add_argument("myc_expr_threshold",         is_required=False, default_value=0.5)
        self.add_argument("bcl2_expr_threshold",        is_required=False, default_value=0.5)
        self.add_argument("meta_script",                is_required=True, is_resource=True)
        self.add_argument("nr_cpus",                    is_required=True, default_value=2)
        self.add_argument("mem",                        is_required=True, default_value="nr_cpus * 2")

    def define_output(self):

        # Get the sample name
        sample_name = self.get_argument("sample_name")

        # generate the output prefix
        output_dir = self.get_output_dir()
        output_prefix = os.path.join(output_dir, sample_name)
        
        # Declare output file name
        self.add_output("filter_variants_text", "{0}_filtered_variants.txt".format(output_prefix))
        self.add_output("filter_variants_json", "{0}_filtered_variants.json".format(output_prefix))
        self.add_output("subset_filter_variants_text", "{0}_filtered_variants_subset.txt".format(output_prefix))
        self.add_output("all_variants", "{0}_all_variants_with_filters.txt".format(output_prefix))
        self.add_output("expr_subset", "{0}_expr_subset.txt".format(output_prefix))
        self.add_output("coo_genes", "{0}_COO_genes.pdf".format(output_prefix))
        self.add_output("expr_subset_coo", "{0}_expr_subset_COO.json".format(output_prefix))
        self.add_output("coo_classification", "{0}_COO_classification.json".format(output_prefix))
        self.add_output("myc_bcl2_expr", "{0}_MYC_BCL2_expr.pdf".format(output_prefix))
        self.add_output("input_features", "{0}_input_features.txt".format(output_prefix))
        self.add_output("input_combos", "{0}_input_combos.txt".format(output_prefix))
        self.add_output("dist_hist_similar_patients", "{0}_distribution_hist_similar_patients.pdf".format(output_prefix))
        self.add_output("survival_similar_risk", "{0}_survival_similar_risk.pdf".format(output_prefix))

    def define_command(self):

        # Get arguments
        sample                      = self.get_argument("sample_name")
        annotated_expression_file   = self.get_argument("annotated_expression_file")
        ref_expr                    = self.get_argument("ref_expr")
        ref_cell_model              = self.get_argument("ref_cell_model")
        recoded_vcf                 = self.get_argument("recoded_vcf")
        mutation_level              = self.get_argument("mutation_level")
        wt                          = self.get_argument("wt")
        myc_expr_threshold          = self.get_argument("myc_expr_threshold")
        bcl2_expr_threshold         = self.get_argument("bcl2_expr_threshold")

        #get the meta script or docker image name
        meta_script      = self.get_argument("meta_script")

        # get one of the output file name prefix
        output_dir = self.get_output_dir()
        output_prefix = os.path.join(output_dir, sample)

        if not self.is_docker:
            cmd = "sudo Rscript --vanilla {0} -e {1} -m {2} -s {3} -o {4} --recodemutlevel={5} " \
                  "--recodewtlevel={6} --mycexprthreshold={7} --bcl2exprthreshold={8}".format(
                meta_script, annotated_expression_file, recoded_vcf, sample, output_prefix, mutation_level, wt,
                myc_expr_threshold, bcl2_expr_threshold)
        else:
            cmd = "Rscript --vanilla {0} -e {1} -m {2} -s {3} -o {4} --recodemutlevel={5} " \
                  "--recodewtlevel={6} --mycexprthreshold={7} --bcl2exprthreshold={8}".format(
                meta_script, annotated_expression_file, recoded_vcf, sample, output_prefix, mutation_level, wt,
                myc_expr_threshold, bcl2_expr_threshold)

        if ref_expr is not None:
            cmd = "{0} --refexpr {1}".format(cmd, ref_expr)

        if ref_cell_model is not None:
            cmd = "{0} --refcellmodel {1}".format(cmd, ref_cell_model)

        cmd = "{0} !LOG3!".format(cmd)

        return cmd
