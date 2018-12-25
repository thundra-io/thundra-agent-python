#!/bin/sh

VERSION=$1
BUCKET_PREFIX=$2
REGIONS=( "eu-west-2" "us-west-2" )
LAYER_NAME_BASE="thundra-lambda-python-layer"
LAYER_NAME_SUFFIX=$2
LAYER_NAME="$LAYER_NAME_BASE$LAYER_NAME_SUFFIX"

STATEMENT_ID_BASE="$LAYER_NAME_BASE-$(($(date +%s)))"

for REGION in "${REGIONS[@]}"
do
    echo "Releasing '$LAYER_NAME' layer for region $REGION ..."

    ARTIFACT_BUCKET=$BUCKET_PREFIX-$REGION
    ARTIFACT_OBJECT=layers/python/thundra-agent-lambda-layer-$VERSION.zip

    echo "Publishing '$LAYER_NAME' layer from artifact $ARTIFACT_OBJECT" \
         " at bucket $ARTIFACT_BUCKET ..."

    PUBLISHED_LAYER_VERSION=$(aws lambda publish-layer-version \
        --layer-name $LAYER_NAME \
        --content S3Bucket=$ARTIFACT_BUCKET,S3Key=$ARTIFACT_OBJECT \
        --compatible-runtimes "python3.6" \
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