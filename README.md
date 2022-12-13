# openapi-generator-quantum

Added logic for processing new extension variables (x-quantumcode and x-provider) in:

modules\openapi-generator\src\main\java.org.opneapitools.codegen\languajes\AbstractPythonConnexionServerCodegen

The template of the new python-quantum language has been modified: 

modules\openapi-generator\src\main\resources\python-quantum\controller.mustache 

## Commands to perform the generation process

### By command line

python3 main.py
mvn clean package -DskipTests
java -jar modules\openapi-generator-cli\target\openapi-generator-cli.jar generate -i openapi_quantum.yaml -g python-quantum -o c:\temp\quantum

### By online mode
python3 main.py
cd modules\openapi-generator-online
java -jar ./target/openapi-generator-online.jar


