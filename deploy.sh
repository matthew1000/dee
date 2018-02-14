# A helper script to deploy the module to Lambda. It assumes the function has already been made.
zip -r /tmp/dee_deploy.zip phrases data *.py
aws lambda update-function-code --function-name dee --zip-file fileb:///tmp/dee_deploy.zip  --publish  $@
