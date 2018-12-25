#!/bin/sh
VERSION=$1
BUCKET_PREFIX=$2
REGIONS=( "eu-west-2" "us-west-2" )
LAYER_NAME_BASE="thundra-lambda-python-layer"
LAYER_NAME_SUFFIX=$2
LAYER_NAME="$LAYER_NAME_BASE$LAYER_NAME_SUFFIX"
SCRIPT_PATH=${0%/*}
STATEMENT_ID_BASE="$LAYER_NAME_BASE-$(($(date +%s)))"

echo "Creating layer zip for: '$LAYER_NAME'"
rm -rf $SCRIPT_PATH/python
pip3 install thundra -t python
if [ ! -f $SCRIPT_PATH/python/thundra/handler.py ]; then
    echo "Wrapper handler not found in the pip version of thundra, adding manually..."
    cp $SCRIPT_PATH/../thundra/handler.py $SCRIPT_PATH/python/thundra/
fi
zip -r "$LAYER_NAME.zip" $SCRIPT_PATH/python/  --exclude=*.DS_Store* --exclude=*.sh --exclude=*.git* --exclude=README.md --exclude=*.dist-info/* --exclude=*__pycache__/*

echo "Zip completed."

 for REGION in "${REGIONS[@]}"
 do
    ARTIFACT_BUCKET=$BUCKET_PREFIX-$REGION
    ARTIFACT_OBJECT=layers/python/thundra-agent-lambda-layer-$VERSION.zip

    echo "Uploading '$LAYER_NAME.zip' at $ARTIFACT_BUCKET with key $ARTIFACT_OBJECT"
    
    aws s3 cp "$SCRIPT_PATH/$LAYER_NAME.zip"  "s3://$ARTIFACT_BUCKET/$ARTIFACT_OBJECT"

    echo "Uploaded '$LAYER_NAME' to $ARTIFACT_BUCKET"
 done

 rm -rf "$SCRIPT_PATH/$LAYER_NAME.zip"