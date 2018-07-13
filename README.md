# CloudConductor ![alt text](http://via.placeholder.com/50x50 "Logo Title Text 1")

## What is CloudConductor?

**CloudConductor** is a cloud-based workflow engine for defining and executing bioinformatics pipelines in a cloud environment. 
Currently, the framework has been tested extensively on the [Google Cloud Platform](https://cloud.google.com/).

## Feature Highlights

  * User-friendly
    * define complex workflows by linking together user-defined modules in [config_obj](http://configobj.readthedocs.io/en/latest/configobj.html) 
    * Comes with 50+ pre-built tools that can be extended/modified to your liking
  * Portable
    * Dockerizable
    * Platform independent
  * Modular/Extensible
    * Pipeline made of user-defined python classes that can be re-used, customized
  * Scalable
    * Cloud computing = you can use lots of computing
  * Pre-Launch Type-Checking
    * Will tell you before execution is run whether it will run
    * Verbose output tells you how to fix whats wrong
  * Elastic
    * resource usage scales automatically with data input size
  * Scatter-Gather Parallelism
    * In-built logic for dividing large tasks into small chunks
  * Economical
    * it's cheap

## Setting up your system
  
CloudConductor is currently designed only for *Linux* systems. 
You will need to install and configure the following tools to run your pipelines on Google Cloud:  

1. [Python](https://www.python.org/) v2.7.*

    You can check your Python version by running the following command in your terminal:

    ```sh
    $ python -V
    Python 2.7.10
    ```

    To install the correct version of Python, visit the official Python [website](https://www.python.org/downloads/).

2. Python packages: *configobj*, *jsonschema*, *requests*

    You will need [pip](https://packaging.python.org/guides/installing-using-linux-tools/) to install the above packages.
    After installing *pip*, run the following commands in your terminal: 

    ``` sh
    # Upgrade pip
    sudo pip install -U pip
    
    # Install Python modules
    sudo pip install -U configobj jsonschema requests
    ```

3. [Google Cloud Platform](https://cloud.google.com/) SDK

    Follow the [instructions](https://cloud.google.com/sdk/docs/downloads-interactive) on the official Google Cloud website.

## Usage

  For more information about CloudConductor and how to use it check the [documentation](https://google.com).

        usage: CloudConductor [-h] --input SAMPLE_SET_CONFIG --name PIPELINE_NAME
                              --pipeline_config GRAPH_CONFIG --res_kit_config
                              RES_KIT_CONFIG --plat_config PLATFORM_CONFIG --plat_name
                              PLATFORM_MODULE [-v] -o FINAL_OUTPUT_DIR
        
        optional arguments:
          -h, --help            show this help message and exit
          --input SAMPLE_SET_CONFIG
                                Path to config file containing input files and information for one or more samples.
          --name PIPELINE_NAME  Descriptive pipeline name. Will be appended to final output dir. Should be unique across runs.
          --pipeline_config GRAPH_CONFIG
                                Path to config file defining pipeline graph and tool-specific input.
          --res_kit_config RES_KIT_CONFIG
                                Path to config file defining the resources used in the pipeline.
          --plat_config PLATFORM_CONFIG
                                Path to config file defining platform where pipeline will execute.
          --plat_name PLATFORM_MODULE
                                Platform to be used. Possible values are:
                                   Google (as module 'GooglePlatform')
          -v                    Increase verbosity of the program.Multiple -v's increase the verbosity level:
                                   0 = Errors
                                   1 = Errors + Warnings
                                   2 = Errors + Warnings + Info
                                   3 = Errors + Warnings + Info + Debug
          -o FINAL_OUTPUT_DIR, --output_dir FINAL_OUTPUT_DIR
                                Absolute path to the final output directory.
                                
## Example User-Module

```python

class SamtoolsFlagstat(Module):
    def __init__(self, module_id, is_docker = False):
        """ 
        User-Defined Module for using Samtools Flagstat to compute summary statistics on a BAM file

        """

        super(Flagstat, self).__init__(module_id, is_docker)
        self.output_keys = ["flagstat"]

    def define_input(self):
        """ 
        Declares the input types expected to be able to run Samtools Flagstat
        
        """
    
        # Requires a a BAM file and index
        self.add_argument("bam",        is_required=True)
        self.add_argument("bam_idx",    is_required=True)
        
        # Requires path to samtools executable
        self.add_argument("samtools",   is_required=True, is_resource=True)
        
        # Specify runtime resources expected to run module
        self.add_argument("nr_cpus",    is_required=True, default_value=2)
        self.add_argument("mem",        is_required=True, default_value=5)

    def define_output(self):
    
        """ 
        Declares the output types and file paths produced by Samtools Flagstat
        
        """
    
        # Generate a unique filename on the fly
        flagstat = self.generate_unique_file_name(".flagstat.out")
        
        
        # Declare module produces output file of type 'flagstat' at path generated above
        self.add_output("flagstat", flagstat, is_path=True)

    def define_command(self):
    
        """ 
        Define unix command that will use the inputs at runtime to produce the declared output
        
        """
        
        # Get path of bam file provided to module at runtime
        bam         = self.get_argument("bam")
        
        # Get path of samtools executable
        samtools    = self.get_argument("samtools")
        
        # Get path of output file to be produced
        flagstat    = self.get_output("flagstat")

        # Generating and returning command
        cmd = "{0} flagstat {1} > {2}".format(samtools, bam, flagstat)
        return cmd

```


## Example User-Pipeline



## Authors

* [Alex Waldrop](https://github.com/alexwaldrop)
* [Razvan Panea](https://github.com/ripanea)
* [Tushar Dave](https://github.com/tushardave26)

