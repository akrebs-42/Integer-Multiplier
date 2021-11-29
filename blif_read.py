import copy

models = {}
currentModel = ''

class Gate:
    output = ''
    inputs = []
    func = ''
    str = ''
    def __init__(self, net_names):
        self.output = net_names[-1]
        self.inputs = net_names[:-1]
        self.str = 'output: ' + self.output + '\ninputs: ' + ' '.join(self.inputs)
    def replace_name(self, old_name, new_name):
        if(old_name in self.inputs):
            index = self.inputs.index(old_name)
            self.inputs[index] = new_name
            self.str = 'output: ' + self.output + '\ninputs: ' + ' '.join(self.inputs)
            self.str = self.str + '\nfunction: ' + self.func
        elif(old_name == self.output):
            self.output = new_name
            self.str = 'output: ' + self.output + '\ninputs: ' + ' '.join(self.inputs)
            self.str = self.str + '\nfunction: ' + self.func

    def set_function(self, function):
        self.func = function
        self.str = self.str + '\nfunction: ' + self.func
        #May need to adjust this in case there are multiple lines for it, but not necessary for current multiplier model
    def __str__(self):
        return self.str
    def __unicode__(self):
        return u(self.str)
    def __repr__(self):
        return self.str

def parse_line(line):
    global currentModel
    global models
    words = line.split()
    if(len(words) == 0):
        print('Empty line')
    elif(words[0] == '.model'):
        #print('Found a model named: ' + words[1])
        currentModel = words[1]
        models[currentModel] = {}
        models[currentModel]['Connections'] = []
        models[currentModel]['Subcircuits'] = []
        models[currentModel]['Nets'] = set()
        models[currentModel]['NullNets'] = set()
    elif(words[0] == '.inputs'):
        #print("Found inputs: ")
        #print(words[1:])
        models[currentModel]['inputs'] = words[1:]
        models[currentModel]['Nets'].update(words[1:])
    elif(words[0] == '.outputs'):
        #print('Found outputs: ')
        #print(words[1:])
        models[currentModel]['outputs'] = words[1:]
        models[currentModel]['Nets'].update(words[1:])
    elif(words[0] == '.names' and len(words) == 2):
        #print('Found a net with name: ' + words[1])
        #models[currentModel]['inputs'] = words[1:]
        models[currentModel]['Nets'].update(words[1])
        models[currentModel]['NullNets'].update(words[1])
    elif(words[0] == '.names' and len(words) > 2):
        #print('Found a gate with the following nets: ')
        #print(words[1:])
        models[currentModel]['Connections'].append(Gate(words[1:]))
        models[currentModel]['Nets'].update(words[1:])
    elif(words[0] == '.subckt'):
        #print('Found a subcircuit for model: ' + words[1])
        models[currentModel]['Subcircuits'].append(line)
    elif(words[0] == '.end'):
        #print('Found end of model')
        currentModel = ''
    elif(words[0].isnumeric()):
        models[currentModel]['Connections'][-1].set_function(line)


def replace_names_connections(models, model, sub, sub_pairs, index):
    connections = copy.deepcopy(models[sub]['Connections'])
    nets = models[sub]['Nets']
    old_names = []
    pairs = copy.deepcopy(sub_pairs)
    for sub_pair in sub_pairs:
        old_names.append(sub_pair.split('=')[0])
    for net in nets:
        if net not in old_names:
            pairs.append('' + net + '=' + net + '-' + str(index))
    for ind in range(len(connections)):
        for sub_pair in pairs:
            connections[ind].replace_name(sub_pair.split('=')[0], sub_pair.split('=')[1])
    nets = []
    for pair in pairs:
        nets.append(pair.split('=')[1])
    #Need to find a way to make all of the connections unique here though
    #Once that is done then the ADD8 subcircuit work should be done and the Multi4 work can be done
    #If all of that works then I should just need to write out the Singular file and I think the parser will be reasonable
    #I also need to make sure to get the RTTO order in the end, still working on that part
    models[model]['Connections'].extend(connections)
#    models[model]['Nets'].update(connections)

    #print('Added connections: ')
    #print(connections)

def replace_names_nets(models, model):
    connections = models[model]['Connections']
    nets = set()
    for connection in connections:
        nets.update(connection.inputs)
        nets.update(connection.output)
    models[model]['Nets'] = nets

def resolve_subcircuits(models):
    for model in models:
        if(len(models[model]['Subcircuits']) > 0):
            ind = 0
            finished = True
            for subcircuit in models[model]['Subcircuits']:
                sub = subcircuit.split()[1]
                if(len(models[sub]['Subcircuits']) > 0):
                    finished = False
                    break
                sub_pairs = subcircuit.split()[2:]
                replace_names_connections(models, model, sub, sub_pairs, ind)
                ind += 1
            if finished:
                replace_names_nets(models, model)
                models[model]['Subcircuits'] = []
    for model in models:
        if(len(models[model]['Subcircuits']) > 0):
            ind = 0
            finished = True
            for subcircuit in models[model]['Subcircuits']:
                sub = subcircuit.split()[1]
                sub_pairs = subcircuit.split()[2:]
                replace_names_connections(models, model, sub, sub_pairs, ind)
                ind += 1


#This returns a string for a new polynomial
def get_next_poly(gate):
    global poly_count
    poly = ''
    input_names = gate.inputs
    output_name = gate.output
    input_vals = gate.func.split()[0]
    output_val = gate.func.split()[-1]
    combine_input_vals = ''.join(input_vals)
    if(input_vals == '11' and output_val == '1'):
        poly = '' + output_name + ' - ' + input_names[0] + '*' + input_names[1]
    elif(input_vals == '1' and output_val == '1'):
        poly = '' + output_name + ' - ' + input_names[0]
    elif(input_vals == '00' and output_val == '1'):
        poly = '' + output_name + ' - 1 + '  + input_names[0] + ' + ' + input_names[1] + ' - ' + input_names[0] + '*' + input_names[1]
    elif(input_vals == '00' and output_val == '0'):
        poly = '' + output_name + ' - ' + input_names[0] + ' - ' + input_names[1] + ' + ' +  input_names[0] + '*' + input_names[1]
    return poly

#This J0 assumes the variables are binary
def get_J0(nets):
    J0 = ''
    for net in nets:
        J0 += '' + net + '^2 - ' + net
    return J0

def write_singular(model):
    J0 = get_J0(model['Nets'])
    poly_count = 0
    ind = 0
    for gate in model['Connections']:
        next_poly = get_next_poly(gate)
        #print(next_poly)
        #Write out something like
        #f.write('f' + str(ind) + ' = ' + next_poly)
        #ind += 1
    #Also use the 'NullNets' value to write out that some polynomials are just 0
    for net in model['NullNets']:
        next_poly = net
        #f.write('f' + str(ind) + ' = ' + next_poly)
        #ind += 1

with open("mult4full.blif", 'r') as f:
  lines = f.readlines()
  for line in lines:
    parse_line(line)
#print(models)

#Now that parsing is done, the subcircuts need to be resolved
resolve_subcircuits(models)
print('Finishing')
print(models['Multi4'])
#Find RTTO ordering
#order_circuit()

#write Singular file for this circuit using RTTO and J0
write_singular(models['Multi4'])
