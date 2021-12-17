import matplotlib.pyplot as plt

fd = ['.\mesh_1', '.\mesh_2', '.\mesh_3', '.\mesh_4', '.\mesh_5', '.\mesh_6', '.\mesh_7', '.\mesh_8', '.\mesh_9', '.\mesh_10']
fl = ['\mesh_1.txt', '\mesh_2.txt', '\mesh_3.txt', '\mesh_4.txt', '\mesh_5.txt', '\mesh_6.txt', '\mesh_7.txt', '\mesh_8.txt', '\mesh_9.txt', '\mesh_10.txt']

S11_values =[]
S22_values =[]
x=[]
for (folder, file) in zip(fd, fl):
    with open(folder + file) as f:
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

fig, ax = plt.subplots()
ax.scatter(x, S11_values, marker=(5, 2), label='S11', color='red')
ax.legend()
ax.set_title("Effect of mesh refinement on stress")
ax.set_xlabel("Mesh size [mm]")
ax.set_ylabel("Stress [MPa]")
ax.grid(color="gray", linestyle="--", linewidth=0.7)
plt.show()

fig, ax = plt.subplots()
ax.scatter(x, S22_values, marker=(5, 2), label='S22', color='red')
ax.legend()
ax.set_title("Effect of mesh refinement on stress")
ax.set_xlabel("Mesh size [mm]")
ax.set_ylabel("Stress [MPa]")
ax.grid(color="gray", linestyle="--", linewidth=0.7)
plt.show()