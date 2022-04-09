import numpy as np
import gmsh
import sys
import os
from gera_malha_per_cfc import create_periodicity

def create_rve(P, domain, x_c, y_c, mesh_size_factor, path, model):
    if (model == "1"):
        R = (np.array(P)/np.pi)**0.5
    elif (model == "2"):
        R = (np.array(P)/(2*np.pi))**0.5
    xmin, xmax = domain[0], domain[1]
    ymin, ymax = domain[2], domain[3]
    Lref = ((xmax - xmin)**2 + (ymax - ymin)**2)**0.5
    tx, ty = xmax - xmin, ymax - ymin
    
    for i in range(len(P)):
        gmsh.initialize()
        
        gmsh.model.add("rve-0" + model + "-P" + str(i) + "-2D")
        
        dom = gmsh.model.occ.addRectangle(xmin, ymin, 0, tx, ty)
        
        if (R[i] !=0):
            for k in range(len(x_c)):
                circ = gmsh.model.occ.addCircle(x_c[k], y_c[k], 0, R[i], 10 + k)
                loop = gmsh.model.occ.addCurveLoop([circ], 10 + k)
                surf = gmsh.model.occ.addPlaneSurface([loop], 10 + k)
            rve = gmsh.model.occ.cut([(2, dom)], [(2, t) for t in range(10, 10 + k + 1)])[0][0]
            rve_dim, rve_tag = rve
        else:
            rve_tag = dom
        
        gmsh.model.occ.synchronize()
        
        p = gmsh.model.occ.getEntities(0)
        gmsh.model.mesh.setSize(p, mesh_size_factor * Lref)
        
        gmsh.model.occ.synchronize()
        
        gmsh.model.addPhysicalGroup(2, [rve_tag], 10)
        
        create_periodicity(0, domain)
        create_periodicity(1, domain)
        
        gmsh.model.mesh.generate()
        
        file_name = path + r'\rve-0' + model + '-P' + str(i) + '-2D.inp'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        gmsh.write(file_name)
        
        gmsh.finalize()
    return

P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
domain = [0, 1, 0, 1, 0, 0]
x_c = [0, 0, 1, 1, 0.5]
y_c = [0, 1, 0, 1, 0.5]
mesh_size_factor = 2e-2
path = r'.\models'

create_rve(P, domain, x_c, y_c, mesh_size_factor, path, model = '2')

P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
domain = [0, 1, 0, 1, 0, 0]
x_c = [0.5]
y_c = [0.5]
mesh_size_factor = 2e-2
path = r'.\models'

create_rve(P, domain, x_c, y_c, mesh_size_factor, path, model = '1')
