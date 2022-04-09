import numpy as np
import gmsh

gmsh.initialize()

gmsh.model.add("solidos-especiais")

L = 1
lc = 1e-2

gmsh.model.occ.addBox(0, 0, 0, np.sqrt(2)*L, np.sqrt(2)*L, np.sqrt(2)*L, 1)

xyz = [[np.sqrt(2)*L, 0, np.sqrt(2)*L/2],
       [np.sqrt(2)*L/2, 0, np.sqrt(2)*L],
       [0, np.sqrt(2)*L/2, np.sqrt(2)*L],
       [0, np.sqrt(2)*L, np.sqrt(2)*L/2],
       [np.sqrt(2)*L/2, np.sqrt(2)*L, 0],
       [np.sqrt(2)*L, np.sqrt(2)*L/2, 0]]

t = 10
for p in xyz:
    gmsh.model.occ.addPoint(p[0], p[1], p[2], lc, t)
    t += 1

t = 100
for l in range(10, 14):
    gmsh.model.occ.addLine(l, l+1, t)
    t += 1
gmsh.model.occ.addLine(l+1, 10, t)
gmsh.model.occ.addCurveLoop([k for k in range(100, 105)], 100)
hexagon = gmsh.model.occ.addPlaneSurface([100])

gmsh.model.occ.synchronize()

gmsh.finalize()
