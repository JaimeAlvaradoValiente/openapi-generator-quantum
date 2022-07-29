# openapi-generator-quantum

Added logic for processing new extension variables (x-quantumcode and x-provider) in:

modules\openapi-generator\src\main\java.org.opneapitools.codegen\languajes\AbstractPythonConnexionServerCodegen

The template of the new python-quantum language has been modified: 

modules\openapi-generator\src\main\resources\python-quantum\controller.mustache 

## Commands to perform the generation process:

mvn clean package -DskipTests

java -jar modules\openapi-generator-cli\target\openapi-generator-cli.jar generate -i openapi_quantum.yaml -g python-quantum -o c:\temp\quantum



