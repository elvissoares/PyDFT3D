import numpy as np
from scipy import optimize
import sys
sys.path.insert(0, '../src/')
from eos import LJEOS
# Author: Elvis do A. Soares
# Github: @elvissoares
# Date: 2022-10-06

eos = LJEOS(sigma=1.0,epsilon=1.0,model='MBWR')

# Objective function to critical point
def objective_cr(x):
    [rho,kT] = x
    return [kT+eos.dpdrho(rho,kT),eos.d2pdrho2(rho,kT)]
# Objective function to vapor-liquid equilibria
def objective(x,kT):
    [rhov,rhol] = x
    return [kT*np.log(rhol)+eos.mu(rhol,kT)-kT*np.log(rhov)-eos.mu(rhov,kT),kT*rhol+eos.p(rhol,kT)-kT*rhov-eos.p(rhov,kT)]
# Vapor-liquid equilibrium
def vle():
    solcr = optimize.root(objective_cr,[0.3,1.25],method='lm')
    [rhoc,kTc] = solcr.x
    kTarray = np.array([kTc])
    rhovarray = np.array([rhoc])
    rholarray = np.array([rhoc])
    x = [rhoc-0.1,rhoc+0.1]
    rhol = rhoc
    kT = kTc
    while kT > 0.7:
        kT = kT - 0.001*kTc
        sol = optimize.root(objective, x, args=(kT),method='lm')
        [rhov,rhol] = sol.x
        x = sol.x
        kTarray=np.append(kTarray,kT)
        rhovarray=np.append(rhovarray,rhov)
        rholarray=np.append(rholarray,rhol)
    return [rhoc,kTc,np.hstack((rhovarray[::-1],rholarray)),np.hstack((kTarray[::-1],kTarray))]

[rhocMBWR,kTcMBWR,rhoMBWR,kTMBWR] = vle()
pMBWR = np.array([eos.p(rhoMBWR[i],kTMBWR[i]) + kTMBWR[i]*rhoMBWR[i] for i in range(rhoMBWR[rhoMBWR<rhocMBWR].size)])

eos = LJEOS(sigma=1.0,epsilon=1.0,model='NewMBWR')

# Objective function to critical point
def objective_cr(x):
    [rho,kT] = x
    return [kT+eos.dpdrho(rho,kT),eos.d2pdrho2(rho,kT)]
# Objective function to vapor-liquid equilibria
def objective(x,kT):
    [rhov,rhol] = x
    return [kT*np.log(rhol)+eos.mu(rhol,kT)-kT*np.log(rhov)-eos.mu(rhov,kT),kT*rhol+eos.p(rhol,kT)-kT*rhov-eos.p(rhov,kT)]
# Vapor-liquid equilibrium
def vle():
    solcr = optimize.root(objective_cr,[0.3,1.25],method='lm')
    [rhoc,kTc] = solcr.x
    kTarray = np.array([kTc])
    rhovarray = np.array([rhoc])
    rholarray = np.array([rhoc])
    x = [rhoc-0.1,rhoc+0.1]
    rhol = rhoc
    kT = kTc
    while kT > 0.7:
        kT = kT - 0.001*kTc
        sol = optimize.root(objective, x, args=(kT),method='lm')
        [rhov,rhol] = sol.x
        x = sol.x
        kTarray=np.append(kTarray,kT)
        rhovarray=np.append(rhovarray,rhov)
        rholarray=np.append(rholarray,rhol)
    return [rhoc,kTc,np.hstack((rhovarray[::-1],rholarray)),np.hstack((kTarray[::-1],kTarray))]

[rhoc,kTc,rho,kT] = vle()
plj = np.array([eos.p(rho[i],kT[i]) + kT[i]*rho[i] for i in range(rho[rho<rhoc].size)])

import matplotlib.pyplot as plt
import pandas as pd
plt.style.use(['science'])

df = pd.read_excel('../MCdata/MCdata-lennardjones-phasediagram.xls',sheet_name='NIST') 
plt.scatter(df['rho1'],df['T'],marker='o',edgecolors='C0',facecolors='none',linewidth=1.2,label='MC')
plt.scatter(df['rho2'],df['T'],marker='o',edgecolors='C0',facecolors='none',linewidth=1.2)
df = pd.read_excel('../MCdata/MCdata-lennardjones-phasediagram.xls',sheet_name='Agrawal1995') 
plt.scatter(df['rho1'],df['T'],marker='s',edgecolors='C0',facecolors='none',linewidth=1.2)
plt.scatter(df['rho2'],df['T'],marker='s',edgecolors='C0',facecolors='none',linewidth=1.2)
df = pd.read_excel('../MCdata/MCdata-lennardjones-phasediagram.xls',sheet_name='HansenVerlet1969') 
plt.scatter(df['rho1'],df['T'],marker='^',edgecolors='C0',facecolors='none',linewidth=1.2)
plt.scatter(df['rho2'],df['T'],marker='^',edgecolors='C0',facecolors='none',linewidth=1.2)
plt.plot(rhoMBWR,kTMBWR,linestyle='--',color='k',label='Johnson1993')
plt.plot(rho,kT,linestyle='-',color='k',label='May2012')
plt.ylabel(r'$k_B T /\epsilon$')
plt.xlabel(r'$\rho_b \sigma^3$')
plt.xlim(-0.1,1.2)
plt.ylim(0.5,1.8)
plt.legend(loc='upper left',ncol=1)

plt.savefig('../figures/phasediagram_lennardjones.png', dpi=200)
plt.show()
plt.close()

df = pd.read_excel('../MCdata/MCdata-lennardjones-phasediagram.xls',sheet_name='NIST') 
plt.scatter(1.0/df['T'],df['P'],marker='o',edgecolors='C0',facecolors='none',linewidth=1.2,label='MC')
plt.plot(1.0/kTMBWR[rhoMBWR<rhocMBWR],pMBWR,linestyle='--',color='k',label='Johnson1993')
plt.plot(1.0/kT[rho<rhoc],plj,linestyle='-',color='k',label='May2012')
plt.yscale('log')
plt.xlabel(r'$\epsilon/k_B T$')
plt.ylabel(r'$p \sigma^3/\epsilon$')
# plt.xlim(0.7,1.5)
# plt.ylim(1e-3,0.3)
plt.legend(loc='upper right',ncol=1)
plt.savefig('../figures/pressure_lennardjones.png', dpi=200)
plt.show()