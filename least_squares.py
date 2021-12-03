import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from subprocess import Popen

#p = Popen("run.bat", cwd=r"./")
#stdout, stderr = p.communicate()

def strain_model(p, S):
    E = p[0]
    v = p[1]
    G = E/(2*(v+1))
    A = np.array([[1/E, -v/E, 0], [-v/E, 1/E, 0], [0, 0, 1/(2*G)]])
    EE = A.dot(S)
    return EE.T.flatten()
    
def residual(p, S_fem, EE_fem):
    EE = strain_model(p, S_fem)
    return EE_fem.T.flatten() - EE

fd = ['.\porosity_0', '.\porosity_10', '.\porosity_20', '.\porosity_30', '.\porosity_40', '.\porosity_50', '.\porosity_60', '.\porosity_70']
fl = ['\strain_stress_0.txt', '\strain_stress_10.txt', '\strain_stress_20.txt', '\strain_stress_30.txt', '\strain_stress_40.txt', '\strain_stress_50.txt', '\strain_stress_60.txt', '\strain_stress_70.txt']

coeff =[]
for (folder, file) in zip(fd, fl):
    with open(folder + file) as f:
        E11=f.readline()
        E22=f.readline()
        E33=f.readline()
        E12=f.readline()
        S11=f.readline()
        S22=f.readline()
        S33=f.readline()
        S12=f.readline()
        P=f.readline()
    E11 = float(E11[4:])
    E22 = float(E22[4:])
    E33 = float(E33[4:])
    E12 = float(E12[4:])
    S11 = float(S11[4:])
    S22 = float(S22[4:])
    S33 = float(S33[4:])
    S12 = float(S12[4:])
    P = float(P[2:])
    S_fem = np.array([S11, S22, S12])
    E_fem = np.array([E11, E22, E12])
    E_input = np.array([0.01, E22, 0])
    resp = least_squares(residual, (10000, 0.2), bounds=([1000, 0.05], [80000, 0.49]), args=(S_fem, E_input), gtol=1e-14)
    coeff.append([resp.x, P])

x=[]
y=[]
for elem in coeff:
    x.append(elem[1])
    y.append(elem[0][0])
print(x)
print(y)

fig, ax = plt.subplots()
ax.scatter(x, y, marker=(5, 2))
ax.set_title("Effect of porosity on elastic modulus")
ax.set_xlabel("Porosity")
ax.set_ylabel("Elastic modulus")
plt.show()