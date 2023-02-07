from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import json
from urllib.parse import unquote



app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def test():
    return 'Hello!'


@app.route('/code/ibm', methods=['GET'])
def get_ibm():
    url = request.headers.get('x-url')
    url = unquote(url)

    circuit=url.split('circuit=')[1]
    y = json.loads(circuit)
    code_array = []

    max_len = max([len(i) for i in y['cols']])

    code_array.append('from qiskit import execute, QuantumRegister, ClassicalRegister, QuantumCircuit, Aer')
    code_array.append('from numpy import pi')

    code_array.append('qreg_q = QuantumRegister('+str(max_len)+', \'q\')')
    code_array.append('creg_c = ClassicalRegister('+str(max_len)+', \'c\')')
    code_array.append('circuit = QuantumCircuit(qreg_q, creg_c)')

    for j in range(0, len(y['cols'])):
        #for x in y['cols'][j]:

        x=y['cols'][j]
        #cuenta cuántas puertas de cada tipo tenemos en una columna
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
            if 'X' in x and '•' in x:
                code_array.append('circuit.cx(qreg_q['+str(x.index("X"))+'], qreg_q['+str(x.index("•"))+'])')
            elif 'Z' in x and '•' in x:
                code_array.append('circuit.cx(qreg_q['+str(x.index("Z"))+'], qreg_q['+str(x.index("•"))+'])')

    code_array.append('backend = Aer.get_backend("qasm_simulator")')
    code_array.append('x=int(shots)')
    code_array.append('job = execute(circuit, backend, shots=x)')
    code_array.append('result = job.result()')
    code_array.append('counts = result.get_counts()')
    code_array.append('return counts')

    dict_response = {}
    dict_response['code'] = code_array
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
    code_array.append('gate_machines_arn= { "riggeti_aspen8":"arn:aws:braket:::device/qpu/rigetti/Aspen-8", "riggeti_aspen9":"arn:aws:braket:::device/qpu/rigetti/Aspen-9", "riggeti_aspen11":"arn:aws:braket:::device/qpu/rigetti/Aspen-11", "riggeti_aspen_m1":"arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-1", "DM1":"arn:aws:braket:::device/quantum-simulator/amazon/dm1","oqc_lucy":"arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy", "borealis":"arn:aws:braket:us-east-1::device/qpu/xanadu/Borealis", "ionq":"arn:aws:braket:::device/qpu/ionq/ionQdevice", "sv1":"arn:aws:braket:::device/quantum-simulator/amazon/sv1", "tn1":"arn:aws:braket:::device/quantum-simulator/amazon/tn1", "local":"local"}')
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
            if 'X' in x and '•' in x:
                code_array.append('circuit.cnot('+str(x.index("X"))+', '+str(x.index("•"))+')')
            elif 'Z' in x and '•' in x:
                code_array.append('circuit.cz('+str(x.index("Z"))+', '+str(x.index("•"))+')')

                
        
    
    code_array.append('return executeAWS(s3_folder, gate_machines_arn[machine], circuit, shots)')

    dict_response = {}
    dict_response['code'] = code_array
    return json.dumps(dict_response, indent = 4)

if __name__ == '__main__':
    app.run(host='localhost', port=8081)