# Resource kit configuration

## Multi-tools Dockers

There are (not recommended) situations when a Docker contains two separate tools as a command requires piping from one command to another.
You can solve this problem by simply defining additional resources in a Docker image.

For example, the aligning output of `BWA` is in *SAM* format, so to convert it to a more efficient format, *BAM*, we are piping the output from `BWA` to `Samtools` to convert the output format.
Thus, we are required to have a Docker image that has both tools. Here is how you define this situation in a resource kit:

```ini
[Docker]
    [[bwa]]
        image = thd7/bwasam:v.20180522
        [[[bwa]]]
            resource_type = bwa
            path = bwa
    
        [[[samtools]]]
            resource_type = samtools
            path = samtools
```

## Multiple resources of same type

There are situations in which the user can have different definitions of the same resource type in the resource kit.
For instance, the analysis pipeline requires two different versions of the same tool.
This resource kit implementation will raise an error as CloudConductor cannot decide which resource definition of the
same resource type to choose from. Consequently, the user has to specify in the pipeline graph the exact resource name that they require.

Consider this part of a resource kit implementation as an example:

```ini
[Path]
    ...
    [[samtools_0.19]]
        resource_type=samtools
        path=samtools
        containing_dir=gs://path/to/samtools_0.19
    [[samtools_1.3]]
        resource_type=samtools
        path=samtools
        containing_dir=gs://path/to/samtools_1.3
    ...
```

... and the implementation of the pipeline graph using the above resource kit:

```ini
    ...
    [align_reads]
        module=BWA
        final_output=bam

    [bam_indexing]
        module=Samtools
        submodule=Index
        input_from=align_reads
        final_output=bam_idx
        [[args]]
            samtools=samtools_0.19

    [bam_summary]
        module=Samtools
        submodule=Flagstat
        input_from=align_reads
        final_output=flagstat
        [[args]]
            samtools=samtools_1.3
    ...
```