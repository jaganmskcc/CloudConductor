<div align=center><img src="docs/_static/cloud-conductor-logo-colored.png" alt="Derp" width=450 height=225 align="middle"/></div>

## What is CloudConductor?

**CloudConductor** is a cloud-based workflow engine for defining and executing bioinformatics pipelines in a cloud environment. 
Currently, the framework has been tested extensively on the [Google Cloud Platform](https://cloud.google.com/), but will eventually support other platforms including AWS, Azure, etc.

## Feature Highlights

  * **User-friendly**
    * Define complex workflows by linking together user-defined modules that can be re-used across pipelines
    * [Config_obj](http://configobj.readthedocs.io/en/latest/configobj.html) for clean, readable workflows (see below example)
    * 50+ pre-installed modules for existing bioinformatics tools
  * **Portable**
    * Docker integration ensures reproducible runtime environment for modules    
    * Platform independent (currently supports GCS; AWS, Azure to come)
  * **Modular/Extensible**
    * User-defined Plug-N-Play modules
      * Re-used across pipelines, re-combined in any combination
      * Modules easily added, customized as new tools needed, old tools changed
      * Eliminates copy/paste re-use of code across workflows 
  * **Pre-Launch Type-Checking**
    * Strongly-typed module declarations allow catching pipeline errors before they occur
    * Pre-launch checks make sure all external files exist before runtime
  * **Scalable**
    * Removes resource limitations imposed by cluster-based HPCCs
  * **Elastic**
    * VM usage automatically scales to match input file sizes, computational needs
  * **Scatter-Gather Parallelism**
    * In-built logic for dividing large tasks into small chunks and re-combining
  * **Economical**
    * Preemptible/Spot instances drastically cut workflow costs

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

3. Clone the **CloudConductor** repo

    ```sh
    # clone the repo
    git clone https://github.com/labdave/CloudConductor.git
    ```

4. [Google Cloud Platform](https://cloud.google.com/) SDK

    Follow the [instructions](https://cloud.google.com/sdk/docs/downloads-interactive) on the official Google Cloud website.

## Documentation

Get started with our full [documentation](https://cloudconductor.readthedocs.io) to explore the ways CloudConductor can streamline the development and execution of complex, multi-sample workflows typical in bioinformatics.

## Project Status

CloudConductor is actively under development. To get involved or request features, please contact any of the authors listed below.

## Authors

* [Alex Waldrop](https://github.com/alexwaldrop)
* [Razvan Panea](https://github.com/ripanea)
* [Tushar Dave](https://github.com/tushardave26)
