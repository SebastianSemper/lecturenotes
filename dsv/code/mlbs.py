import numpy as np
import matplotlib.pyplot as plt


def gen_MLBS(taps: int, start: int):
    numTaps = int(
        np.ceil(np.log2(taps)).astype(int)
    )
    length = 2**numTaps - 1
    state = start

    sequence = []
    for ll in range(length):
        # move last bit to output
        sequence.append(state & 1)
        feedback = state
        for tt in range(1, numTaps - 1):
            if (taps >> (numTaps - tt - 1)) & 1:
                feedback ^= state >> tt
        # keep only last bit of combined XOR
        feedback &= 1
        # shift registers
        state = state >> 1
        # feedback from back to front
        state |= feedback << (numTaps - 1)

    sequence = 2 * (np.array(sequence) - 0.5)
    return sequence


if __name__ == "__main__":
    sequence = gen_MLBS(0xC + 1, 1)
    plt.stem(sequence)
    plt.show()
