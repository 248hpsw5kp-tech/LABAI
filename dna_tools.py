from Bio.Seq import Seq

def gc_content(seq):
    seq = seq.upper()
    return (seq.count("G") + seq.count("C")) / len(seq) * 100


def find_orfs(sequence):
    seq = Seq(sequence)
    proteins = []
    for frame in range(3):
        trans = seq[frame:].translate()
        proteins.append(str(trans))
    return proteins
