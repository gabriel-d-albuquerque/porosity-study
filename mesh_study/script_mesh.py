from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import os
import numpy as np

# Assign porosity of study
P = 0.7
# Calculates the radius of the circular porus
R = np.sqrt(P/np.pi)
# Mesh sizes of study
SIZE = [0.001, 0.0025, 0.005, 0.01, 0.02, 0.03]
# Model name
MODEL_NAME = ['mesh_study_01', 'mesh_study_025', 'mesh_study_05', 'mesh_study_1', 'mesh_study_2', 'mesh_study_3']
# Part name
PART_NAME = ['part_01', 'part_025', 'part_05', 'part_1', 'part_2', 'part_3']
# Job name
JOB_NAME = ['mesh_01', 'mesh_025', 'mesh_05', 'mesh_1', 'mesh_2', 'mesh_3']
# Output file name
FILE_NAME = ['mesh_01', 'mesh_025', 'mesh_05', 'mesh_1', 'mesh_2', 'mesh_3']

for i in range(6):
	# Creating model
	mdb.Model(MODEL_NAME[i])
	
	# Creating part
	s = mdb.models[MODEL_NAME[i]].ConstrainedSketch(name='__profile__', sheetSize=200.0)
	g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
	s.setPrimaryObject(option=STANDALONE)
	s.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))
	s.CircleByCenterPerimeter(center=(0.5, 0.5), point1=(0.5 + R, 0.5))
	p = mdb.models[MODEL_NAME[i]].Part(name=PART_NAME[i], dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
	p = mdb.models[MODEL_NAME[i]].parts[PART_NAME[i]]
	p.BaseShell(sketch=s)
	s.unsetPrimaryObject()
	del mdb.models[MODEL_NAME[i]].sketches['__profile__']
	
	# Creating material
	mdb.models[MODEL_NAME[i]].Material(name='aluminum')
	mdb.models[MODEL_NAME[i]].materials['aluminum'].Elastic(table=((72000.0, 0.33), ))
	
	# Creating section
	mdb.models[MODEL_NAME[i]].HomogeneousSolidSection(name='Section-1', material='aluminum', thickness=None)
	
	# Assigning section
	f = p.faces
	region = p.Set(faces=(f[0:], ), name='Set-1')
	p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
	    offsetType=MIDDLE_SURFACE, offsetField='', 
	    thicknessAssignment=FROM_SECTION) 
	
	# Creating assembly
	a = mdb.models[MODEL_NAME[i]].rootAssembly
	a.DatumCsysByDefault(CARTESIAN)
	a.Instance(name='Part-1-1', part=p, dependent=ON)
	
	# Creating step
	mdb.models[MODEL_NAME[i]].StaticStep(name='Step-1', previous='Initial')
	mdb.models[MODEL_NAME[i]].fieldOutputRequests['F-Output-1'].setValues(variables=(
	    'S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 
	    'EVOL'))
	
	# Creating BC for side AD
	e1 = a.instances['Part-1-1'].edges
	region = a.Set(edges=(e1[4:], ), name='Set-2')
	mdb.models[MODEL_NAME[i]].DisplacementBC(name='BC-1', createStepName='Step-1', 
	    region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
	    distributionType=UNIFORM, fieldName='', localCsys=None)
	
	# Creating BC for A vertice
	v1 = a.instances['Part-1-1'].vertices
	region = a.Set(vertices=(v1[1:2], ), name='Set-3')
	mdb.models[MODEL_NAME[i]].DisplacementBC(name='BC-2', createStepName='Step-1', 
	    region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
	    distributionType=UNIFORM, fieldName='', localCsys=None)
	
	# Creating BC for BC side
	region = a.Set(edges=(e1[2:3], ), name='Set-4')
	mdb.models[MODEL_NAME[i]].DisplacementBC(name='BC-3', createStepName='Step-1', 
	    region=region, u1=0.01, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
	    distributionType=UNIFORM, fieldName='', localCsys=None)
	
	# Creating horizontal partition
	e1 = p.edges
	p.PartitionFaceByShortestPath(faces=f[0:], point1=p.InterestingPoint(
	    edge=e1[4], rule=MIDDLE), point2=p.InterestingPoint(edge=e1[2], 
	    rule=MIDDLE)) 
	
	# Creating vertical partition
	p = mdb.models[MODEL_NAME[i]].parts[PART_NAME[i]]
	f = p.faces
	e1 = p.edges
	p.PartitionFaceByShortestPath(faces=f[0:], point1=p.InterestingPoint(
    edge=e1[2], rule=MIDDLE), point2=p.InterestingPoint(edge=e1[8], rule=MIDDLE)) 

	# Meshing
	p = mdb.models[MODEL_NAME[i]].parts[PART_NAME[i]]
	f = p.faces
	p.seedPart(size=SIZE[i], deviationFactor=0.1, minSizeFactor=0.1)
	p.setMeshControls(regions=f[0:], elemShape=TRI)
	p.generateMesh()
	
	# Creating job
	mdb.Job(name=JOB_NAME[i], model=MODEL_NAME[i], description='', type=ANALYSIS, 
	    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
	    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
	    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
	    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
	    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
	    numGPUs=1)
	
	# Submit job
	mdb.jobs[JOB_NAME[i]].submit(consistencyChecking=OFF)
	mdb.jobs[JOB_NAME[i]].waitForCompletion()
	
	# Operating on ODB data
	path = './'
	filename = JOB_NAME[i] + '.odb'
	
	myodb = session.openOdb(name = path + filename)
	
	region = p.Set(edges=(e1[4:5], ), name='Set-5')
	index = region.nodes[0].label-1
	
	step_name = myodb.steps.items()[0][0] # get the step name
	
	S11 = myodb.steps[step_name].frames[-1].fieldOutputs['S'].values[index].data[0]
	S22 = myodb.steps[step_name].frames[-1].fieldOutputs['S'].values[index].data[1]
	S33 = myodb.steps[step_name].frames[-1].fieldOutputs['S'].values[index].data[2]
	S12 = myodb.steps[step_name].frames[-1].fieldOutputs['S'].values[index].data[3]
	
	with open(FILE_NAME[i] + '.txt', 'w') as file:
	    file.write('S11='+str(S11)+'\n')
	    file.write('S22='+str(S22)+'\n')
	    file.write('S33='+str(S33)+'\n')
	    file.write('S12='+str(S12)+'\n')
	    file.write('m_s='+str(SIZE[i]))
	
	
# Save the model
mdb.saveAs(pathName='./mesh_study.cae')
