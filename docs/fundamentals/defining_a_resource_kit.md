# Defining a resource kit

In **CloudConductor**, resources are defined by a configuration file named *resource kit*.
This section will explain how to create a resource kit.

Every resource kit is divided in two large sections.
The first section is named ***Docker*** and defines resources provided through *Docker*.
The second section is named ***PATH*** and defines resources available on an external storage system such as Google Cloud Storage.

Each resource is defined by a *resource type*, a *path* and sometimes a *containing directory*.

The **resource type** is represented in the resource kit by the __mandatory__ keyword ***resource_type***. 
It has the same value as as the *input key* of a pipeline module that uses the specific resource.
For example, submodule `Index` from module `Samtools` has one input key, named *samtools* that defines the required resource type.
Consequently, the resource of type *samtools* will be connected to the input key *samtools* from submodule `Index`.

The **executable path** is represented in the resource kit by the __mandatory__ keyword ***path***.
Its value should be the executable path (absolute, relative to the source directory or basename with '*' ) that CloudConductor will execute.

There are many examples of tools for which copying only their executable is not enough, so for these tools the entire directory needs to be transfered.
The **containing directory** of an executable is defined in the resource kit as the __optional__ keyword ***containing_dir***.
This keyword should be used when the resource requires an entire directory of dependencies in order to be functional.
When using this keyword, please ensure that the executable path specified by the keyword **path** is relative to this directory.

## Docker

As expected, when defining a resource from Docker, you will need the path to the Docker image.
Additionally, you will need to specify what resources are provided in the Docker image. 
Finally, the template of the Docker section of a resource kit is as follows:

```ini
[Docker]
    [[*unique_name_docker_resource*]]
        image=*path_docker_image*
        [[[*name_of_resource*]]]
            resource_type=*resource_input_key*
            path=*executable_path_on_docker*
```

For instance, the resource kit definition for `Trimmomatic` and `Samtools` is:

```ini
[Docker]
    [[Trimmomatic_docker]]
        image=quay.io/biocontainers/trimmomatic:0.36--5
        [[[trimmomatic]]]
            resource_type=trimmomatic
            path=trimmomatic

    [[Samtools_docker]]
        image=quay.io/biocontainers/samtools:1.8--3
        [[[samtools]]]
            resource_type=samtools
            path=samtools
```

## External Resources

In general, we highly recommend that you use resource through the Docker system as it will ensure the reproducibility of your pipeline. 
However, you can also use the resources available on an external storage system, such as Google Cloud Storage.

The template to define a resource from an external storage system is the following:

```ini
[Path]
    [[*name_of_resource*]]
        resource_type=*resource_input_key*
        path=*executable_path*
```

Here are a few examples of defined resources available only on an external storage systems:

```ini
[Path]
    [[gnomAD_exome]]
        resource_type=gnomad_ref
        path=gs://gnomad-public/release/2.0.2/vcf/exomes/gnomad.exomes.r2.0.2.sites.vcf.bgz
    [[gnomAD_exome_index]]
        resource_type=gnomad_ref_idx
        path=gs://gnomad-public/release/2.0.2/vcf/exomes/gnomad.exomes.r2.0.2.sites.vcf.bgz.tbi
    [[bwa]]
        resource_type=bwa
        path=bin/bedtools
        containing_dir=gs://path/to/bedtools/main/directory/
```
