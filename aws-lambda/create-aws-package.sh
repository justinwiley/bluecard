#!/bin/bash
# installs required node libraries, creates zip file for Amazon lambda

npm install
zip -r aws-lambda.zip *