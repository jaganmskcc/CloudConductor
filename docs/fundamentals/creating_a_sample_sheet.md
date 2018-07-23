# Creating a sample sheet

In **CloudConductor**, the main input of a pipeline is specified in a ***sample sheet***.
Except three mandatory keys (*samples*, *name*, *paths*) any additional input keys specified in the sample sheet 
are related to the modules used in the pipeline graph.

The sample sheet is in JSON format and its template is as following:

```json
{
    "samples": 
    [
        {
            "name": *name_of_sample1*,
            "paths": {
                *input_path_key1*: *path1*,
                *input_path_key2*: *path2*,
                ... 
            }
            *sample_specific_input_key1*: *value_key1*,
            *sample_specific_input_key2*: *value_key2*,
            ...
        },
        ...
    ],
    *general_input_key1*: *value1*,
    *general_input_key2*: *value2*,
    ...
}
```

In the above template, the keys ***samples***, ***name*** and ***paths*** are mandatory as 
they specify a list of samples, the name of the specific sample and the file data paths of the specific sample, respectively.
You can specify any additional input keys at any level in the sample sheet, however sample-specific information
should be specified at the sample level.

Here are two example sample sheets:

```json
{
    "paired_end": true,
    "seq_platform": "Illumina",
    "samples": 
    [
        {
            "name": "S1",
            "paths": {
                "R1": "Illumina_S1_R1.fastq.gz",
                "R2": "Illumina_S2_R2.fastq.gz"
            },
            "library_name": "PREP_S1",
            "is_tumor": true
        },
        {
            "name": "S2",
            "paths":{
                "R1": "Illumina_S2_R1.fastq.gz",
                "R2": "Illumina_S2_R2.fastq.gz"
            },
            "library_name": "PREP_S2",
            "is_tumor": false
        }
    ]
}
```

````json
{
    "samples":
    [
        {
            "name": "Variant2",
            "paths": {
                "vcf": "variants_S1_S2.vcf.gz",
                "vcf_idx": "variants_S1_S2.vcf.gz.tbi"
            }
        }
    ]
}
````
