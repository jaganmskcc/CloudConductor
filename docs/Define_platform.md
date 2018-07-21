# 3. Define the running platform

Currently, CloudConductor is implemented and tested for [Google Cloud Platform](https://cloud.google.com/),
however we are planning to develop new platform systems in the future. 

## Google Cloud Platform (GCP)

In order to use Google Cloud as the processing platform, you will need to complete and configure a few steps:

  1. [Create a Google Cloud Platform account](#account) (if you do not have one already)
  2. [Create a service account key for CloudConductor](#service-account-key)
  3. [Identify your resource quota](#resource-quota)
  4. [Create a reporting topic on Google Pub/Sub](#reporting-topic)
  5. [Generate a compute image](#compute-image)
  6. [Configure CloudConductor](#configure-cloudconductor)

### Account

If you already have a GCP account and you can access your cloud console, then you can skip this step entirely. 

Otherwise, please follow this [link](https://console.cloud.google.com/) to access your cloud console and to start an account.
Please ensure that you configure your billing account as it is a requirement to have access to the cloud services.

### Service account key

Now that you have access to the cloud, we should configure your account so that CloudConductor has access as well.
You will need to [create](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) a service account for CloudConductor.
Make sure you keep the generated private key only to yourself as anyone that has access to your private key will be able to 
access your resources.

### Resource quota

An important step when using CloudConductor is understanding your resource limits. CloudConductor is capable to run
thousands of instances and allocate petabytes of storage, but your GCP account might not be able to run at this scale yet (especially if you just created your account).
Also, as expected, the total processing cost will be higher when using many resources, but the results will come much faster.

Please follow and read the information in this [link](https://cloud.google.com/compute/quotas).

### Reporting topic

When CloudConductor is complete, it generates a final report that is transferred to the final output directory and 
a topic on [Google Pub/Sub](https://cloud.google.com/pubsub/docs/overview). Having all analysis run reports sent to a single Pub/Sub topic will
ensure that, at the end of the day, all run statistics are centralized into one single location.

Follow this [link](https://cloud.google.com/pubsub/docs/quickstart-console) to read the instructions on how to create your Pub/Sub topic.

### Compute image

All [instances](https://cloud.google.com/compute/docs/instances/) on Google Cloud require a [disk image](https://cloud.google.com/compute/docs/images).
Also, CloudConductor requires Docker for the initialization step of the tools. 

### Configure CloudConductor

Now that you finally have your Google Cloud account ready to run CloudConductor, you need to configure CloudConductor.

Here is a template of what needs to be completed in a CloudConductor platform configuration file for Google Cloud:

```ini
PLAT_MAX_NR_CPUS            = integer(min=1,max=300000)     # Maximum vCPUs count (for the entire GCP project)
PLAT_MAX_MEM                = integer(min=1,max=1000000)    # Maximum memory RAM in GB (for the entire GCP project)
PLAT_MAX_DISK_SPACE         = integer(min=1,max=2000000)    # Maximum disk space in GB (for the entire GCP project)
PROC_MAX_NR_CPUS            = integer(min=1,max=64)         # Maximum vCPUs count (for one single instance)
PROC_MAX_MEM                = integer(min=1,max=416)        # Maximum memory RAM in GB (for one single instance)
PROC_MAX_DISK_SPACE         = integer(min=1,max=64000)      # Maximum disk space in GB (for one single instance)

report_topic                = string            # Pub/Sub topic where final reports are sent 

service_account_key_file    = string            # Local path to CloudConductor service account private key 

zone                        = string            # The zone where all instances are created
randomize_zone              = boolean           # Specify if to randomize the zone 

[task_processor]
disk_image                  = string            # Disk image

is_preemptible              = boolean           # Specify if the running instances to be preemptible
max_reset                   = integer           # Maximum number of preemptions before total stop 

cmd_retries                 = integer           # Maximum number of command reruns 
```

An example of a platform configuration file is:

```ini
PLAT_MAX_NR_CPUS            = 150000
PLAT_MAX_MEM                = 500000
PLAT_MAX_DISK_SPACE         = 1000000
PROC_MAX_NR_CPUS            = 48
PROC_MAX_MEM                = 312
PROC_MAX_DISK_SPACE         = 64000

report_topic                = pipeline_reports

zone                        = us-central1-c
randomize_zone              = True

service_account_key_file    = /home/cloudconductor/.priv_key/CC.json

[task_processor]
disk_image                  = CC-image-latest

is_preemptible              = True
max_reset                   = 5

cmd_retries                 = 3
```
