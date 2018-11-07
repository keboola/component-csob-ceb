#!/bin/bash

#push test image to ECR
if ! [ -z "$BASE_KBC_CONFIG" ]&&! [ -z "$KBC_STORAGE_TOKEN" ]
then
	echo "Preparing KBC test image"
	docker pull quay.io/keboola/developer-portal-cli-v2:latest
	export REPOSITORY=`docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD -e KBC_DEVELOPERPORTAL_URL quay.io/keboola/developer-portal-cli-v2:latest ecr:get-repository $KBC_DEVELOPERPORTAL_VENDOR $KBC_DEVELOPERPORTAL_APP`
	docker tag $APP_IMAGE:latest $REPOSITORY:test
	eval $(docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD -e KBC_DEVELOPERPORTAL_URL quay.io/keboola/developer-portal-cli-v2:latest ecr:get-login $KBC_DEVELOPERPORTAL_VENDOR $KBC_DEVELOPERPORTAL_APP)
	docker push $REPOSITORY:test
	docker pull quay.io/keboola/syrup-cli:latest
	
	docker run --rm -e KBC_STORAGE_TOKEN quay.io/keboola/syrup-cli:latest run-job $KBC_DEVELOPERPORTAL_APP $BASE_KBC_CONFIG test

	if [ -s kbc_configs.txt ]
		then
			echo "Runing legacy config tests.."
			while read conf; do
	  			echo "docker run --rm -e KBC_STORAGE_TOKEN quay.io/keboola/syrup-cli:latest run-job $KBC_DEVELOPERPORTAL_APP $conf test"
			done <kbc_configs.txt
		else
			echo ""
			echo "No base config or kbc storage token provided, skipping KBC test run.."
	  fi
else
	echo "No live KBC tests configured! Consider adding one!"
fi