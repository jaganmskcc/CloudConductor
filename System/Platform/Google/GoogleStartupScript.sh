#!/usr/bin/env bash

# Signal that instance is fully initialized
ZONE=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | cut -d "/" -f 4)
gcloud --quiet compute instances add-metadata $(hostname) --metadata READY=TRUE --zone ${ZONE}