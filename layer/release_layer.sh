#!/bin/sh
set -ex
export VERSION=$(python3.6 ../setup.py --version)
BUCKET_PREFIX=$1
LAYER_NAME_SUFFIX=$2
REGIONS=( "ap-northeast-1" "ap-northeast-2" "ap-south-1" "ap-southeast-1" "ap-southeast-2" "ca-central-1" "eu-central-1" "eu-north-1" "eu-west-1" "eu-west-2" "eu-west-3" "sa-east-1" "us-east-1" "us-east-2" "us-west-1" "us-west-2" )
LAYER_NAME_BASE="catchpoint-lambda-python-layer"
LAYER_NAME="$LAYER_NAME_BASE"

if [[ ! -z "$LAYER_NAME_SUFFIX" ]]; then
  LAYER_NAME="$LAYER_NAME_BASE-$LAYER_NAME_SUFFIX"
fi

STATEMENT_ID_BASE="$LAYER_NAME_BASE-$(($(date +%s)))"

for REGION in "${REGIONS[@]}"
do
    echo "Releasing '$LAYER_NAME' layer for region $REGION ..."

    ARTIFACT_BUCKET=$BUCKET_PREFIX-$REGION
    ARTIFACT_OBJECT=layers/python/catchpoint-agent-lambda-layer-$VERSION.zip

    echo "Publishing '$LAYER_NAME' layer from artifact $ARTIFACT_OBJECT" \
         " at bucket $ARTIFACT_BUCKET ..."

    PUBLISHED_LAYER_VERSION=$(aws lambda publish-layer-version \
        --layer-name $LAYER_NAME \
        --content S3Bucket=$ARTIFACT_BUCKET,S3Key=$ARTIFACT_OBJECT \
        --compatible-runtimes python2.7 python3.6 python3.7 python3.8 python3.9 \
        --region $REGION \
        --query 'Version')

    echo $PUBLISHED_LAYER_VERSION

    echo "Published '$LAYER_NAME' layer with version $PUBLISHED_LAYER_VERSION"

    # #################################################################################################################

    echo "Adding layer permission for '$LAYER_NAME' layer with version $PUBLISHED_LAYER_VERSION" \
         " to make it accessible by everyone ..."

    STATEMENT_ID="$STATEMENT_ID_BASE-$REGION"
    aws lambda add-layer-version-permission \
        --layer-name $LAYER_NAME \
        --version-number $PUBLISHED_LAYER_VERSION \
        --statement-id "$LAYER_NAME-$STATEMENT_ID" \
        --action lambda:GetLayerVersion \
        --principal '*' \
        --region $REGION \

    echo "Added layer permission for '$LAYER_NAME' layer"

done
