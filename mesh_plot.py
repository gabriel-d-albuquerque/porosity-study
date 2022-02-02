import matplotlib.pyplot as plt
import numpy as np

fl = ['\mesh_01.txt', '\mesh_025.txt', '\mesh_05.txt', '\mesh_1.txt', '\mesh_2.txt', '\mesh_3.txt']

S11_values =[]
S22_values =[]
x=[]
for file in fl:
    with open('.\mesh_study' + file) as f:
        S11=f.readline()
        S22=f.readline()
        S33=f.readline()
        S12=f.readline()
        s=f.readline()
    S11 = float(S11[4:])
    S22 = float(S22[4:])
    S33 = float(S33[4:])
    S12 = float(S12[4:])
    s = float(s[4:])
    S11_values.append(S11)
    S22_values.append(S22)
    x.append(s)

S11_values = np.array(S11_values)/S11_values[5]
S22_values = np.array(S22_values)/S22_values[5]

fig, ax = plt.subplots()
ax.scatter(x, S11_values, marker=(5, 2), label='S11', color='red')
ax.scatter(x, S22_values, marker=(5, 2), label='S22', color='blue')
ax.legend()
ax.set_title("Influence of mesh refinement on stress components")
ax.set_xlabel("Mesh size [mm]")
ax.set_ylabel("Relative stress component")
ax.grid(color="gray", linestyle="--", linewidth=0.7)
plt.yscale("log")
plt.show()

fig, ax = plt.subplots()
ax.scatter(x, S11_values, marker=(5, 2), label='S11', color='red')
ax.scatter(x, S22_values, marker=(5, 2), label='S22', color='blue')
ax.legend()
ax.set_title("Influence of mesh refinement on stress components")
ax.set_xlabel("Mesh size [mm]")
ax.set_ylabel("Relative stress component")
ax.grid(color="gray", linestyle="--", linewidth=0.7)
plt.show()

