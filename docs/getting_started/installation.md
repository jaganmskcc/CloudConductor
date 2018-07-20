# Installation

This section helps to get the **CloudConductor** up and running on your local machine. There are two ways in which you
 can install **CloudConductor** on your local Linux running system.
  * [Install from source](#install-from-source)
  * [Install from Docker Hub](#install-from-docker-hub)

If you want to run your workflows on [Google Cloud Platform], please refer to the section 
[Install Google Cloud platform SDK](#install-google-cloud-platform-SDK).

## Install from source

### Pre-requisites
  * Linux OS
  * Python v.2.7.*
  * Git

Following tools are required to run your workflows using **CloudConductor**:  

  1. [Python] v2.7.*

      You can check your pre-installed Python version by running the following command in your terminal:

      ```bash
      $ python -V
      Python 2.7.10
      ```

      To install the correct version of Python, visit the official [Python website].

  2. Python packages: *configobj*, *jsonschema*, *requests*

      You will need [pip] to install the above packages. After installing **pip**, run the following commands in your 
      terminal: 

      ```bash
      # Upgrade pip
      sudo pip install -U pip
    
      # Install Python modules
      sudo pip install -U configobj jsonschema requests
      ```

  3. Git

      Please follow the instructions on official [Git] website to download and install **Git** on your local system.
  
  4. Download the **CloudConductor** repository from the **GitHub** by executing following command line:
  
    ```bash
    $ git clone https://github.com/labdave/CloudConductor.git
    ``` 

## Install from Docker Hub

The only pre-requisite here is the [Docker] client. Please execute the following command line to see if your system 
already have Docker-client installed or not.

```bash
$ sudo docker --version
``` 

If the Dcoker is not installed on your system, you can get it from the website of [Docker-client]. 

After the Docker set up, please pull the **CloudConductor** Docker image from the [Docker Hub]. To do so, please run 
the following command line:

```bash
$ sudo docker pull davelabhub/cloudconductor
```

You can run **CloudConductor** as Docker container as follows:

```bash
$ sudo docker run --rm --user root davelabhub/cloudconductor "cloudconductor --help"
``` 

## Install Google Cloud Platform SDK

Follow the [instructions] on the official Google Cloud website.

[Python]: (https://www.python.org/)
[Python website]: (https://www.python.org/downloads/)
[pip]: (https://packaging.python.org/guides/installing-using-linux-tools/)
[Git]: (https://git-scm.com/downloads)
[Google Cloud Platform]: (https://cloud.google.com/)
[instructions]: (https://cloud.google.com/sdk/docs/downloads-interactive)
[Docker]: (https://www.docker.com/)
[Docker-client]: (https://docs.docker.com/install/)
[Docker Hub]: (https://hub.docker.com/)
