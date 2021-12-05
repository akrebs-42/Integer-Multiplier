import sys

#These variables are global for parsing
models = {}
currentModel = ''
var_ind = 0

#This Gate class is a holder used to show the relationship between nets
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

#Parse through each line, using .blif keywords and saving net names
def parse_line(line):
    global currentModel
    global models
    global var_ind
    words = line.split()
    if(len(words) == 0):
        print('Empty line')
    elif(words[0] == '.model'):
        #Set up the data structures for this model
        currentModel = words[1]
        models[currentModel] = {}
        models[currentModel]['Connections'] = []
        models[currentModel]['Nets'] = {}
    elif(words[0] == '.inputs'):
        #Set the inputs and set their weight to 0
        models[currentModel]['inputs'] = words[1:]
        for word in words[1:]:
            models[currentModel]['Nets'][word] = 0
    elif(words[0] == '.outputs'):
        #Set the outputs
        models[currentModel]['outputs'] = words[1:]
    elif(words[0] == '.names' and len(words) > 2):
        #Create the connection gate here
        models[currentModel]['Connections'].append(Gate(words[1:]))
        #Set the weight of the output to be one higher than the max of its inputs
        vals = []
        for word in words[1:-1]:
            vals.append(models[currentModel]['Nets'][word])
        max_value = max(vals)
        models[currentModel]['Nets'][words[-1]] = max_value + 1
    elif(words[0].isnumeric()):
        #Set the function for the previous gate
        #Note: Testing so far on a mult4 has never had a gate with more than one function line
        models[currentModel]['Connections'][-1].set_function(line)
    elif(words[0] == '.end'):
        print('Found end of model')



#This returns a string for a new polynomial
def get_next_poly(gate):
    poly = ''
    input_names = gate.inputs
    output_name = gate.output
    input_vals = gate.func.split()[0]
    output_val = gate.func.split()[-1]
    combine_input_vals = ''.join(input_vals)
    #AND gate
    if(input_vals == '11' and output_val == '1'):
        poly = '' + output_name + ' - ' + input_names[0] + '*' + input_names[1]
    #Buffer
    elif(input_vals == '1' and output_val == '1'):
        poly = '' + output_name + ' - ' + input_names[0]
    #NOR gate
    elif(input_vals == '00' and output_val == '1'):
        poly = '' + output_name + ' - 1 + '  + input_names[0] + ' + ' + input_names[1] + ' - ' + input_names[0] + '*' + input_names[1]
    #OR gate
    elif(input_vals == '00' and output_val == '0'):
        poly = '' + output_name + ' - ' + input_names[0] + ' - ' + input_names[1] + ' + ' +  input_names[0] + '*' + input_names[1]

    #Make sure to remove all invalid characters from the names
    poly = poly.replace('|', '_').replace('(', '_').replace(')', '_')
    return poly

#Returns the RTTO order string value for the model
def get_RTTO_order_string(model):
    all_values = model['Nets'].values()
    max_value = max(all_values)
    #Set all of the outputs to be the max values
    #There may not be a specific need for this since
    #all outputs should be higher than their inputs
    for output in model['outputs']:
        model['Nets'][output] = max_value
    ring = 'ring r = 2, ('

    terms = [k for k, v in sorted(model['Nets'].items(), reverse=True, key=lambda item: item[1])]

    middle = terms[0]
    for term in terms[1:]:
        middle += ', ' + term
    #Make sure to remove all invalid characters from the names (has to be done on the middle alone)
    middle = middle.replace('|', '_').replace('(', '_').replace(')', '_')

    ring += middle
    ring += '), lp;\n'
    return ring

#Returns the vanishing polynomial
def get_vanishing_poly(var_name):
    return '' + var_name + '^2 - ' + var_name

#Writes the Singular file
def write_singular(model, write_file):
    ind = 0
    with open(write_file, 'w') as f:
        #Write the RTTO ordering
        f.write('//Define the ring\n\n')
        ring = get_RTTO_order_string(model)
        f.write(ring)

        #Write the gate polynomials
        f.write('\n//Define the gate polys\n\n')
        for gate in model['Connections']:
            next_poly = get_next_poly(gate)
            f.write('poly f' + str(ind) + ' = ' + next_poly + ';\n')
            ind += 1
        J_str = 'ideal J = f0'
        for i in range(1,ind):
            J_str += ', f' + str(i)
        f.write(J_str + ';\n')

        #Write the vanishing polynomials of the inputs
        f.write('\n//Define the input vanishing polys\n\n')
        vanish_start_ind = ind
        for input in model['inputs']:
            vanishing_poly = get_vanishing_poly(input)
            f.write('poly f' + str(ind) + ' = ' + vanishing_poly + ';\n')
            ind += 1
        J0_str = 'ideal J0 = f' + str(vanish_start_ind)
        for i in range(vanish_start_ind, ind):
            J0_str += ', f' + str(i)
        f.write(J0_str + ';\n')

        #Write the combination ideal of the circuit and vanishing polynomials
        f.write('\n//Computer groebner basis G from J and J0\n\n')
        f.write('ideal G = J + J0;\n')

#This is the main set_function
#Check that a file was given to write to
if(len(sys.argv) < 2):
    print('Error, needs the filename to parse')
    exit(1)
read_file = sys.argv[1]

#Desginate the write file, if none is provided call it write.sing
write_file = ''
if(len(sys.argv) < 3):
    write_file = 'write.sing'
else:
    write_file = sys.argv[2]

#Read from the input file
with open(read_file, 'r') as f:
  lines = f.readlines()
  for line in lines:
    parse_line(line)

#write Singular file for this circuit using RTTO and J0
#This code makes an assumption that the last model is
#the one that should be written
write_singular(models[currentModel], write_file)
