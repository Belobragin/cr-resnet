# conteinerized Resnet50 neural net for adversarial images analysis

## Overview
1. This repository provides Python code to build and run docker container for image classification of adversarial images comparing to the adversarial source (initial images). This is a part of integral `werewolf - aker - cr-resnet project`. 
Please refer to `aker` project for more explanations on adversarial images.
2. The main goal of this project was to provide stable source of image classification to measure image attack quality quantification, for the most popular adversarial attack algorythms.
3. This project is for fun and personal use only and it is not a commercial product.
4. This project is served as a local and an aws cloud options. Details are below.
5. Code is served "as-is", with absolutely no gurantees or support, on the best effort basis. I will try to answer the questions, but can not promise that.
  
## Resnet50 neural net
The foundation article on introduction of a `Deep Residual Learning for Image Recognition` (Resnet) is provided in the `./ref` folder
    
## License and terms of use
This repo is covered by the standard `BSD 3-Clause "New" or "Revised" License`. 
Citing demands use of a next citation:
```
Vladimir Belobragin
e-mail:   vblvbl133@gmail.com
linkedin: https://www.linkedin.com/in/belovl%D0%B0d/?isSelfProfile=true
```

## Security
This projects container is NOT intended for public exposure. Run it locally behind the firewall and other security devices OR/AND, if run in the aws cloud, use a private subnet. The recommended aws cloud IAC decision is included.
Author bears no responsibility for this product use consequences. Play with the code on your own risk.

## More verbose product description
(TODO)