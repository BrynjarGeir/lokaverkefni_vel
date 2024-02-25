def calculateRichardsonNumber(dT, Tave, dz, dU, g = 9.82):
    return (g * dT * dz) / (Tave * dU**2)

def calculateBruntVaisala(dT, dz, Tave, g = 9.82):
    return ((g * dT) / (Tave * dz)) ** 0.5

def calculatePotentialTemperature(T, P0, P, Rcp = 0.286):
    return T * (P0 / P) ** Rcp
    