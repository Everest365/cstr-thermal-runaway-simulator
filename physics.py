import numpy as np
from scipy.integrate import solve_ivp

PARAMS = {
    "q": 100.0,        # Volumetric flow rate (L/min)
    "V": 100.0,        # Reactor volume (L)
    "rho": 1000.0,     # Density (g/L)
    "Cp": 0.239,       # Heat capacity (J/g*K)
    "dH": -50000.0,    # Exothermic heat of reaction (J/mol)
    "E_R": 8750.0,     # Activation energy / Gas constant (K)
    "k0": 7.2e10,      # Pre-exponential factor (1/min)
    "UA": 50000.0,     # Heat transfer coeff * area (J/min*K)
    "Ca0": 1.0,        # Feed concentration (mol/L)
    "T0": 350.0,       # Feed temperature (K)
}

def cstr_odes(t, y, Tc, p, pump_failure=False):
    Ca, T = y
    T_safe = np.clip(T, 200.0, 2000.0)
    k = p["k0"] * np.exp(-p["E_R"] / T_safe)
    
    # Simulate a 70% drop in cooling efficiency after t = 3.0 min
    current_UA = p["UA"] * 0.3 if (pump_failure and t >= 3.0) else p["UA"]
    
    dCa_dt = (p["q"] / p["V"]) * (p["Ca0"] - Ca) - k * Ca
    
    heat_flow = (p["q"] / p["V"]) * (p["T0"] - T)
    heat_gen = (-p["dH"] / (p["rho"] * p["Cp"])) * k * Ca
    heat_rem = (current_UA / (p["V"] * p["rho"] * p["Cp"])) * (Tc - T)
    dT_dt = heat_flow + heat_gen + heat_rem
    
    return [dCa_dt, dT_dt]

def run_simulation(Tc=300.0, T_init=350.0, Ca_init=0.5, t_max=10.0, custom_params=None, pump_failure=False):
    p = PARAMS.copy()
    if custom_params:
        p.update(custom_params)
        
    t_eval = np.linspace(0, t_max, 500)
    sol = solve_ivp(
        fun=lambda t, y: cstr_odes(t, y, Tc, p, pump_failure),
        t_span=(0, t_max),
        y0=[Ca_init, T_init],
        t_eval=t_eval,
        method="RK45"
    )
    return sol.t, sol.y[0], sol.y[1]
