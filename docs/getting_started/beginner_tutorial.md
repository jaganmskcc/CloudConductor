# Beginner's Tutorial

## Pre-requisites
Following are the requirments before you can use the **CloudConductor**. Please make sure your system is properly 
setup for **CloudConductor**.
  * Linux OS
  * Python v.2.7.*
  * CloudConductor
  * Google Cloud SDK
  
If you have any question about the installation of required tools, please refer to our [Installation] section which 
helps you to set up your system for **CloudConductor**.

## Running **CloudConductor**

The **CloudConductor** reuires four types of configuration files as follows:
  * [Workflow config](#prepare-workflow-config)
  * [Resource Kit config](#prepare-resource-kit-config)
  * [Platform config](#prepare-platform-config)
  * [Sample Sheet](#prepare-sample-sheet)

### Prepare Workflow Config
The workflow configuration exemplifies your data processing steps, where output of one tools becomes input of 
consecutive tool. Following is workflow example which takes a raw `FASTQ` files from `RNAseq` experiment, perform 
QC, and align to the Human reference genome to produce the aligned reads as `BAM` file. You can refer to [Workflow 
fundamentals] for more details.

```ini
[split_samples]
module = SampleSplitter

[fastqc]
module          = FastQC
docker_image    = fastqc
input_from      = split_samples
final_output    = R1_fastqc, R2_fastqc

[trimmomatic]
module          = Trimmomatic
docker_image    = trimmomatic
input_from      = split_samples
final_output    = trim_report
    [[args]]
        MINLEN  = 25

[star_bam]
module          = Star
docker_image    = star
input_from      = trimmomatic
final_output    = bam, transcriptome_mapped_bam, raw_read_counts, final_log
   [[args]]
        ref     = star_genome_dir

[star_bam_index]
module          = Samtools
docker_image    = samtools
submodule       = Index
input_from      = star_bam
final_output    = bam_idx
```

### Prepare Resource Kit Config
The resource kit configuration defines the resources needed to run your workflow. The resouces can be path to the 
reference files, tool executables, docker images, etc. Following is a resource kit example containing all the required
 resource to produce aligned reads from raw `FASTQ` file for a `RNAseq` experiment. You can refer to [Resouce Kit 
fundamentals] for more details.

```ini
[Docker]
    [[fastqc]]
        image = quay.io/biocontainers/fastqc:0.11.7--pl5.22.0_2
        [[[fastqc]]]
            resource_type   = fastqc
            path            = fastqc
    [[trimmomatic]]
        image = quay.io/biocontainers/trimmomatic:0.36--5
        [[[trimmomatic]]]
            resource_type   = trimmomatic
            path            = trimmomatic
    [[star]]
        image = quay.io/biocontainers/star:2.6.0b--0
        [[[star]]]
            resource_type   = star
            path            = STAR
    [[samtools]]
        image = quay.io/biocontainers/samtools:1.8--3
        [[[samtools]]]
            resource_type   = samtools
            path            = samtools
[Path]
    [[adapters]]
        resource_type   = adapters
        path            = gs://davelab_data/tools/Trimmomatic_0.36/adapters/adapters.fa
    [[star_genome_dir]]
       resource_type   = ref
       path            = gs://davelab_data/ref/hg19/RNA/star
    [[ref]]
        resource_type   = ref
        path            = gs://davelab_data/ref/hg19/RNA/ensembl.hg19.release84.fa
```

### Prepare Platform Config
The platform configuration defines the runtime platform for the **CloudConductor** to run your workflow. The 
`Platform Config` set several things for the runtime platform such as which zone, service account key, maximun 
retires for command execution, etc. Following is a example of `Platform Config` to run on the workflow on [Google Cloud 
Platform]. You can refer to [Platform fundamentals] for more details.

```ini
zone                        = us-east1-c
randomize_zone              = False
service_account_key_file    = var/GAP_new.json
report_topic                = pipeline_reports

[task_processor]
disk_image                  = davelab-image-docker
max_reset                   = 3
is_preemptible              = True
cmd_retries                 = 1
apt_packages                = pigz
```

### Prepare Sample Sheet
The sample sheet provide sample information to the **CloudConductor**. The sample information such as the 
type of the sample (i.e. tumor, normal), sequencing platform on which the sample were sequenced, path to the sample 
raw data, etc. Following is sample sheet example. You can refer to [Sample Sheet fundamentals] for more details.

```json
{
  "paired_end": true,
  "seq_platform": "Illumina",
  "samples": [
    {
      "name": "s1",
      "paths": {
        "R1": "gs://your_desired_loc/s1_1_I13_0124.fastq.gz",
        "R2": "gs://your_desired_loc/s1_2_I13_0124.fastq.gz"
      },
      "is_tumor": false,
      "lib_name": "LIB_NAME"
    },
    {
      "name": "s2",
      "paths": {
        "R1": "gs://your_desired_loc/s2_1_I13_0124.fastq.gz",
        "R2": "gs://your_desired_loc/s2_2_I13_0124.fastq.gz"
      },
      "is_tumor": false,
      "lib_name": "LIB_NAME"
    }
  ]
}
```

Once, you have preapared all the required files you can run the **CloudConductor** as follows:

```bash
$ ./CloudConductor --name cc_run_1 \
                   --input sample_sheet.json \
                   --pipeline_config workflow.config \
                   --res_kit_config res_kit.config \
                   --plat_config gcp_platform.config \
                   --plat_name Google \
                   --output_dir gs://your_desired_loc/cc_run_1/ \
                   -vvv
```

[Installation]: (installation.md)
[Workflow fundamentals]: (../fundamentals/creating_a_workflow.md)
[Resouce Kit fundamentals]: (../fundamentals/defining_a_resource_kit.md)
[Platform fundamentals]: (../fundamentals/defining_the_runtime_platform.md)
[Sample Sheet fundamentals]: (../fundamentals/creating_a_sample_sheet.md)
[Google Cloud Platform]: (https://cloud.google.com/)
