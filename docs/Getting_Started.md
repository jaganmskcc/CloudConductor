# Getting Started

There are two ways in which you can install and use **CloudConductor**.

  * [Install using Docker](#install-using-docker)
  * [Install from source](#install-from-source)

## Install using Docker

### Prepare your system

You will need to install Docker in order to use the **CloudConductor** image. 
Please follow the instructions from Docker's [official website](https://docs.docker.com/install/)

### Running **CloudConductor**

Currently, **CloudConductor** is available on `davelab` DockerHub. You can run it using the following command:

```bash
sudo docker run -it davelab/cloudconductor "cloudconductor --help"
```

## Install from source

### Prepare your system

**CloudConductor** is currently designed only for *Linux* systems. 
You will need to install and configure the following tools to run your pipelines on Google Cloud:  

1. [Python](https://www.python.org/) v2.7.*

    You can check your Python version by running the following command in your terminal:

    ```
    $ python -V
    Python 2.7.10
    ```

    To install the correct version of Python, visit the official Python [website](https://www.python.org/downloads/).

2. Python packages: *configobj*, *jsonschema*, *requests*

    You will need [pip](https://packaging.python.org/guides/installing-using-linux-tools/) to install the above packages.
    After installing *pip*, run the following commands in your terminal: 

    ```bash
    # Upgrade pip
    sudo pip install -U pip
    
    # Install Python modules
    sudo pip install -U configobj jsonschema requests
    ```

3. [Google Cloud Platform](https://cloud.google.com/) SDK

    Follow the [instructions](https://cloud.google.com/sdk/docs/downloads-interactive) on the official Google Cloud website.

4. Git

    Follow the [instructions](https://git-scm.com/downloads) on the offical Git website.

### Running **CloudConductor**

First you need to clone to repository locally and than you can run **CloudConductor**.

```bash
# Clone the repository locally
git clone https://github.com/davelab/CloudConductor

# Enter the project directory
cd CloudConductor

# Run CloudConductor
./CloudConductor --help
```
