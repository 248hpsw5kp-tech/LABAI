def pcr_mix(reactions, volume=25):
    total = reactions * volume

    mix = {
        "10X Buffer (µL)": 2.5 * reactions,
        "dNTPs (µL)": 0.5 * reactions,
        "Forward Primer (µL)": 1 * reactions,
        "Reverse Primer (µL)": 1 * reactions,
        "Taq Polymerase (µL)": 0.25 * reactions,
        "Water (µL)": total - (2.5+0.5+1+1+0.25)*reactions
    }
    return mix


def melting_temp(sequence):
    sequence = sequence.upper()
    A = sequence.count("A")
    T = sequence.count("T")
    G = sequence.count("G")
    C = sequence.count("C")
    return 2*(A+T) + 4*(G+C)
