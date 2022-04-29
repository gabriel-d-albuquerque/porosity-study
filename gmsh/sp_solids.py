from os import remove
import numpy as np
import gmsh
import sys

gmsh.initialize()

gmsh.model.add("solidos-especiais")

def createPolygon(xyz_poly):
    i_p = 1
    for p in xyz_poly:
        last_point = gmsh.model.occ.addPoint(p[0], p[1], p[2])
        i_p += 1

    i_l = 1
    for p in range(last_point - i_p + 2, last_point):
        gmsh.model.occ.addLine(p, p + 1)
        i_l += 1
    last_line = gmsh.model.occ.addLine(last_point, last_point - i_p + 2)
    i_l += 1

    last_cl = gmsh.model.occ.addCurveLoop([k for k in range(last_line - i_l + 2, last_line + 1)])

    polygon = gmsh.model.occ.addPlaneSurface([last_cl])

    return polygon

L = 1

xyz_hex = [[np.sqrt(2)*L, 0, np.sqrt(2)*L/2],
           [np.sqrt(2)*L/2, 0, np.sqrt(2)*L],
           [0, np.sqrt(2)*L/2, np.sqrt(2)*L],
           [0, np.sqrt(2)*L, np.sqrt(2)*L/2],
           [np.sqrt(2)*L/2, np.sqrt(2)*L, 0],
           [np.sqrt(2)*L, np.sqrt(2)*L/2, 0]]
hexagon = createPolygon(xyz_hex)
x_hex, y_hex, z_hex = gmsh.model.occ.getCenterOfMass(2, hexagon)

xyz_trian = [[np.sqrt(2)*L/2, 0, np.sqrt(2)*L],
             [0, 0, np.sqrt(2)*L],
             [0, np.sqrt(2)*L/2, np.sqrt(2)*L]]
triangle = createPolygon(xyz_trian)
fuse, map = gmsh.model.occ.fuse([(2, triangle)], [(2, hexagon)])

xyz_trian = [[0, np.sqrt(2)*L, 0],
             [0, np.sqrt(2)*L, np.sqrt(2)*L/2],
             [np.sqrt(2)*L/2, np.sqrt(2)*L, 0]]
triangle = createPolygon(xyz_trian)
fuse, map = gmsh.model.occ.fuse([(2, triangle)], fuse)

xyz_trian = [[np.sqrt(2)*L, 0, 0],
             [np.sqrt(2)*L, np.sqrt(2)*L/2, 0],
             [np.sqrt(2)*L, 0, np.sqrt(2)*L/2]]
triangle = createPolygon(xyz_trian)
fuse, map = gmsh.model.occ.fuse([(2, triangle)], fuse)

copy = gmsh.model.occ.copy(fuse)
gmsh.model.occ.mirror(copy, 1, 0, 0, 0)
fuse, map = gmsh.model.occ.fuse(fuse, copy)

copy = gmsh.model.occ.copy(fuse)
gmsh.model.occ.mirror(copy, 0, 0, 1, 0)
fuse, map = gmsh.model.occ.fuse(fuse, copy)

copy = gmsh.model.occ.copy(fuse)
gmsh.model.occ.mirror(copy, 0, 1, 0, 0)
fuse, map = gmsh.model.occ.fuse(fuse, copy)

gmsh.model.occ.synchronize()

gmsh.model.occ.remove_all_duplicates

dims_ext = []
tags_ext = []
for i in range(len(fuse)):
    dim_i, tag_i = fuse[i]
    dims_ext.append(dim_i)
    tags_ext.append(tag_i)
ext = gmsh.model.occ.addSurfaceLoop(tags_ext)

gmsh.model.occ.synchronize()

rve = gmsh.model.occ.addVolume([ext])
copy = gmsh.model.occ.copy([(3, rve)])
gmsh.model.occ.dilate(copy, 0, 0, 0, 0.9, 0.9, 0.9)
offset, map = gmsh.model.occ.cut([(3, rve)], copy)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, x_hex*2, y_hex*2, z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, x_hex*2, y_hex*2, -z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, x_hex*2, -y_hex*2, z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, x_hex*2, -y_hex*2, -z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, -x_hex*2, y_hex*2, z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, -x_hex*2, y_hex*2, -z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, -x_hex*2, -y_hex*2, z_hex*2)

copy = gmsh.model.occ.copy(offset)
gmsh.model.occ.translate(copy, -x_hex*2, -y_hex*2, -z_hex*2)

vt = gmsh.model.occ.getEntities(3)

vt, map = gmsh.model.occ.fuse(vt[0:1], vt[1:])

gmsh.model.occ.synchronize()

gmsh.model.occ.addBox(-np.sqrt(2)*L, -np.sqrt(2)*L, -np.sqrt(2)*L, 2*np.sqrt(2)*L, 2*np.sqrt(2)*L, 2*np.sqrt(2)*L, 10)
rve, map = gmsh.model.occ.intersect(vt, [(3, 10)])

gmsh.model.occ.remove_all_duplicates

gmsh.model.addPhysicalGroup(3, [1])

gmsh.model.occ.synchronize()

mesh_size_factor = 0.1
p = gmsh.model.occ.getEntities(0)
gmsh.model.mesh.setSize(p, mesh_size_factor)

gmsh.model.occ.synchronize()

gmsh.model.mesh.generate()

gmsh.write("sp-solid.inp")

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()