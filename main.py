from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
import os
import docker
import json
from urllib.parse import unquote
import socket
import yaml
import requests

import random, string
import re

global ports

#SETUP APIs
app = Flask(__name__)

def get_parameters(qasmString):
    # Definir el patrón regex para buscar el tipo y el nombre de la variable
    pattern = r"input (\w+)\[\d+\] (\w+)"

    # Realizar la búsqueda utilizando el patrón regex
    coincidences = re.findall(pattern, qasmString)

    if coincidences:
        return [[coincidence[0], coincidence[1]] for coincidence in coincidences]
    else:
        return None, None

@app.route('/hello', methods=['GET'])
def test():
    return 'Hello!'

@app.route('/docker', methods=['POST'])
def createContainer():
    client = docker.from_env()
    running_container = client.containers.list()
    port=getFreePort()
    yaml = request.form.get('yaml')
    name = request.form.get('name')
    #aws_access_key_id= request.form.get('aws_access_key')
    #aws_secret_access_key= request.form.get('aws_secret')
    #with open('./.aws/credentials', 'w') as f:
    #    f.write('[default]\n')
    #    f.write('aws_access_key_id='+aws_access_key_id+'\n')
    #    f.write('aws_secret_access_key='+aws_secret_access_key)
    if name in [container.name for container in running_container]:
        name=name+str(port)
    cmd='java -jar openapi-generator-cli.jar generate -i '+yaml+' -g python-quantum -o ./openapi_server >NUL'
    #https://raw.githubusercontent.com/JaimeAlvaradoValiente/openapi-generator-quantum/main/openapi_quantum.yaml -g python-quantum -o ../openapi_server >NUL"')
    os.system(cmd)
    client.images.build(path='./', tag=name)
    c=client.containers.create(image=name, ports={8080: port}, name=name)
    c.start()
    path='http://quantumservicesdeployment.spilab.es:'+str(port)+'/ui'
    response_data = {
        "path": path,
        "container_name": name
    }
    #return "<html><h1><a href='" + path + "'>" + path + "</a></h1><h1>Container name: " + name + "</h1></html>"
    return response_data


