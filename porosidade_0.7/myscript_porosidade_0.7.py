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
s.CircleByCenterPerimeter(center=(0.5, 0.5), point1=(0.972, 0.5))
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
region = a.Set(edges=(e1[4:], ), name='Set-2')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for A vertice
v1 = a.instances['Part-1-1'].vertices
region = a.Set(vertices=(v1[1:2], ), name='Set-3')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for BC side
region = a.Set(edges=(e1[2:3], ), name='Set-4')
mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1', 
    region=region, u1=0.01, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating horizontal partition
e1 = p.edges
p.PartitionFaceByShortestPath(faces=f[0:], point1=p.InterestingPoint(
    edge=e1[4], rule=MIDDLE), point2=p.InterestingPoint(edge=e1[2], 
    rule=MIDDLE)) 

# Creating vertical partition
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
e1 = p.edges
p.PartitionFaceByShortestPath(faces=f[0:], point1=p.InterestingPoint(
    edge=e1[2], rule=MIDDLE), point2=p.InterestingPoint(edge=e1[8], rule=MIDDLE)) 

# Meshing
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
p.seedPart(size=0.01, deviationFactor=0.1, minSizeFactor=0.1)
p.setMeshControls(regions=f[0:], elemShape=TRI)
p.generateMesh()

# Creating job
mdb.Job(name='porosidade_7', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=1)

# Submit job
mdb.jobs['porosidade_7'].submit(consistencyChecking=OFF)
mdb.jobs['porosidade_7'].waitForCompletion()

# Operating on ODB data
path = './'
filename = 'porosidade_7.odb'

myodb = session.openOdb(name = path + filename)

nNodesSets = len(myodb.rootAssembly.nodeSets['SET-2'].nodes[0])
nodeList = []
for node in myodb.rootAssembly.nodeSets['SET-2'].nodes[0]:
    nodeList.append(int(node.label)-1)

RFx = 0
for index in nodeList:
    RFx += myodb.steps['Step-1'].frames[-1].fieldOutputs['RF'].values[index].data[0]

step_name = myodb.steps.items()[0][0] # get the step name

if (myodb.steps[step_name].frames[-1].fieldOutputs['E']): # get the strains
    E11, E22, E33, E12 = 0.0, 0.0, 0.0, 0.0
    for item in myodb.steps[step_name].frames[-1].fieldOutputs['E'].values:
        E11 += item.data[0]
        E22 += item.data[1]
        E33 += item.data[2]
        E12 += item.data[3]

if (myodb.steps[step_name].frames[-1].fieldOutputs['S']): # get the stress
    S11, S22, S33, S12 = 0.0, 0.0, 0.0, 0.0
    for item in myodb.steps[step_name].frames[-1].fieldOutputs['S'].values:
        S11 += item.data[0]
        S22 += item.data[1]
        S33 += item.data[2]
        S12 += item.data[3]

v = mdb.models['Model-1'].materials['aluminio'].elastic.table[0][1]

Ex = (S11-v*S22)/E11
Ey = (S22-v*S11)/E22
G  = S12/(2*E12)
#Dúvidas:
#   - E33 nulo no EPT?
#   - Ex, Ey iguais ao valor de E sem a porosidade;
#   - G = E/[2*(1+v)];
#   - S11 = RFx/A => E = S11/E11.

with open('strain_stress_07.txt', 'w') as file:
    file.write('ij |  E  |  S \n')
    file.write('(11; '+str(E11)+'; '+str(S11)+') \n')
    file.write('(22; '+str(E22)+'; '+str(S22)+') \n')
    file.write('(33; '+str(E33)+'; '+str(S33)+') \n')
    file.write('(12; '+str(E12)+'; '+str(S12)+') \n')
    file.write('RFx = '+str(RFx)+'\n')
    file.write('Ex  = '+str(Ex)+'\n')
    file.write('Ey  = '+str(Ey)+'\n')
    file.write('G   = '+str(G)+'\n')

# Save the model
mdb.saveAs(pathName='./estudo_porosidade_0.7.cae')