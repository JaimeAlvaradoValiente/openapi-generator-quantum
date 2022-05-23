# openapi-generator-quantum

Añadida lógica para procesar la nueva variable extension (x-quantumcode) en:
modules\openapi-generator\src\main\java.org.opneapitools.codegen\languajes\AbstractPythonConnexionServerCodegen

Modificada la plantilla template en: 
modules\openapi-generator\src\main\resources\python-quantum\controller.mustache 

## Comandos para lanzar 

mvn clean package -DskipTests

java -jar modules\openapi-generator-cli\target\openapi-generator-cli.jar generate -i C:\Users\jalva\Downloads\OpenAPI\openapi.yaml -g python-quantum -o c:\temp\quantum

