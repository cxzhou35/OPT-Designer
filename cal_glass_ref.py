from math import *
# two variables, wl: wavelength   gt: glass_type
def calculate_glass_ref(x, gt):
    # initialize
    K1 = 1
    L1 = 1
    K2 = 1
    L2 = 1
    K3 = 1
    L3 = 1

    if(gt == 0):
        return 1.0000000000
    elif (gt == 1):
        K1 = 6.145552510E-01
        L1 = 1.459878840E-02
        K2 = 6.567750170E-01
        L2 = 2.877695880E-03
        K3 = 1.026993460E+00
        L3 = 1.076530510E+02

    elif (gt == 2):
        K1 = 1.676433800E-01
        L1 = 6.051777110E-02
        K2 = 1.543350760E+00
        L2 = 1.185242730E-02
        K3 = 1.173131230E+00
        L3 = 1.136711000E+02

    ref = sqrt((K1 * x * x) / (x * x - L1) + (K2 * x * x) /
                      (x * x - L2) + (K3 * x * x) / (x * x - L3) + 1)
    return ref

def main():
    wavelength = float(input("Please input the wavelength(um) here: "))
    glass_type = int(input("Please input the glass type here(0: air 1: H-K9L 2: H-ZF2): "))
    ref = calculate_glass_ref(wavelength, glass_type)


if __name__ == '__main__':
    main()
