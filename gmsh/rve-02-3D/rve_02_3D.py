from abaqus import *
from abaqusConstants import *
import numpy as np
import sys
from getState import getState

sys.path.insert(1, r'..\..\PBC_novtx_3D')

import periodic_bcs_3D

for i in range(8):
    inpf_name = '../models/rve-02-P' + str(i) + '-3D.inp'
    m_name = 'rve-02-P' + str(i) + '-3D'
    j_name = m_name
    out_name = 'strain-stress-P' + str(i) + '-3D'
    eps = 1e-5
    domain = [0, 1, 0, 1, 0, 1]
    P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    FILE_NAME = "rve-02-3D"
    
    xmin, xmax = domain[0], domain[1]
    ymin, ymax = domain[2], domain[3]
    zmin, zmax = domain[4], domain[5]
    
    mdb.ModelFromInputFile(name = m_name, inputFileName = inpf_name)
    
    m = mdb.models[m_name]
    p = m.parts['PART-1']
    a = m.rootAssembly
    
    a.Instance(name = 'PART-1-1', part = p, dependent = ON)
    
    elem = tuple((p.elements[i].label for i in range(len(p.elements))))
    elem_set = p.SetFromElementLabels(name = 'elem', elementLabels = elem)
    
    m.Material(name = 'aluminum')
    m.materials['aluminum'].Elastic(table = ((72000, 0.33), ))
    
    m.HomogeneousSolidSection(name='Section-1', material='aluminum', thickness=None)
    p.SectionAssignment(region = elem_set, sectionName = 'Section-1', offset = 0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    
    periodic_bcs_3D.pbc_tool(model_name = m_name, opt = '4. Sets + RFs + coefs + eq')
    
    m.StaticStep(name = 'Step-1', previous = 'Initial')
    m.FieldOutputRequest(name = 'F-Output-1', createStepName = 'Step-1', variables = ('S', 'E', 'U', 'EVOL'))
    
    RP1_strain = a.allSets['RP1_strain']
    RP2_shear = a.allSets['RP2_shear']
    
    m.DisplacementBC(name = 'BC-1', createStepName = 'Step-1', region = RP1_strain, u1 = 0.01, u2 = 0.0, u3 = 0.0, ur1 = UNSET, ur2 = UNSET, ur3 = UNSET, amplitude = UNSET, fixed = OFF, distributionType = UNIFORM, fieldName = '', localCsys = None)
    
    m.DisplacementBC(name = 'BC-2', createStepName = 'Step-1', region = RP2_shear, u1 = 0.01, u2 = UNSET, u3 = UNSET, ur1 = UNSET, ur2 = UNSET, ur3 = UNSET, amplitude = UNSET, fixed = OFF, distributionType = UNIFORM, fieldName = '', localCsys = None)
    
    mdb.Job(name=j_name, model=m_name, type=ANALYSIS,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE,  
	resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, numGPUs=1)
    
    mdb.jobs[j_name].submit()
    mdb.jobs[j_name].waitForCompletion()
    
    path = './'
    getState(path + j_name + '.odb', out_name, P[i], FILE_NAME)

mdb.saveAs('./' + FILE_NAME + '.cae')
