# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-18.54.59 126836
# Run by Gabriel Delgado on Sat Oct 09 14:42:56 2021
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import os

# Creating part
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))
s.CircleByCenterPerimeter(center=(0.5, 0.5), point1=(0.809, 0.5))
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
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getSequenceFromMask(mask=('[#1 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
region = p.Set(faces=faces, name='Set-1')
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# Creating assembly
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)

# Creating step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')

# Creating BC for side AD
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#10 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
region = a.Set(edges=edges1, name='Set-2')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for A vertice
a = mdb.models['Model-1'].rootAssembly
v1 = a.instances['Part-1-1'].vertices
verts1 = v1.getSequenceFromMask(mask=('[#2 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
region = a.Set(vertices=verts1, name='Set-3')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating BC for BC side
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#4 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
region = a.Set(edges=edges1, name='Set-4')
mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1', 
    region=region, u1=0.01, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)

# Creating horizontal partition
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#1 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
v1, e1, d2 = p.vertices, p.edges, p.datums # (dúvida) poderia excluir?
p.PartitionFaceByShortestPath(faces=pickedFaces, point1=p.InterestingPoint(
    edge=e1[4], rule=MIDDLE), point2=p.InterestingPoint(edge=e1[2], 
    rule=MIDDLE)) # (dúvida) função InterestingPoint e seu argumento

# Creating vertical partition
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#3 ]', ), ) # (dúvida) função getSequenceFromMask e seu argumento
v2, e, d = p.vertices, p.edges, p.datums # (dúvida) poderia excluir?
p.PartitionFaceByShortestPath(faces=pickedFaces, point1=p.InterestingPoint(
    edge=e[2], rule=MIDDLE), point2=p.InterestingPoint(edge=e[8], rule=MIDDLE)) # (dúvida) função InterestingPoint e seu argumento

# Meshing
p.seedPart(size=0.02, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# Creating job
mdb.Job(name='porosidade_3', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
    numGPUs=1)

# Save the model
mdb.saveAs(pathName='./estudo_porosidade_0.3.cae')

# Submit job
mdb.jobs['porosidade_3'].submit(consistencyChecking=OFF)
#: The job input file "porosidade_1.inp" has been submitted for analysis.
#: Job Job-1: Analysis Input File Processor completed successfully.
#: Job Job-1: Abaqus/Standard completed successfully.
#: Job Job-1 completed successfully. 

o3 = session.openOdb(
    name='C:/Users/Gabriel Delgado/OneDrive/Universidade/IC/HelloAbaqus/tarefa2/porosidade_0.3/porosidade_3.odb')
#: Model: C:/Users/Gabriel Delgado/OneDrive/Universidade/IC/HelloAbaqus/tarefa2/porosidade_0.3/porosidade_3.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       4
#: Number of Node Sets:          6
#: Number of Steps:              1
mdb.save()

# (dúvida) Erro a partir deste ponto

# # Operating on XY data
# openMdb(
#     pathName='C:/Users/Gabriel Delgado/OneDrive/Universidade/IC/HelloAbaqus/tarefa2/porosidade_0.7/estudo_porosidade_0.7.cae')
# p = mdb.models['Model-1'].parts['Part-1']
# a = mdb.models['Model-1'].rootAssembly
# odb = session.odbs['C:/Users/Gabriel Delgado/OneDrive/Universidade/IC/HelloAbaqus/tarefa2/porosidade_0.7/porosidade_7.odb']
# session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('RF', 
#     NODAL, ((COMPONENT, 'RF1'), )), ), nodeSets=('SET-2', ))
# xy1 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 9']
# xy2 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 10']
# xy3 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 12']
# xy4 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 205']
# xy5 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 206']
# xy6 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 207']
# xy7 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 208']
# xy8 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 209']
# xy9 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 210']
# xy10 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 211']
# xy11 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 212']
# xy12 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 213']
# xy13 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 214']
# xy14 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 215']
# xy15 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 216']
# xy16 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 217']
# xy17 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 218']
# xy18 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 219']
# xy19 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 220']
# xy20 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 221']
# xy21 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 222']
# xy22 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 223']
# xy23 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 224']
# xy24 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 225']
# xy25 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 226']
# xy26 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 227']
# xy27 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 228']
# xy28 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 301']
# xy29 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 302']
# xy30 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 303']
# xy31 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 304']
# xy32 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 305']
# xy33 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 306']
# xy34 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 307']
# xy35 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 308']
# xy36 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 309']
# xy37 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 310']
# xy38 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 311']
# xy39 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 312']
# xy40 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 313']
# xy41 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 314']
# xy42 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 315']
# xy43 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 316']
# xy44 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 317']
# xy45 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 318']
# xy46 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 319']
# xy47 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 320']
# xy48 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 321']
# xy49 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 322']
# xy50 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 323']
# xy51 = session.xyDataObjects['RF:RF1 PI: PART-1-1 N: 324']
# xy52 = sum((xy1, xy2, xy3, xy4, xy5, xy6, xy7, xy8, xy9, xy10, xy11, xy12, 
#     xy13, xy14, xy15, xy16, xy17, xy18, xy19, xy20, xy21, xy22, xy23, xy24, 
#     xy25, xy26, xy27, xy28, xy29, xy30, xy31, xy32, xy33, xy34, xy35, xy36, 
#     xy37, xy38, xy39, xy40, xy41, xy42, xy43, xy44, xy45, xy46, xy47, xy48, 
#     xy49, xy50, xy51))
# xy52.setValues(
#     sourceDescription='sum ( ( "RF:RF1 PI: PART-1-1 N: 9", "RF:RF1 PI: PART-1-1 N: 10", "RF:RF1 PI: PART-1-1 N: 12", "RF:RF1 PI: PART-1-1 N: 205", "RF:RF1 PI: PART-1-1 N: 206", "RF:RF1 PI: PART-1-1 N: 207", "RF:RF1 PI: PART-1-1 N: 208", "RF:RF1 PI: PART-1-1 N: 209", "RF:RF1 PI: PART-1-1 N: 210", "RF:RF1 PI: PART-1-1 N: 211", "RF:RF1 PI: PART-1-1 N: 212", "RF:RF1 PI: PART-1-1 N: 213", "RF:RF1 PI: PART-1-1 N: 214", "RF:RF1 PI: PART-1-1 N: 215", "RF:RF1 PI: PART-1-1 N: 216", "RF:RF1 PI: PART-1-1 N: 217", "RF:RF1 PI: PART-1-1 N: 218", "RF:RF1 PI: PART-1-1 N: 219", "RF:RF1 PI: PART-1-1 N: 220", "RF:RF1 PI: PART-1-1 N: 221", "RF:RF1 PI: PART-1-1 N: 222", "RF:RF1 PI: PART-1-1 N: 223", "RF:RF1 PI: PART-1-1 N: 224", "RF:RF1 PI: PART-1-1 N: 225", "RF:RF1 PI: PART-1-1 N: 226", "RF:RF1 PI: PART-1-1 N: 227", "RF:RF1 PI: PART-1-1 N: 228", "RF:RF1 PI: PART-1-1 N: 301", "RF:RF1 PI: PART-1-1 N: 302", "RF:RF1 PI: PART-1-1 N: 303", "RF:RF1 PI: PART-1-1 N: 304", "RF:RF1 PI: PART-1-1 N: 305", "RF:RF1 PI: PART-1-1 N: 306", "RF:RF1 PI: PART-1-1 N: 307", "RF:RF1 PI: PART-1-1 N: 308", "RF:RF1 PI: PART-1-1 N: 309", "RF:RF1 PI: PART-1-1 N: 310", "RF:RF1 PI: PART-1-1 N: 311", "RF:RF1 PI: PART-1-1 N: 312", "RF:RF1 PI: PART-1-1 N: 313", "RF:RF1 PI: PART-1-1 N: 314", "RF:RF1 PI: PART-1-1 N: 315", "RF:RF1 PI: PART-1-1 N: 316", "RF:RF1 PI: PART-1-1 N: 317", "RF:RF1 PI: PART-1-1 N: 318", "RF:RF1 PI: PART-1-1 N: 319", "RF:RF1 PI: PART-1-1 N: 320", "RF:RF1 PI: PART-1-1 N: 321", "RF:RF1 PI: PART-1-1 N: 322", "RF:RF1 PI: PART-1-1 N: 323", "RF:RF1 PI: PART-1-1 N: 324" ) )')
# tmpName = xy52.name
# session.xyDataObjects.changeKey(tmpName, 'rftotal_7')

# # Generating report file
# x0 = session.xyDataObjects['rftotal_7']
# session.writeXYReport(fileName='rftotal_0.7.txt', xyData=(x0, )) #(dúvida) xyData só tem x0?
# mdb.save()