from Modules import Module

class ABCGCBClassifier(Module):
    def __init__(self, module_id, is_docker = False):
        super(ABCGCBClassifier, self).__init__(module_id, is_docker)
        self.output_keys = ["classification_report"]

    def define_input(self):
        self.add_argument("sample_name",        is_required=True)
        self.add_argument("genes_results",       is_required=True)
        self.add_argument("ref",                is_required=True, is_resource=True)
        self.add_argument("classifier",         is_required=True, is_resource=True)
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value="nr_cpus * 2")

    def define_output(self):

        # Declare unique file name
        self.add_output("classification_report", "ABC_GCB_gene_expr.pdf")

    def define_command(self):

        # Get arguments
        sample          = self.get_argument("sample_name")
        ref             = self.get_argument("ref")
        expression_file = self.get_argument("genes_results")

        #get the classifier script or docker image name
        classifier      = self.get_argument("classifier")

        #get the output file and make appropriate path for it
        #output_file     = self.get_output("classification_report")

        if not self.is_docker:
            cmd = "sudo Rscript --vanilla {0} -e {1} -s {2} -r {3} !LOG3!".format(classifier, expression_file, sample,
                                                                                  ref)
        else:
            cmd = "Rscript --vanilla $(which {0}) -e {1} -s {2} -r {3} !LOG3!".format(classifier, expression_file,
                                                                                    sample, ref)

        return cmd