@app.route('/update_circuit', methods=['POST'])
def update_circuit_url():
    port=getFreePort()
    data = request.data.decode('utf-8')
    data_dict = json.loads(data)

    circuit_name = data_dict.get('circuit_name')
    new_url=None
    new_circuit_string=None
    if 'new_url' in data_dict:
        new_url = data_dict.get('new_url')
    else :
        new_circuit_string = data_dict.get('new_circuit_string')
    yaml_url = data_dict.get('yaml_data')
    name= data_dict.get('name')
    docker_hub_repo = data_dict.get('docker_hub_repo')


    try:
        response = requests.get(yaml_url)
        yaml_data = response.text

        # Parsear el YAML
        yaml_dict = yaml.safe_load(yaml_data)

        # Buscar el circuito con el nombre proporcionado
        if 'paths' in yaml_dict and f'/circuit/{circuit_name}' in yaml_dict['paths']:

            #circuit = yaml_dict['paths'][f'/circuit/{circuit_name}']
            if new_url is not None:
                if 'get' in yaml_dict['paths'][f'/circuit/{circuit_name}']:
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['get']['x-quantumCode'] = new_url
                elif 'post' in yaml_dict['paths'][f'/circuit/{circuit_name}']:
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['post']['x-quantumCode'] = new_url
            else:
                if 'get' in yaml_dict['paths'][f'/circuit/{circuit_name}']:
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['get']['x-quantumCode']=None
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['get']['x-quantumCodeQASM']="\""+new_circuit_string+"\""


                if 'post' in yaml_dict['paths'][f'/circuit/{circuit_name}']:
                    parameters=get_parameters(new_circuit_string)
                    lines=new_circuit_string.split('\n')

                    # Iterar sobre cada item en la lista
                    new_circuit_str=""
                    for item in lines:
                        new_circuit_str=new_circuit_str+item
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['post']['x-quantumCode']=None
                    yaml_dict['paths'][f'/circuit/{circuit_name}']['post']['x-quantumCodeQASM']="\""+new_circuit_str+"\""
                    string_random = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
                    if len(parameters) != 0:
                        new_dict={'content' : {'application/json':{'schema':{'$ref':{}}}}}
                        new_dict['content']['application/json']['schema']['$ref']='#/components/schemas/'+string_random
                        yaml_dict['paths'][f'/circuit/{circuit_name}']['post']['requestBody']=new_dict
                        new_schema={'properties': {}}
                        for parameter in parameters:
                            new_schema['properties'][parameter[1]]={}
                            new_schema['properties'][parameter[1]]['example']=0
                            new_schema['properties'][parameter[1]]['format']=parameter[0]
                            new_schema['properties'][parameter[1]]['type']='number'
                            yaml_dict['components']['schemas'][string_random]=new_schema

            #yaml_dict['paths'][f'/circuit/{circuit_name}']['x-quantumCode'] = new_url
            stream = 'document.yaml'
            with open(stream, 'w') as f:
                yaml.dump(yaml_dict, f)
            print('Circuit URL successfully updated in YAML')


            cmd='java -jar openapi-generator-cli.jar generate -i ./'+stream+' -g python-quantum -o ./openapi_server >NUL'
            #https://raw.githubusercontent.com/JaimeAlvaradoValiente/openapi-generator-quantum/main/openapi_quantum.yaml -g python-quantum -o ../openapi_server >NUL"')
            os.system(cmd)

            client = docker.from_env()
            running_container = client.containers.list()

            # Eliminar la imagen Docker existente con el mismo nombre
            for container in running_container:
                if container.name == name:
                    container.stop()
                    container.remove()

            # Construir la nueva imagen Docker
            client.images.build(path='./', tag=name)

            #Subir a dockerhub
            tagged_image = client.images.get(name)
            tagged_image.tag(docker_hub_repo, tag='latest')
            client.images.push(docker_hub_repo, tag='latest')

            #Crear el contenedor
            c=client.containers.create(image=name, ports={8080: port}, name=name)
            c.start()
            path='http://quantumservicesdeployment.spilab.es:'+str(port)+'/ui'
            response_data = {
                "path": path,
                "container_name": name
            }
            #return "<html><h1><a href='" + path + "'>" + path + "</a></h1><h1>Container name: " + name + "</h1></html>"
            return response_data
        else:
            return jsonify({'error': f'A circuit with the name {circuit_name} was not found in the provided YAML.'}), 404

    except Exception as e:
        return jsonify({'error': f'Error al cargar o procesar el YAML: {str(e)}'}), 500




