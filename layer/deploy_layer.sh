#!/bin/sh
set -ex

BUCKET_PREFIX=$1
LAYER_NAME_SUFFIX=$2

REGIONS=( "ap-northeast-1" "ap-northeast-2" "ap-south-1" "ap-southeast-1" "ap-southeast-2" "ca-central-1" "eu-central-1" "eu-north-1" "eu-west-1" "eu-west-2" "eu-west-3" "sa-east-1" "us-east-1" "us-east-2" "us-west-1" "us-west-2" )
LAYER_NAME_BASE="catchpoint-lambda-python-layer"
LAYER_NAME="$LAYER_NAME_BASE"

if [[ ! -z "$LAYER_NAME_SUFFIX" ]]; then
  LAYER_NAME="$LAYER_NAME_BASE-$LAYER_NAME_SUFFIX"
fi

SCRIPT_PATH=${0%/*}
STATEMENT_ID_BASE="$LAYER_NAME_BASE-$(($(date +%s)))"

echo "Creating layer zip for: '$LAYER_NAME'"
rm -rf $SCRIPT_PATH/python
pip3 install catchpoint -t python
export VERSION=$(python3.6 ../setup.py --version)
if [ ! -f $SCRIPT_PATH/python/catchpoint/handler.py ]; then
    echo "Wrapper handler not found in the pip version of catchpoint, adding manually..."
    cp $SCRIPT_PATH/../catchpoint/handler.py $SCRIPT_PATH/python/catchpoint/
fi
zip -r "$LAYER_NAME.zip" $SCRIPT_PATH/python/  --exclude=*.DS_Store* --exclude=*.sh --exclude=*.git* --exclude=README.md --exclude=*.dist-info/* --exclude=*__pycache__/*

echo "Zip completed."

 for REGION in "${REGIONS[@]}"
 do
    ARTIFACT_BUCKET=$BUCKET_PREFIX-$REGION
    ARTIFACT_OBJECT=layers/python/catchpoint-agent-lambda-layer-$VERSION.zip

    echo "Uploading '$LAYER_NAME.zip' at $ARTIFACT_BUCKET with key $ARTIFACT_OBJECT"
    
    aws s3 cp "$SCRIPT_PATH/$LAYER_NAME.zip"  "s3://$ARTIFACT_BUCKET/$ARTIFACT_OBJECT"

    echo "Uploaded '$LAYER_NAME' to $ARTIFACT_BUCKET"
 done

 rm -rf "$SCRIPT_PATH/$LAYER_NAME.zip"
