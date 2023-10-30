import math as mt

calibre_data = {
    14: {"Diametro": 0.163, "Imax": 18},
    12: {"Diametro": 0.205, "Imax": 25},
    10: {"Diametro": 0.259, "Imax": 30},
    8: {"Diametro": 0.326, "Imax": 40},
    6: {"Diametro": 0.412, "Imax": 60},
    5: {"Diametro": 0.462, "Imax": 65},
    4: {"Diametro": 0.519, "Imax": 85}
}

def calculate_energy(potency, hours):
    return ((potency/1000) * hours) # para que sea KWh y no Wh 

def calculate_cost(energy):
    price_perKWh = 1.386014
    return energy * price_perKWh

def calculate_calibre(large, total_V, total_I):
    p = 1.72e-8
    pi_value = mt.pi

    diameter = mt.sqrt((p*large*4*total_I)/(pi_value*total_V))

    return diameter 