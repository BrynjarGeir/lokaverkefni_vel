def calculateRichardsonNumber(dT, Tave, dz, dU, g = 9.82):
    return (g * dT * dz) / (Tave * dU**2)

def calculateBruntVaisala(dT, dz, Tave, g = 9.82):
    return ((g * dT) / (Tave * dz)) ** 0.5

def calculatePotentialTemperature(T, P0, P, Rcp = 0.286):
    return T * (P0 / P) ** Rcp

def rowRichardson(row):
    theta_0 = calculatePotentialTemperature(row.t_15, 1000, row.p_15)
    theta_1 = calculatePotentialTemperature(row.t_250, 1000, row.p_250)
    theta_2 = calculatePotentialTemperature(row.t_500, 1000, row.p_500)
    dT01 = theta_1 - theta_0
    dT12 = theta_2 - theta_1
    Tave01 = (theta_0 + theta_1) / 2
    Tave12 = (theta_1 + theta_2) / 2
    dz01, dz12 = 250 - 15, 500 - 250
    dU01 = row.ws_250 - row.ws_15
    dU12 = row.ws_500 - row.ws_250
    g = 9.82

    Ri_01 = (g * dT01 * dz01) / (Tave01 * dU01**2)
    Ri_12 = (g * dT12 * dz12) / (Tave12 * dU12**2)
    return Ri_01, Ri_12

def rowBruntVaisala(row):
    theta_0 = calculatePotentialTemperature(row.t_15, 1000, row.p_15)
    theta_1 = calculatePotentialTemperature(row.t_250, 1000, row.p_250)
    theta_2 = calculatePotentialTemperature(row.t_500, 1000, row.p_500)
    dT01 = theta_1 - theta_0
    dT12 = theta_2 - theta_1
    Tave01 = (theta_0 + theta_1) / 2
    Tave12 = (theta_1 + theta_2) / 2
    dz01, dz12 = 250 - 15, 500 - 250
    g = 9.82

    N_01 = ((g * dT01) / (Tave01 * dz01))
    N_02 = ((g * dT12) / (Tave12 * dz12))

    return N_01, N_02
    