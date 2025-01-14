import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import scipy.signal

F_s, x = scipy.io.wavfile.read(
    "../data/g_maj.wav"
)

sliceRun = slice(
    int(0.08 * F_s), int(4.25 * F_s)
)
T = np.linspace(
    0, x.size / F_s, x.size, endpoint=False
)

y = x[sliceRun][
    : int(np.floor(x[sliceRun].size / 14) * 14)
].reshape((14, -1))[:, 1000:-1000]
N = y.shape[1]

dfts = np.fft.fft(y, axis=1)
freqs = np.fft.fftfreq(N) * F_s
plotInd = np.logical_and(
    (np.abs(freqs)) < 200, freqs > 0
)

plt.figure()
plt.subplot(211)
plt.plot(T[sliceRun], x[sliceRun], linewidth=0.4)
plt.xlabel("t[s]")
plt.ylabel("x[n]")
plt.subplot(212)
for dd in range(8):
    spectrum_dB = 10 * np.log10(
        np.abs(dfts[dd, :]) ** 2
    )
    plt.plot(
        freqs[plotInd],
        spectrum_dB[plotInd],
    )
    peakSearch = scipy.signal.find_peaks(
        spectrum_dB, height=120
    )
    peaksPos = peakSearch[0]
    peaksHeight = peakSearch[1]["peak_heights"]
    filterPeaks = np.logical_and(
        freqs[peaksPos] > 0,
        freqs[peaksPos] < 200,
    )
    plt.stem(
        freqs[peaksPos[filterPeaks]],
        peaksHeight[filterPeaks],
        bottom=np.min(spectrum_dB[plotInd]),
        basefmt=" ",
    )
    print(freqs[peaksPos[filterPeaks]])
plt.ylabel("10log10(|X(F)|^2)")
plt.xlabel("F[Hz]")
plt.show()
