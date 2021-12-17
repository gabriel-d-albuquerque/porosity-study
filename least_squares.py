import numpy as np
import matplotlib.pyplot as plt
from numpy.core.function_base import linspace
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
    
def residual_strain(p, S_fem, EE_fem):
    EE = strain_model(p, S_fem)
    return EE_fem.T.flatten() - EE

def exponential_model(m, P):
    E_rel = np.exp(-m*P)
    return E_rel

def differential_model(m, P):
    E_rel = (1-P)**m
    return E_rel

def mori_tanaka_model(m, P):
    E_rel = (1 + (m*P)/(1 - P))**(-1)
    return E_rel

def pabst_model(m, P):
    E_rel = np.exp(-m*P/(1-P))
    return E_rel

def hasselman_model(a, P):
    E_rel = 1+(a*P)/(1-(a+1)*P)
    return E_rel

def generalized_residual(m, P, E_rel_fem, T):
    E = T(m, P)
    return E_rel_fem - E

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
    EE_fem = np.array([E11, E22, E12])
    EE_input = np.array([0.01, E22, 0])
    resp = least_squares(residual_strain, (10000, 0.2), bounds=([1000, 0.05], [80000, 0.49]), args=(S_fem, EE_input), gtol=1e-14)
    coeff.append([resp.x, P])

x=[]
y=[]
for elem in coeff:
    x.append(elem[1])
    y.append(elem[0][0]/coeff[0][0][0])
x_values = linspace(0, 1, 100)
x = np.array(x)
y = np.array(y)

relation_exponential = least_squares(generalized_residual, (1, ), bounds=([-20], [20]), args=(x, y, exponential_model), gtol=1e-14)
m_exponential = relation_exponential.x
exponential_values = np.exp(-m_exponential*x_values)

relation_differential = least_squares(generalized_residual, (1, ), bounds=([-20], [20]), args=(x, y, differential_model), gtol=1e-14)
m_differential = relation_differential.x
differential_values = (1 - x_values)**m_differential

relation_mt = least_squares(generalized_residual, (1, ), bounds=([-20], [20]), args=(x, y, mori_tanaka_model), gtol=1e-14)
m_mt = relation_mt.x
mt_values = (1+(m_mt*x_values)/(1-x_values))**(-1)

relation_pabst = least_squares(generalized_residual, (1, ), bounds=([-20], [20]), args=(x, y, pabst_model), gtol=1e-14)
m_pabst = relation_pabst.x
pabst_values = np.exp(-m_pabst*x_values/(1-x_values))

relation_hasselman = least_squares(generalized_residual, (-1, ), bounds=([-20], [20]), args=(x, y, hasselman_model), gtol=1e-14)
a_hasselman = relation_hasselman.x
hasselman_values = 1+(a_hasselman*x_values)/(1-(a_hasselman+1)*x_values)

voigt_values = 1-x_values

ra_values = (1-x_values)**2/(1+2*x_values-3*0.33*x_values)

fig, ax = plt.subplots()
ax.scatter(x, y, marker=(5, 2), label='FEM model', color='red')
ax.plot(x_values, exponential_values, linewidth=1.0, label='Exponential', color='blue')
ax.plot(x_values, differential_values, linewidth=1.0, label='Differential', color= 'purple')
ax.plot(x_values, mt_values, linewidth=1.0, label='Mori-Tanaka', color= 'lime')
ax.plot(x_values, voigt_values, linewidth=1.0, label='Voigt Bound', color= 'orange')
ax.plot(x_values, pabst_values, linewidth=1.0, label='Pabst', color='darkgreen')
ax.plot(x_values, hasselman_values, linewidth=1.0, label='Hasselman', color='cyan')
ax.plot(x_values, ra_values, linewidth=1.0, label='Ramakrishnan-Arunachalam', color='crimson')
ax.legend()
ax.set_title("Effect of porosity on elastic modulus")
ax.set_xlabel("Porosity")
ax.set_ylabel("Elastic modulus ratio")
ax.grid(color="gray", linestyle="--", linewidth=0.7)
plt.show()