@app.route('/code/ibm', methods=['GET'])
def get_ibm():
    url = request.headers.get('x-url')
    url = unquote(url)


    circuit=url.split('circuit=')[1]
    y = json.loads(circuit)
    print(y)
    code_array = []

    max_len = max([len(i) for i in y['cols']])

    code_array.append('from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile')
    code_array.append('from numpy import pi')
    code_array.append('from qiskit.providers.basic_provider import BasicProvider')
    code_array.append('from qiskit_ibm_provider import IBMProvider')
    code_array.append('import qiskit.qasm3')

    code_array.append('qreg_q = QuantumRegister('+str(max_len)+', \'q\')')
    code_array.append('creg_c = ClassicalRegister('+str(max_len)+', \'c\')')
    code_array.append('circuit = QuantumCircuit(qreg_q, creg_c)')
    code_array.append('gate_machines_arn= {"local":"local", "ibm_brisbane":"ibm_brisbane", "ibm_osaka":"ibm_osaka", "ibm_kyoto":"ibm_kyoto", "simulator_stabilizer":"simulator_stabilizer", "simulator_mps":"simulator_mps", "simulator_extended_stabilizer":"simulator_extended_stabilizer", "simulator_statevector":"simulator_statevector"}')

    for j in range(0, len(y['cols'])):
        #for x in y['cols'][j]:

        x=y['cols'][j]
        #cuenta cuantas puertas de cada tipo tenemos en una columna
        g = [[x.count(z), z] for z in set(x)]

        l=len(g)

        if l==1 or (l==2 and ((g[0][1]=='H' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='H') or (g[0][1]=='Z' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='Z') or (g[0][1]=='X' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='X'))):
            if x[0] == 'Swap' and x[1] == 'Swap':
                code_array.append('circuit.swap(qreg_q[0], qreg_q[1])')
            elif x[0] == 'Measure':
                for k in range(0, len(x)):
                    code_array.append('circuit.measure(qreg_q['+str(k)+'], creg_c['+str(k)+'])')
            else:
                for i in range(0, len(x)):
                    if x[i] == 'H':
                        code_array.append('circuit.h(qreg_q['+str(i)+'])')
                    elif x[i] == 'Z':
                        code_array.append('circuit.z(qreg_q['+str(i)+'])')
                    elif x[i] == 'X':
                        code_array.append('circuit.x(qreg_q['+str(i)+'])')
        elif l==2 or l==3:
            if 'X' in x and '\x95' in x:
                code_array.append('circuit.cx(qreg_q['+str(x.index("X"))+'], qreg_q['+str(x.index("\x95"))+'])')
            elif 'Z' in x and '\x95' in x:
                code_array.append('circuit.cx(qreg_q['+str(x.index("Z"))+'], qreg_q['+str(x.index("\x95"))+'])')
    code_array.append('if machine == "local":')
    code_array.append('    backend = BasicProvider().get_backend("basic_simulator")')
    code_array.append('    x=int(shots)')
    code_array.append('    transpiled_circuit = transpile(circuit, backend)')
    code_array.append('    job = backend.run(transpiled_circuit, shots=x)')
    code_array.append('    result = job.result()')
    code_array.append('    counts = result.get_counts()')
    code_array.append('    return counts')
    code_array.append('else:')
    code_array.append('    provider = IBMProvider()')
    code_array.append('    backend = provider.get_backend(gate_machines_arn[machine])')
    code_array.append('    x=int(shots)')
    code_array.append('    transpiled_circuit = transpile(circuit, backend)')
    code_array.append('    job = backend.run(transpiled_circuit, backend, shots=x)')
    code_array.append('    result = job.result()')
    code_array.append('    counts = result.get_counts()')
    code_array.append('    return counts')

    dict_response = {}
    dict_response['code'] = code_array
    print(dict_response)
    return json.dumps(dict_response, indent = 4)

@app.route('/code/aws', methods=['GET'])
def get_aws():
    url = request.headers.get('x-url')
    url = unquote(url)


    circuit=url.split('circuit=')[1]
    y = json.loads(circuit)
    code_array = []

    code_array.append('from braket.circuits import Gate')
    code_array.append('from braket.circuits import Circuit')
    code_array.append('from braket.devices import LocalSimulator')
    code_array.append('from braket.aws import AwsDevice')
    code_array.append('gate_machines_arn= {"riggeti_aspen_m3":"arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3", "DM1":"arn:aws:braket:::device/quantum-simulator/amazon/dm1", "oqc_lucy":"arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy", "ionq_aria1":"arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1", "ionq_aria2":"arn:aws:braket:us-east-1::device/qpu/ionq/Aria-2", "ionq_forte":"arn:aws:braket:us-east-1::device/qpu/ionq/Forte", "ionq_harmony":"arn:aws:braket:us-east-1::device/qpu/ionq/Harmony", "sv1":"arn:aws:braket:::device/quantum-simulator/amazon/sv1", "tn1":"arn:aws:braket:::device/quantum-simulator/amazon/tn1", "local":"local"}')
    code_array.append('s3_folder = ("amazon-braket-7c2f2fa45286", "api")')

    code_array.append('circuit = Circuit()')

    for j in range(0, len(y['cols'])):

        x=y['cols'][j]

        g = [[x.count(z), z] for z in set(x)]

        l=len(g)

        if l==1 or (l==2 and ((g[0][1]=='H' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='H') or (g[0][1]=='Z' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='Z') or (g[0][1]=='X' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='X'))):
            if x[0] == 'Swap' and x[1] == 'Swap':
                code_array.append('circuit.swap(0,1)')
            else:
                for i in range(0, len(x)):
                    if x[i] == 'H':
                        code_array.append('circuit.h('+str(i)+')')
                    elif x[i] == 'Z':
                        code_array.append('circuit.z('+str(i)+')')
                    elif x[i] == 'X':
                        code_array.append('circuit.x('+str(i)+')')
        elif l==2 or l==3:
            if 'X' in x and '\x95' in x:
                code_array.append('circuit.cnot('+str(x.index("X"))+', '+str(x.index("\x95"))+')')
            elif 'Z' in x and '\x95' in x:
                code_array.append('circuit.cz('+str(x.index("Z"))+', '+str(x.index("\x95"))+')')




    code_array.append('return executeAWS(s3_folder, gate_machines_arn[machine], circuit, shots)')

    dict_response = {}
    dict_response['code'] = code_array
    print(dict_response)

    return json.dumps(dict_response, indent = 4)


