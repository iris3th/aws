#!/bin/bash
[ $# -ne 3  ] && { echo “usage: script requires 3 command line parameters, AWS_ACCESS_KEY_ID , AWS_SECRET_ACCESS_KEY , AWS_REGION space separated"; exit 1; }

export AWS_ACCESS_KEY_ID=$1
export AWS_SECRET_ACCESS_KEY=$2
export AWS_REGION=$3
for i in `aws s3 ls s3://deciphex-technical-assessment --recursive | awk '{print $4}'`;do echo $i ; aws s3api head-object --bucket deciphex-technical-assessment --key $i;done
