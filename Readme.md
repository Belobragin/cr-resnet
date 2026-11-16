# containerized Resnet50 neural net for adversarial images analysis
Refer to [aker](https://github.com/Belobragin/paker) project for more explanations on adversarial images.

## Overview
1. This repository provides Python code to build and run docker container for image classification. This is a part of integral `werewolf - aker - cr-resnet project`. 
2. This project is for fun and personal use only and it is not a commercial product.
3. Code is served "as-is", with absolutely no gurantees or support, on the best effort basis. I will try to answer the questions, but can not promise that
4. this code was prepared with the assistance of Claude Sonnet 5.5
  
## Resnet50 neural net
The foundation article on introduction of a `Deep Residual Learning for Image Recognition` (Resnet) is provided in the `./ref` folder
    
## License and terms of use
This repo is covered by the standard [BSD 3-Clause "New" or "Revised" License](https://github.com/Belobragin/cr-resnet/blob/main/LICENSE)  
For citing use the next information::
```
Vladimir Belobragin
e-mail:   vblvbl133@gmail.com
linkedin: https://www.linkedin.com/in/belovl%D0%B0d/
```

## Security
This projects container is NOT intended for public exposure. Run it locally behind the firewall and other security devices OR/AND, if run in the aws cloud, restrict access to lambda. Use attached templates to build resource stack. No responsibility for this product. Play with the code on your own risk.

## More verbose product description
- put your environment variables to .env.example and save it as .env
- clone the repo and build the container. Run it locally with docker-composer or push it to aws ecr and build aws cloudformation stack to run in the cloud. Follow Makefile.example commands.
- this application is stateless

## Input request format
1. serever responds on `/api/v1/predict` endpoint. For local run 3 folders are mounted, defined by environment variables^
    - `IMAGE_LOCAL_STORAGE` as "image"
    - `ADVERSARIAL_LOCAL_STORAGE` as "adversarial"
    - `FILTER_LOCAL_STORAGE` as "filter"
   
2. example of local api:
```
@curl -X POST "http://localhost:${RESNET_SERVER_PORT}/api/v1/predict?image_name=hog-test.jpg&folder=image"
```

example of the aws cloud api (your exported aws credentials must have adequate permissions):
```
source .env
export UNIQUE_LAMBDA_AWS_ADDRESS=$(aws cloudformation describe-stacks \
		--stack-name $AWS_RESOURCE_CFN_STACK_NAME \
		--query "Stacks[0].Outputs[?OutputKey =='LambdaFunctionUrl'].OutputValue" \
		--output text)
python3 iac/awscloud/script/sigv4_post.py \
		"$UNIQUE_LAMBDA_AWS_ADDRESS/api/v1/predict?image_name=hog.jpg&folder=image"

```
3. example of the output:
```
{"image": "hog.jpg", "folder": "image", "predictions": {"n0": ["n02396427", "wild_boar", "342", "96.27"], "n1": ["n02395406", "hog", "341", "3.61"], "n2": ["n02397096", "warthog", "343", "0.1"]}}
```
