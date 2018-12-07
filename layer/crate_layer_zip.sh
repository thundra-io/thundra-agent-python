#!/bin/sh
VERSION=$1
REGIONS=( "ap-northeast-1" "ap-northeast-2" "ap-south-1" "ap-southeast-1" "ap-southeast-2" "ca-central-1" "eu-central-1" "eu-west-1" "eu-west-2" "eu-west-3" "sa-east-1" "us-east-1" "us-east-2" "us-west-1" "us-west-2" )
LAYER_NAME_BASE="thundra-lambda-python-layer"
LAYER_NAME_SUFFIX=$2
LAYER_NAME="$LAYER_NAME_BASE$LAYER_NAME_SUFFIX"

STATEMENT_ID_BASE="$LAYER_NAME_BASE-$(($(date +%s)))"

echo "Createing layer zip for: '$LAYER_NAME'"
pip3 install thundra -t ./python
if [ ! -f python/thundra/handler.py ]; then
    echo "Wrapper handler not found in the pip version of thundra, adding manually..."
    cp handler.py python/thundra/
fi
zip -r "$LAYER_NAME.zip" python/  --exclude=*.DS_Store* --exclude=*.sh --exclude=*.git* --exclude=README.md --exclude=*.dist-info/*

echo "Zip completed."

# for REGION in "${REGIONS[@]}"
# do
#     ARTIFACT_BUCKET=thundra-dist-$REGION
#     ARTIFACT_OBJECT=layers/python/thundra-agent-lambda-layer-$VERSION.zip

#     echo "Uploading '$LAYER_NAME.zip' at $ARTIFACT_BUCKET with key $ARTIFACT_OBJECT" 
    
#     aws s3 cp "./$LAYER_NAME.zip"  "s3://$ARTIFACT_BUCKET/$ARTIFACT_OBJECT"

#     echo "Uploaded '$LAYER_NAME' to $ARTIFACT_BUCKET"

# done

# rm -rf "./$LAYER_NAME.zip"