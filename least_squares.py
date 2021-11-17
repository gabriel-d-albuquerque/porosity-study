import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy.optimize import least_squares

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

with open('porosity_70\strain_stress_70.txt') as f:
    E11=f.readline()
    E22=f.readline()
    E33=f.readline()
    E12=f.readline()
    S11=f.readline()
    S22=f.readline()
    S33=f.readline()
    S12=f.readline()
    RFx=f.readline()

E11 = float(E11[4:])
E22 = float(E22[4:])
E33 = float(E33[4:])
E12 = float(E12[4:])
S11 = float(S11[4:])
S22 = float(S22[4:])
S33 = float(S33[4:])
S12 = float(S12[4:])

S_fem = np.array([S11, S22, S12])
E_fem = np.array([E11, E22, E12]) + np.random.uniform(-1e-8, 1e-8, 3)

resp = least_squares(residual, (10000, 0.2), bounds=([1000, 0.05], [80000, 0.49]), args=(S_fem, E_fem), gtol=1e-14)
print(resp)