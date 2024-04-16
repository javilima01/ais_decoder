import numpy as np
import crcmod
from scipy.special import erf

class matlab:
    @classmethod
    def bitarray_to_bytes(cls, s) -> bytes:
        s = "".join(map(str, s))
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

    @classmethod
    def _CRCGenerator(cls):
        return crcmod.predefined.mkPredefinedCrcFun("crc-16-genibus")

    @classmethod
    def pad_to_nearest_multiple_of_eight(cls, arr):
        length = len(arr)
        remainder = length % 8
        if remainder != 0:
            pad_width = 8 - remainder
            arr = np.pad(arr, (0, pad_width), mode='constant', constant_values=0)
        return arr

    @classmethod
    def get_checksum(cls, data, index):
        if len(data) < index + 16:
            return False
        crcGen = matlab._CRCGenerator()
        string = matlab.bitarray_to_bytes(data[:index])
        checkSum = crcGen(string)
        return hex(checkSum)[2:] == matlab.bitarray_to_bytes(data[index:index + 16]).hex()

    @classmethod
    def gaussdesign(cls, bt, span, sps, half=False):
        """
        Esta función implementa la función `gaussdesign` de MATLAB en Python.

        Parámetros:
        bt: Producto de banda ancha de tiempo de símbolo de 3 dB
        span: Número de símbolos
        sps: Muestras por símbolo

        Retorno:
        h: Un vector de impulso de filtro FIR con longitud `2 * span * sps`
        """

        sigma = np.sqrt(np.log(2)) / (2 * np.pi * bt)

        # Cálculo del parámetro de forma del filtro
        alpha = 1 / (2 * (sigma**2))

        # Cálculo del vector de tiempo
        t = np.arange((-span * sps) / 2, (span * sps) / 2 + 1) / sps

        # Cálculo del filtro gaussiano
        h = np.exp(-alpha * (t**2))

        # Normalización del filtro
        h = h / (np.sqrt(2 * np.pi) * sigma)
        h_norm = h / np.sum(h)
        if half:
            return h_norm[: -int((span * sps) / 2 + 1)]
        return h_norm

    @classmethod
    def gmsk_modulate(cls, data, bt, pulse_length, samplesPerSymbol):
        """
        Implements Gaussian Minimum Shift Keying (GMSK) modulation in Python.

        Args:
            data: A binary data stream (numpy array of 0s and 1s).
            bt: Gaussian filter bandwidth-to-symbol rate factor.
            pulse_length: Pulse length (T).
            samplesPerSymbol: Number of samples per symbol (N).

        Returns:
            A numpy array representing the baseband modulated signal.
        """

        # Calculate Gaussian filter bandwidth
        T = pulse_length
        B = bt / T


        def gmsk_pulse(t):
            """
            Defines the GMSK pulse shaping function using the Q-function.
            """
            q_subtraction = 2 * np.pi * B * (t - T / 2) / np.sqrt(np.log(2))
            q_addition = 2 * np.pi * B * (t + T / 2) / np.sqrt(np.log(2))
            q_subtraction = np.array(
                [erf(i) for i in q_subtraction]
            )
            q_addition = np.array(
                [erf(i) for i in q_addition]
            )
            return 1 / (2 * T) * (q_subtraction - q_addition)

        # Modulate the data
        modulated_data = np.zeros(len(data) * samplesPerSymbol, dtype=np.complex_)
        phase = 0  # Initial phase offset
        data = (data - 0.5) * 2
        k = 2.7
        for i in range(len(data)):
            bit = data[i]
            t = np.linspace(-T, T, samplesPerSymbol)
            pulse = k * gmsk_pulse(t)
            modulated_data[i * samplesPerSymbol: (i + 1) * samplesPerSymbol] = np.exp(bit * 1j * (phase + np.cumsum(pulse)))
            phase += bit * np.sum(pulse)

        return modulated_data
    
    @classmethod
    def wola(cls, x, N):
        if x.ndim > 1:
            x = x.flatten()  # Convertir a un vector si no lo es
        L = len(x)

        if N >= L:
            return x  # No es necesario aplicar WOLA, devolver la señal original

        M = -(-L // N)  # Factor de WOLA (equivalente a ceil(L/N) en MATLAB)
        aux = np.zeros(M * N, dtype=x.dtype)
        aux[:L] = x
        y = np.sum(aux.reshape((M, N)), axis=0)
        return y

    @classmethod
    def semavg(cls, X, M):
        if X.ndim > 1 or X.size == 0:
            raise ValueError("El parámetro X debe ser un vector no vacío")

        if isinstance(M, int):
            M = [M]

        if len(M) != 1:
            raise ValueError("El parámetro M debe ser un escalar")

        M = M[0]

        if not isinstance(M, int) or M <= 0:
            raise ValueError("El parámetro M debe ser un entero positivo")

        if len(X) < M / 2:
            raise ValueError("Número de muestras del búfer de entrada incorrecto")

        xx = np.concatenate(
            (
                [X[int((M - 1) / 2) - i] for i in range(int((M - 1) / 2), 0, -1)],
                X,
                [X[-i] for i in range(1, int(M / 2) + 1)],
            )
        )
        y = np.convolve(np.ones(M) / M, xx, mode="valid")
        return y

    # fin semavg

    @classmethod
    def gefh_detect(
        cls, Flags_Deteccion, Flags_Postdeteccion
    ):  # esta funcion hubo que adaptarla porque si no en python daba uno menos que en matlab (Daba Bin_Inicial: 222 Bin_Final: 363 en vez de 223 y 364)
        Y = []
        numero_hoppers = 0
        flag_hopper = 0

        for ciclo in range(len(Flags_Deteccion)):
            C1 = (Flags_Deteccion[ciclo] == 1) and (flag_hopper == 0)
            C2 = (Flags_Postdeteccion[ciclo] == 0) and (flag_hopper == 1)

            if C1:
                Y.append({"Bin_Inicial": ciclo + 1, "Bin_Final": None})
                flag_hopper = 1

            if C2:
                Y[numero_hoppers]["Bin_Final"] = ciclo
                numero_hoppers += 1
                flag_hopper = 0

        # Último hopper
        if flag_hopper == 1:
            Y.append({"Bin_Inicial": len(Flags_Deteccion), "Bin_Final": None})

        return Y

    @classmethod
    def syncGen(cls, samplesPerSymbol, sequence=None):
        # Generate ideal AIS sync waveform
        # Set up training sequence
        if sequence is None:
            tr1 = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=bool)
        else:
            tr1 = np.array(sequence, dtype=bool)
        # Apply NRZI encoding
        for ii in range(1, len(tr1)):
            if tr1[ii] == 1:
                tr1[ii] = tr1[ii - 1]
            else:
                tr1[ii] = not tr1[ii - 1]
        modulated_signal = matlab.gmsk_modulate(tr1, 0.3, 3, samplesPerSymbol)

        data = np.genfromtxt("signal.csv", delimiter=",", names=True, dtype=None)
        complex_array = np.array([complex(row["real"], row["imaginary"]) for row in data])

        return complex_array

    @classmethod
    def aisUnstuff(cls, bitsIn):
        # aisUnstuff takes message bits in and outputs a new bitstream with the
        # zero stuffing bits removed
        onesCount = 0
        bitsOut = np.zeros(len(bitsIn), dtype=int)
        bitsOutIdx = 0
        for ii in range(len(bitsIn)):
            if onesCount < 5:
                bitsOut[bitsOutIdx] = bitsIn[ii]
                bitsOutIdx += 1
            if bitsIn[ii] == 1:
                onesCount += 1
            else:
                onesCount = 0
        bitsOutIdx = min(len(bitsIn), bitsOutIdx)
        bitsOut = bitsOut[:bitsOutIdx]

        return bitsOut
