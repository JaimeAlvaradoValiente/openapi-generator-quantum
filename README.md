# openapi-generator-quantum

## Overview

This generator is based on the OpenAPI Specification. We have extended the OpenAPI Specification with an extension that allows developers to define quantum APIs that encapsulate quantum circuits as a service or select a provider for executing these circuits.

## Extensions

This generator contains two extensions, x-quantumCode and x-quantumProvider:

- x-quantumCode extension use is to reference a URL with a RAW format file that should contain the quantum code of the circuit or the URL of the Quirk circuit.

- x-quantumProvider extension use is to indicate the provider where the circuit will be executed (AWS or IBM).

Two parameters have been included, machine and shots:

- The machine parameter with which at runtime you can define the quantum machine on which you want to run the circuit, within the provider, you have specified. 

- The shots parameter indicates the number of times you want to run the circuit.

There is an example at [https://raw.githubusercontent.com/openapi-generator-quantum/main/openapi_quantum.yaml](https://raw.githubusercontent.com/JaimeAlvaradoValiente/openapi-generator-quantum/main/openapi_quantum.yaml)

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


