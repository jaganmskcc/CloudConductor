
**CloudConductor** is a *workflow management system* to generate and run computational pipelines on a cloud platform. 
Currently, the framework was extensively tested on the [Google Cloud Platform](https://cloud.google.com/) to run *computational biology* pipelines.

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

  For instructions on how to run CloudConductor, please check our [documentation](https://google.com). 

## Authors

* [Alex Waldrop](https://github.com/alexwaldrop)
* [Razvan Panea](https://github.com/ripanea)
* [Tushar Dave](https://github.com/tushardave26)

