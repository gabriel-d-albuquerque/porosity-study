# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
import gmsh
#import meshio
#import trimesh

def create_RVE_particles(domain, particles, eps=1e-3 , mesh_size_factor=0.05, element_order=1):
    xmin, xmax = domain[0], domain[1]
    ymin, ymax = domain[2], domain[3]
    zmin, zmax = domain[4], domain[5]

    Lref = ((xmax - xmin)**2.0 + (ymax - ymin)**2.0 + (zmax - zmin)**2.0)**0.5

    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin

    domain_id = 10
    first_particle_id = 20
    nparticles = len(particles)

    gmsh.initialize()
    gmsh.model.occ.addBox(xmin, ymin, zmin, dx, dy, dz, domain_id)

    #gmsh.model.addPhysicalGroup(3, [domain_id], 1000)
    #gmsh.model.setPhysicalName(3, domain_id + 1, 'matrix')


    for k, particle in enumerate(particles):
        center = particle[0:3]
        radius = particle[3]
        gmsh.model.occ.addSphere(center[0], center[1], center[2], radius, first_particle_id + k)

    #gmsh.model.addPhysicalGroup(3, range(first_particle_id, first_particle_id + nparticles), 1100)
    #gmsh.model.setPhysicalName(3, 1100, 'inclusions')

    out, _ = gmsh.model.occ.fragment([(3, domain_id)], [(3, i) for i in range(first_particle_id, first_particle_id + nparticles)])
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

    Vin = gmsh.model.getEntitiesInBoundingBox(xmin-eps, ymin-eps, zmin-eps, xmax+eps, ymax+eps, zmax+eps, 3)
    for V in Vin:
        out.remove(V)
    gmsh.model.removeEntities(out, True)

    p = gmsh.model.getBoundary(Vin, False, False, True)  # Get all points
    gmsh.model.mesh.setSize(p, mesh_size_factor * Lref)
    gmsh.option.setNumber("Mesh.ElementOrder", element_order)
    gmsh.option.setNumber('Mesh.SaveGroupsOfNodes', 1)

    Vin = gmsh.model.getEntitiesInBoundingBox(xmin-eps, ymin-eps, zmin-eps, xmax+eps, ymax+eps, zmax+eps, 3)
    V_ids = []
    for V in Vin:
        V_ids.append(V[1])
    gmsh.model.addPhysicalGroup(3, V_ids)

    create_periodicity(0, domain)
    create_periodicity(1, domain)
    create_periodicity(2, domain)

    gmsh.model.mesh.generate()
    #gmsh.model.mesh.optimize('Netgen')

    return


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
            # pply the periodicity constraint between surfaces meshes
            if (abs(xmin2 - xmin) < eps and abs(xmax2 - xmax) < eps
                    and abs(ymin2 - ymin) < eps and abs(ymax2 - ymax) < eps
                    and abs(zmin2 - zmin) < eps and abs(zmax2 - zmax) < eps):
                gmsh.model.mesh.setPeriodic(2, [j[1]], [i[1]], translation)
    return


def get_face_nodes(coords, ref, dir, eps=1e-4):
    nodes = []
    nodes_idx = []
    for k, node in enumerate(coords):
        if (node[dir] > (ref - eps)) and (node[dir] < (ref + eps)):
            nodes.append(node)
            nodes_idx.append(k)
    nodes = np.array(nodes)
    return nodes, nodes_idx

''' -----------------------------------------
MAIN CODE
 -----------------------------------------'''

# RVE creation with periodicity
domain = [0, 1, 0, 1, 0, 1]

# CFC - 4 particles - 3 at the faces ( 6 * 1/2) + 1 (8* 1/8) at the corners
r = 0.207642 #f = 15
#r = 0.228539 f = 20
#r = 0.246186  f = 25
#r = 0.261612 f = 30
#r = 0.275406 f = 35
#r = 0.287941  f = 40
#r = 0.299471 f = 45
particles =[[0.5,0.5,0.0,r],
            [0.5,0.5,1.0,r],
            [0.5,0.0,0.5,r],
            [0.5,1.0,0.5,r],
            [0.0,0.5,0.5,r],
            [1.0,0.5,0.5,r],
            [1.0,1.0,1.0,r],
            [1.0,1.0,0.0,r],
            [1.0,0.0,1.0,r],
            [0.0,1.0,1.0,r],
            [1.0,0.0,0.0,r],
            [0.0,1.0,0.0,r],
            [0.0,0.0,1.0,r],
            [0.0,0.0,0.0,r]]
            
create_RVE_particles(domain, particles, mesh_size_factor=0.01, element_order=1)
#gmsh.write("periodic_example.vtk")
gmsh.write("t_one_incl_15.inp")

# Verification
nodes = gmsh.model.mesh.getNodes()
nnodes = len(nodes[0])
coords = np.reshape(nodes[1], (nnodes,3))

face_neg, idx_neg = get_face_nodes(coords, domain[0], 0)
face_pos, idx_pos = get_face_nodes(coords, domain[1], 0)

plt.figure()
plt.plot(face_neg[:,1], face_neg[:,2], 'oy', label='xneg')
plt.plot(face_pos[:,1], face_pos[:,2], '.k', label='xpos')
plt.legend()
plt.xlabel('y')
plt.ylabel('z')
plt.axis('equal')

face_neg, idx_neg = get_face_nodes(coords, domain[2], 1)
face_pos, idx_pos = get_face_nodes(coords, domain[3], 1)

plt.figure()
plt.plot(face_neg[:,0], face_neg[:,2], 'oy', label='yneg')
plt.plot(face_pos[:,0], face_pos[:,2], '.k', label='ypos')
plt.legend()
plt.xlabel('x')
plt.ylabel('z')
plt.axis('equal')

face_neg, idx_neg = get_face_nodes(coords, domain[4], 2)
face_pos, idx_pos = get_face_nodes(coords, domain[5], 2)

plt.figure()
plt.plot(face_neg[:,0], face_neg[:,1], 'oy', label='zneg')
plt.plot(face_pos[:,0], face_pos[:,1], '.k', label='zpos')
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')

gmsh.finalize()
plt.show()
