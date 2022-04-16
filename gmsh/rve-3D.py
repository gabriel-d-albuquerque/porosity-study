import numpy as np
import gmsh
import sys
import os
from gera_malha_per_cfc import create_periodicity

def create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model):
    if (model == "1"):
        R = ((3*np.array(P))/(4*np.pi))**(1/3)
    elif (model == "2"):
        R = ((3*np.array(P))/(8*np.pi))**(1/3)
    xmin, xmax = domain[0], domain[1]
    ymin, ymax = domain[2], domain[3]
    zmin, zmax = domain[4], domain[5]
    Lref = ((xmax - xmin)**2 + (ymax - ymin)**2 + (zmax - zmin)**2)**0.5
    tx, ty, tz = xmax - xmin, ymax - ymin, zmax - zmin
    
    for i in range(len(P)):
        gmsh.initialize()
        
        gmsh.model.add("rve-0" + model + "-P" + str(i) + "-3D")
        
        dom = gmsh.model.occ.addBox(xmin, ymin, zmin, tx, ty, tz)
        
        if (R[i] !=0):
            for k in range(len(x_c)):
                sphr = gmsh.model.occ.addSphere(x_c[k], y_c[k], z_c[k], R[i], 10 + k)
            rve = gmsh.model.occ.cut([(3, dom)], [(3, t) for t in range(10, 10 + k + 1)])[0][0]
            rve_dim, rve_tag = rve
        else:
            rve_tag = dom
        
        gmsh.model.occ.synchronize()
        
        p = gmsh.model.occ.getEntities(0)
        gmsh.model.mesh.setSize(p, mesh_size_factor * Lref)
        
        gmsh.model.occ.synchronize()
        
        gmsh.model.addPhysicalGroup(3, [rve_tag], 10)
        
        create_periodicity(0, domain)
        create_periodicity(1, domain)
        create_periodicity(2, domain)

        gmsh.model.mesh.generate()
        
        file_name = path + r'\rve-0' + model + '-P' + str(i) + '-3D.inp'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        gmsh.write(file_name)
        
        gmsh.finalize()
    return

P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
domain = [0, 1, 0, 1, 0, 1]
x_c = [0, 1, 0, 1, 0, 0, 1, 1, 0.5]
y_c = [0, 0, 1, 1, 0, 1, 1, 0, 0.5]
z_c = [0, 0, 0, 1, 1, 1, 0, 1, 0.5]
mesh_size_factor = 2e-2
path = r'.\models'

create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model = '2')

P = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
domain = [0, 1, 0, 1, 0, 1]
x_c = [0.5]
y_c = [0.5]
z_c = [0.5]
mesh_size_factor = 2e-2
path = r'.\models'

create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model = '1')
