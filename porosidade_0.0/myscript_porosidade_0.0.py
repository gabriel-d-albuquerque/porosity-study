from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import os
import numpy as np

# Creating part
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE) #duvida
s.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Creating material
mdb.models['Model-1'].Material(name='aluminio')
mdb.models['Model-1'].materials['aluminio'].Elastic(table=((72000.0, 0.33), ))

# Creating section
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', material='aluminio', thickness=None)

# Assigning section
f = p.faces
region = p.Set(faces=(f[0:], ), name='Set-1')
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION) 

# Creating assembly
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
a.Instance(name='Part-1-1', part=p, dependent=ON)

# Creating step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 
    'EVOL'))

# Creating BC for side AD
e1 = a.instances['Part-1-1'].edges
region = a.Set(edges=(e1[3:], ), name='Set-2')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for A vertice
v1 = a.instances['Part-1-1'].vertices
region = a.Set(vertices=(v1[0:1], ), name='Set-3')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for BC side
region = a.Set(edges=(e1[1:2], ), name='Set-4')
mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1', 
    region=region, u1=0.01, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Meshing
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
p.seedPart(size=0.01, deviationFactor=0.1, minSizeFactor=0.1)
p.setMeshControls(regions=f[0:], elemShape=TRI)
p.generateMesh()

# Creating job
mdb.Job(name='porosidade_0', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=1)

# Submit job
mdb.jobs['porosidade_0'].submit(consistencyChecking=OFF)
mdb.jobs['porosidade_0'].waitForCompletion()

# Operating on ODB data
path = './'
filename = 'porosidade_0.odb'

myodb = session.openOdb(name = path + filename)

nNodesSets = len(myodb.rootAssembly.nodeSets['SET-2'].nodes[0])
nodeList = []
for node in myodb.rootAssembly.nodeSets['SET-2'].nodes[0]:
    nodeList.append(int(node.label)-1)

RFx = 0
for index in nodeList:
    RFx += myodb.steps['Step-1'].frames[-1].fieldOutputs['RF'].values[index].data[0]

step_name = myodb.steps.items()[0][0] # get the step name

evol = []
total_v = 0
for item in myodb.steps[step_name].frames[-1].fieldOutputs['EVOL'].values:
    evol.append(item.data)
    total_v += item.data

if (myodb.steps[step_name].frames[-1].fieldOutputs['E']): # get the strains
    E11, E22, E33, E12 = 0.0, 0.0, 0.0, 0.0
    i = 0
    for item in myodb.steps[step_name].frames[-1].fieldOutputs['E'].values:
        E11 += evol[i]*item.data[0]
        E22 += evol[i]*item.data[1]
        E33 += evol[i]*item.data[2]
        E12 += evol[i]*item.data[3]
        i += 1
    E11 = E11/total_v
    E22 = E22/total_v
    E33 = E33/total_v
    E12 = E12/total_v

if (myodb.steps[step_name].frames[-1].fieldOutputs['S']): # get the stress
    S11, S22, S33, S12 = 0.0, 0.0, 0.0, 0.0
    i = 0
    for item in myodb.steps[step_name].frames[-1].fieldOutputs['S'].values:
        S11 += evol[i]*item.data[0]
        S22 += evol[i]*item.data[1]
        S33 += evol[i]*item.data[2]
        S12 += evol[i]*item.data[3]
    S11 = S11/total_v
    S22 = S22/total_v
    S33 = S33/total_v
    S12 = S12/total_v

with open('strain_stress_0.txt', 'w') as file:
    file.write('E11='+str(E11)+'\n')
    file.write('E22='+str(E22)+'\n')
    file.write('E33='+str(E33)+'\n')
    file.write('E12='+str(E12)+'\n')
    file.write('S11='+str(S11)+'\n')
    file.write('S22='+str(S22)+'\n')
    file.write('S33='+str(S33)+'\n')
    file.write('S12='+str(S12)+'\n')
    file.write('RFx='+str(RFx))

# Save the model
mdb.saveAs(pathName='./estudo_porosidade_0.0.cae')