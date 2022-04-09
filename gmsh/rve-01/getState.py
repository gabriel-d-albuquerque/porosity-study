import sys
from odbAccess import *

if 'abaqusConstants' not in sys.modules:
    from abaqusConstants import *

def getState(file, out_name, P):
    myodb = openOdb(file)
    
    step_name = myodb.steps.items()[0][0] # get the step name
    
    evol = []
    total_v = 0
    for item in myodb.steps[step_name].frames[-1].fieldOutputs['EVOL'].values:
        evol.append(item.data)
        total_v += item.data
    
    if (myodb.steps[step_name].frames[-1].fieldOutputs['E']): # get the strains
        E11, E22, E33, E12 = 0.0, 0.0, 0.0, 0.0
        k = 0
        for item in myodb.steps[step_name].frames[-1].fieldOutputs['E'].values:
            E11 += evol[k]*item.data[0]
            E22 += evol[k]*item.data[1]
            E33 += evol[k]*item.data[2]
            E12 += evol[k]*item.data[3]
            k += 1
    
    if (myodb.steps[step_name].frames[-1].fieldOutputs['S']): # get the stress
        S11, S22, S33, S12 = 0.0, 0.0, 0.0, 0.0
        k = 0
        for item in myodb.steps[step_name].frames[-1].fieldOutputs['S'].values:
            S11 += evol[k]*item.data[0]
            S22 += evol[k]*item.data[1]
            S33 += evol[k]*item.data[2]
            S12 += evol[k]*item.data[3]
    	    k += 1
    
    with open(out_name + '.txt', 'w') as fl:
        fl.write('E11='+str(E11)+'\n')
        fl.write('E22='+str(E22)+'\n')
        fl.write('E33='+str(E33)+'\n')
        fl.write('E12='+str(E12)+'\n')
        fl.write('S11='+str(S11)+'\n')
        fl.write('S22='+str(S22)+'\n')
        fl.write('S33='+str(S33)+'\n')
        fl.write('S12='+str(S12)+'\n')
        fl.write('P='+str(P))
