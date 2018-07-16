# CloudConductor

## What is CloudConductor?

**CloudConductor** is a cloud-based workflow engine for defining and executing bioinformatics pipelines in a cloud environment. 
Currently, the framework has been tested extensively on the [Google Cloud Platform](https://cloud.google.com/), but will eventually support other platforms including AWS, Azure, etc.

## Why use CloudConductor?

**CloudConductor** comes with multiple features:

  * **User-friendly**
    * Define complex workflows by linking together user-defined modules that can be re-used across pipelines
    * [Config_obj](http://configobj.readthedocs.io/en/latest/configobj.html) for clean, readable workflows (see below example)
    * +50 pre-installed modules for existing bioinformatics tools
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

## Why you SHOULD use CloudConductor?

Here are some reasons:

  * Running 1,000 samples is as easy as running 10 samples with **CloudConductor**
  * You do not need to worry about managing your processing platform as **CloudConductor** does that all for you!
  * The protocol of your analysis pipelines will be more readible and easy to access.
    You do not need to worry about identifying the versions of the tools you used in your analysis, as they will all be in one place.

Don't believe us, [try it yourself](Getting_Started.html)!