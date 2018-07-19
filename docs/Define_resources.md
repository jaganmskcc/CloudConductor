# 2. Define resources

In **CloudConductor**, resources are defined by a configuration file named *resource kit*.
This section will explain how to create a resource kit.

Every resource kit is divided in two large sections.
The first section is named ***Docker*** and defines resources provided through *Docker*.
The second section is named ***PATH*** and defines resources available on an external storage system such as Google Cloud Storage.

Each resource is defined by a *resource type*, a *path* and sometimes a *containing directory*.

The **resource type** is represented in the resource kit by the keyword ***resource_type***. It is  should be the same as the *input key* of a pipeline module that uses the specific resource.
For example, submodule `Index` from module `Samtools` has one input key, named *samtools* that defines the required resource type.
Consequently, the resource of type *samtools* will be connected to the input key *samtools* from submodule `Index`.

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

You can also use the resources 

### What is a resource kit?

### How to create a resource kit?

### Examples