@app.route('/code/variosIbm', methods=['POST'])
def variosIbm():

    circuitos = []
    for i in request.json.keys():
        circuitos.append(ast.literal_eval(unquote(request.json[i]).split('circuit=')[1]))


    desplazamiento = []
    for y in circuitos:
        print(y)
        desplazamiento.append(max([len(i) for i in y['cols']]))

    code_array = []

    code_array.append('from qiskit import execute, QuantumRegister, ClassicalRegister, QuantumCircuit, Aer')
    code_array.append('from numpy import pi')

    code_array.append('qreg_q = QuantumRegister('+str(sum(desplazamiento))+', \'q\')')
    code_array.append('creg_c = ClassicalRegister('+str(sum(desplazamiento))+', \'c\')')
    code_array.append('circuit = QuantumCircuit(qreg_q, creg_c)')

    for index, circuito in enumerate(circuitos):
        despl=0
        if index != 0:
            for i in range(0,index):
                despl=despl+desplazamiento[i]
        for j in range(0, len(circuito['cols'])):
            #for x in circuito['cols'][j]:

            x=circuito['cols'][j]
            #cuenta cuantas puertas de cada tipo tenemos en una columna
            g = [[x.count(z), z] for z in set(x)]

            l=len(g)

            if l==1 or (l==2 and ((g[0][1]=='H' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='H') or (g[0][1]=='Z' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='Z') or (g[0][1]=='X' and g[1][1]==1) or (g[0][1]==1 and g[1][1]=='X'))):
                if x[0] == 'Swap' and x[1] == 'Swap':
                    code_array.append('circuit.swap(qreg_q[0], qreg_q[1])')
                elif x[0] == 'Measure':
                    for k in range(0, len(x)):
                        code_array.append('circuit.measure(qreg_q['+str(k+despl)+'], creg_c['+str(k+despl)+'])')
                else:
                    for i in range(0, len(x)):
                        if x[i] == 'H':
                            code_array.append('circuit.h(qreg_q['+str(i+despl)+'])')
                        elif x[i] == 'Z':
                            code_array.append('circuit.z(qreg_q['+str(i+despl)+'])')
                        elif x[i] == 'X':
                            code_array.append('circuit.x(qreg_q['+str(i+despl)+'])')
            elif l==2 or l==3:
                if 'X' in x and '\x95' in x:
                    code_array.append('circuit.cx(qreg_q['+str(x.index("X")+despl)+'], qreg_q['+str(x.index("\x95")+despl)+'])')
                elif 'Z' in x and '\x95' in x:
                    code_array.append('circuit.cx(qreg_q['+str(x.index("Z")+despl)+'], qreg_q['+str(x.index("\x95")+despl)+'])')

    code_array.append('return circuit')

    dict_response = {}
    dict_response['code'] = code_array
    return json.dumps(dict_response, indent = 4)


def updatePorts():
    for i in range(8082, 8182):
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = ("0.0.0.0", i)
        result_of_check = a_socket.connect_ex(location)

        if result_of_check == 0:
            ports[i]=1
        else:
            ports[i]=0

        a_socket.close()

def getFreePort():
    puertos=[k for k, v in ports.items() if v == 0]
    ports[puertos[0]]=1
    return puertos[0]




if __name__ == '__main__':
   ports={}
   updatePorts()
   print('hecho')
   app.run(host='0.0.0.0', port=8080, debug=False)

