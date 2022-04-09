import numpy as np
import gmsh
import sys
import os

def create_periodicity(direction, domain, eps=1e-4):
    if (direction == 0):
        tx, ty, tz = domain[1] - domain[0], 0.0, 0.0
        smin = gmsh.model.getEntitiesInBoundingBox(domain[0]-eps, domain[2]-eps, domain[4]-eps, domain[0]+eps, domain[3]+eps, domain[5]+eps, 2)

    if (direction == 1):
        tx, ty, tz = 0.0, domain[3] - domain[2], 0.0
        smin = gmsh.model.getEntitiesInBoundingBox(domain[0]-eps, domain[2]-eps, domain[4]-eps, domain[1]+eps, domain[2]+eps, domain[5]+eps, 2)

    if (direction == 2):
        tx, ty, tz = 0.0, 0.0, domain[5] - domain[4]
        smin = gmsh.model.getEntitiesInBoundingBox(domain[0]-eps, domain[2]-eps, domain[4]-eps, domain[1]+eps, domain[3]+eps, domain[4]+eps, 2)

    translation = [1, 0, 0, tx, 0, 1, 0, ty, 0, 0, 1, tz, 0, 0, 0, 1]

    for i in smin:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(i[0], i[1])
        smax = gmsh.model.getEntitiesInBoundingBox(xmin-eps+tx, ymin-eps+ty, zmin-eps+tz, xmax+eps+tx, ymax+eps+ty, zmax+eps+tz, 2)

        for j in smax:
            xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = gmsh.model.getBoundingBox(j[0], j[1])
            xmin2 -= tx
            xmax2 -= tx
            ymin2 -= ty
            ymax2 -= ty
            zmin2 -= tz
            zmax2 -= tz
            # Apply the periodicity constraint between surfaces meshes
            if (abs(xmin2 - xmin) < eps and abs(xmax2 - xmax) < eps
                    and abs(ymin2 - ymin) < eps and abs(ymax2 - ymax) < eps
                    and abs(zmin2 - zmin) < eps and abs(zmax2 - zmax) < eps):
                gmsh.model.mesh.setPeriodic(2, [j[1]], [i[1]], translation)
    return

def create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model):
    if (model == "1"):
        R = (3*np.array(P)/8*np.pi)**0.5
    elif (model == "2"):
        R = (3*np.array(P)/(4*np.pi))**0.5
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
                sphr = gmsh.model.occ.addShpere(x_c[k], y_c[k], z_c[k], R[i], 10 + k)
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
        create_periodicity(3, domain)

        gmsh.model.mesh.generate()
        
        file_name = path + r'\rve-0' + model + '-P' + str(i) + '-2D.inp'
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
path = r'C:\Users\gabri\Documents\IC\integration\models'

create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model = '2')

P = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
domain = [0, 1, 0, 1, 0, 0]
x_c = [0]
y_c = [0]
mesh_size_factor = 2e-2
path = r'C:\Users\gabri\Documents\IC\integration\models'

create_rve(P, domain, x_c, y_c, z_c, mesh_size_factor, path, model = '1')
