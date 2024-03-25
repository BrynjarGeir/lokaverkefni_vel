import numpy as np

def calculateRichardsonNumber(dT, Tave, dz, dU, g = 9.82):
    return (g * dT * dz) / (Tave * dU**2)

def calculateBruntVaisala(dT, dz, Tave, g = 9.82):
    return ((g * dT) / (Tave * dz)) ** 0.5

def calculatePotentialTemperature(T, P0, P, Rcp = 0.286):
    return T * (P0 / P) ** Rcp

def rowRichardson(row):
    theta_0 = calculatePotentialTemperature(row.t_15, 100000, row.p_15)
    theta_1 = calculatePotentialTemperature(row.t_250, 100000, row.p_250)
    theta_2 = calculatePotentialTemperature(row.t_500, 100000, row.p_500)
    dT01 = theta_1 - theta_0
    dT12 = theta_2 - theta_1
    dT02 = theta_2 - theta_0
    Tave01 = (theta_0 + theta_1) / 2
    Tave12 = (theta_1 + theta_2) / 2
    Tave02 = (theta_0 + theta_2) / 2
    dz01, dz12, dz02 = 250 - 15, 500 - 250, 500-15
    dU01 = row.ws_250 - row.ws_15
    dU12 = row.ws_500 - row.ws_250
    dU02 = row.ws_500 - row.ws_15
    g = 9.82

    try:
        Ri_01 = (g * dT01 * dz01) / (Tave01 * dU01**2)
    except ZeroDivisionError:
        Ri_01 = np.inf
    except Exception as e:
        Ri_01 = np.nan
    
    try:
        Ri_12 = (g * dT12 * dz12) / (Tave12 * dU12**2)
    except ZeroDivisionError:
        Ri_12 = np.inf
    except Exception as e:
        Ri_12 = np.nan

    try:
        Ri_02 = (g * dT02 * dz02) / (Tave02 * dU02**2)
    except ZeroDivisionError:
        Ri_02 = np.inf
    except Exception as e:
        Ri_01 = np.nan

    return Ri_01, Ri_12, Ri_02

def rowBruntVaisala(row):
    theta_0 = calculatePotentialTemperature(row.t_15, 100000, row.p_15)
    theta_1 = calculatePotentialTemperature(row.t_250, 100000, row.p_250)
    theta_2 = calculatePotentialTemperature(row.t_500, 100000, row.p_500)
    dT01 = theta_1 - theta_0
    dT12 = theta_2 - theta_1
    dT02 = theta_2 - theta_0
    Tave01 = (theta_0 + theta_1) / 2
    Tave12 = (theta_1 + theta_2) / 2
    Tave02 = (theta_0 + theta_2) / 2
    dz01, dz12, dz02 = 250 - 15, 500 - 250, 500 - 15
    g = 9.82

    try:
        N_01 = ((g * dT01) / (Tave01 * dz01))**0.5
    except ZeroDivisionError:
        N_01 = np.inf
    except Exception as e:
        N_01 = np.nan

    try:
        N_12 = ((g * dT12) / (Tave12 * dz12))**0.5
    except ZeroDivisionError:
        N_12 = np.inf
    except Exception as e:
        N_12 = np.nan
    
    try:
        N_02 = ((g * dT02) / (Tave02 * dz02))**0.5
    except ZeroDivisionError:
        N_02 = np.inf
    except Exception as e:
        N_02 = np.nan

    return N_01, N_12, N_02
    