# Proceso para decodificar una señal AIS en phyton

from scipy.signal import resample_poly, lfilter, convolve
import scipy.io as sio
import numpy as np
from modules import matlab
from scipy.signal.windows import kaiser
from dataextractor import get_message
archivo = "senhal_depuracion_ais_384K.dat"
# Leer el archivo en modo binario ('rb')
with open(archivo, "rb") as file:
    # Leer todos los bytes del archivo
    bytes_data = file.read()

# Convertir los bytes en números complejos
contenido = np.frombuffer(bytes_data, dtype=np.complex64)
#print(contenido) -> coincide

xnum = [complex(numero) for numero in contenido]
xt = np.array(xnum)
# from rtlsdr import RtlSdr
# from threading import Semaphore, Thread
# aux_samples = Semaphore(1)

# xt = np.array([], np.complex_)
# def add_samples(iq, context):
#     global xt
#     aux_samples.acquire()
#     xt = np.concatenate((xt, iq))
#     aux_samples.release()

# def read_samples():
#     sdr.read_samples_async(add_samples)

# import time
# sdr = RtlSdr()
# sdr.sample_rate = 2.048e6  # Frecuencia de muestreo en Hz
# sdr.center_freq = 161.75e6    # Frecuencia central en Hz (frecuencia AIS en mar)
# sdr.gain = "auto"

# print(f"FS: {sdr.sample_rate}")
# samples_thread = Thread(target=read_samples)
# samples_thread.start()

# print("Started sleeping")
# time.sleep(30)
# print("Finished sleeping")


# sdr.cancel_read_async()
# samples_thread.join()

# Realizamos la FFT de la señal
print("Started decomulating")
fs_nueva = 96000
fs = 384000
# fs = sdr.sample_rate
x_resampled = resample_poly(xt, fs_nueva, fs)  # no es exacto del todo
#print(x_resampled) -> coincide

xfft = np.fft.fft(x_resampled)
xfft_db = 20 * np.log10(np.abs(xfft))
#print(xfft_db) -> coincide
vector = np.linspace(-fs_nueva, fs_nueva, len(x_resampled))

# DETECCIÓN GRUESA MEDIANTE FFT
# Primero, nos interesa ver segmentos de la señal para encontrar el pulso,
# para ello se realiza un bucle de MxN

M = 960
W = 15
N = int(M / W)

# Enventanamos la señal, la ventana kaiser es la que mejor suaviza los
# aumentos en la señal
ventana = kaiser(M, 6.9)
wventana = ventana * M / sum(ventana)
#print(wventana) -> coincide

fres = 100
frecs = M / N * fres * np.arange(0, N)

# OJO, los indices hay que sumarle uno porque, la funcion find no es igual que where ni flatnonzero, y si no los indices daban mal
# Hallamos los indices de ruido
# cond1ruido = (frecs <= 15000) & (frecs >= 5000)
# cond2ruido = (frecs >= np.mod(-15000, fs_nueva)) & (frecs <= np.mod (-5000,fs_nueva))
indruido = (
    np.flatnonzero(
        ((frecs <= 15000) & (frecs >= 5000))
        | ((frecs >= np.mod(-15000, fs_nueva)) & (frecs <= np.mod(-5000, fs_nueva)))
    )
) + 1
#print(indruido) -> coincide
# Hallamos los indices ais superior e inferior
indaissup = (np.flatnonzero(((frecs <= 25000 + 6125) & (frecs >= 25000 - 6125)))) + 1
#print(indaissup) -> coincide
indaisinf = (
    np.flatnonzero(
        (frecs >= np.mod(-(25000 + 6125), fs_nueva))
        & (frecs <= np.mod(-(25000 - 6125), fs_nueva))
    )
) + 1
#print(indaisinf) -> coincide

tam = len(indaissup)
#print(tam) -> coincide
dist = int(np.floor(len(x_resampled) - M) / N + 1)
#print(dist) -> coincide

nivelruido = []
nivelruidos = []
aissup = []
aisinf = []
wffty_resultados = []

# Cambios andrea:
for ii in range(int((len(x_resampled) - M) / N + 1)):
    y = x_resampled[ii * N : ii * N + M]  # necesita el N+1 para ser igual que en matlab
    #print(y) -> coincide
    wffty = np.fft.fft(matlab.wola(wventana * y, N)) / M
    # wffty = np.fft.fft(np.multiply(w, y), N) / M
    wffty_dB = 20 * np.log10(np.abs(wffty))
    wffty_resultados.append(wffty_dB)

    nivelruidos = np.abs(wffty[indruido]) ** 2 * M / N * tam
    nivelruido.append(np.mean(nivelruidos) + 2.6 * np.std(nivelruidos))
    #print(nivelruido) -> coincide
    aissup.append(np.mean(np.abs(wffty[indaissup]) ** 2 * M / N * tam))
    #print(aissup) -> coincide
    aisinf.append(np.mean(np.abs(wffty[indaisinf]) ** 2 * M / N * tam))
    #print(aisinf) -> coincide
#end for
ejeFrec = fs_nueva / N * ((np.arange(N) - N / 2))

noiseLevelsinruido = matlab.semavg(np.array(nivelruido), 501)
#print(noiseLevelsinruido) #-> mas o menos coincide, pero no es demasiado exacto
#print(len(noiseLevelsinruido))
aissupSinRuido = matlab.semavg(np.array(aissup), 101)
#print(aissupSinRuido) -> mas o menos, igual que el anterior
#print(len(aissupSinRuido))
aisinfSinRuido = matlab.semavg(np.array(aisinf), 101)
#print(aisinfSinRuido) -> lo mismo
#print(len(aisinfSinRuido))

niveles = np.vstack((aisinfSinRuido, noiseLevelsinruido, aissupSinRuido))

v = np.linspace(1, 1000, len(niveles[0]))

# Vemos en que canal esta la señal
flagAISinf = 0
flagAISsup = 0

mediainf = np.mean(aisinfSinRuido)  # esto es despues de la media deslizante
#print(mediainf) -> coincide pero ojo
mediasup = np.mean(aissupSinRuido)
#print(mediasup) -> coincide pero ojo

if mediainf > mediasup:
    detec = aisinfSinRuido > noiseLevelsinruido * 10 ** (3 / 10)
    flagAISinf = 1
else:
    detec = aissupSinRuido > noiseLevelsinruido * 10 ** (3 / 10)
    flagAISsup = 1

pulso = matlab.gefh_detect(detec, detec)
#print(pulso) -> coincide

# Detección fina
# Oscilador para centrar la señal:
freq_angular = 2 * np.pi * 25 / 96
t = t = np.arange(len(detec))
OL = np.exp(1j * freq_angular * t)
#print(OL) -> coincide

refinedPulses = []
for ii in range(len(pulso)):
    iniInd = (pulso[ii]["Bin_Inicial"] - 1) * N
    endInd = (pulso[ii]["Bin_Final"] - 1) * N

    # Verificar si la longitud del segmento es mayor que fs_nueva * 0.022
    if endInd - iniInd + 1 > fs_nueva * 0.022:
        # Potencia de ruido estimada en el intervalo de tiempo de interés
        noisePow = np.mean(
            noiseLevelsinruido[pulso[ii]["Bin_Inicial"] - 1 : pulso[ii]["Bin_Final"] - 1]
        )
        #print(noisePow) #-> coincide

        # Adquirimos el tramo de señal de interés y lo pasamos a 48KHz
        z = x_resampled[iniInd:endInd+1]
        #print(len(z))
        #OL = np.exp(
        #    1j * 2 * np.pi * 25 / 96 * np.arange(len(z))
        #)  # Oscilador para centrar la señal
        oscilador = OL[np.mod(np.arange(len(z)), len(OL))]
        #print(oscilador) #-> ya coincide, no estaba bien el rango de z
        if flagAISsup == 1:
            zy = z * np.conj(oscilador)
        else:
            zy = z * oscilador

        # Cargar el filtro de paso bajo
        mat_contents = sio.loadmat("lpf.mat")
        lpf = mat_contents["lpf"].flatten()

        # Filtrar la señal con el filtro de paso bajo
        zfiltrada = lfilter(lpf, 1, zy)
        #print(zfiltrada) #-> coincide

        # Reducir la señal a una frecuencia de muestreo de 24KHz (tomando una de cada dos muestras)
        zfinal = zfiltrada[::2]
        #print(zfinal) #-> coincide

        # Calcular la potencia instantánea
        instPow = matlab.semavg(np.abs(zfinal) ** 2, 31)
        #print(instPow) #-> no coincide

        # Detección
        detection = instPow > noisePow * 10 ** (3 / 10)
        #print(detection) #-> no se

        # Detectar hoppers
        refinedPulses.extend(matlab.gefh_detect(detection, detection))
        #print(refinedPulses) #-> coincide


# hay que arreglar a partir de aqui
"""for i in range(1,dist + 1):
  indiceini = int((i - 1) * N)
  indicefin = int((i - 1) * N + M)-1
  y = x_resampled[indiceini:indicefin]
  wy = wventana[1:]*np.array(y)
"""

# Generar el oscilador para centrar la señal
n = len(detec)
t = np.arange(n)
OL = np.exp(1j * 2 * np.pi * 25 / 96 * t)

for jj in range(len(refinedPulses)):
    iniInd = refinedPulses[jj]["Bin_Inicial"]
    endInd = refinedPulses[jj]["Bin_Final"]
    if endInd - iniInd + 1 > fs_nueva / 2 * 0.022:

        # Aislamos el pulso actual
        instPowPulse = instPow[iniInd-1 : endInd]
        #print(instPowPulse) #-> coincide
        z = zfinal[iniInd-1:endInd]
        #print(z) -> coicide

        # Obtenemos los instantes de comienzo y final del pulso calculando
        # la potencia media en el mismo y viendo los instantes de tiempo
        # donde esta cae por debajo de 3 dB en relacion al valor medio
        meanPow = np.mean(instPowPulse)
        indices = np.where(instPowPulse > meanPow * 10 ** (-3 / 10))[0]
        demodSignal = z[indices]
        #print(demodSignal) #-> coincide

        Samples = demodSignal
        Fs = fs_nueva / 2
        SamplesPerSymbol = 5

        validCRC = 0
        Message = []

        syncCalc = matlab.syncGen(SamplesPerSymbol)

        # Add some debugging prints
        # print("Filtered signal length:", len(result))
        # print("Filtered signal values:", result)

        # Now let's check the correlation using convolution
        syncCorr = convolve(syncCalc, syncCalc[::-1], mode='full')

        # print("Sync correlation length:", len(syncCorr))
        # print("Sync correlation values:", syncCorr)

        # Check for NaN or infinite values in correlation
        if np.any(np.isnan(syncCorr)) or np.any(np.isinf(syncCorr)):
            raise ValueError("Invalid values encountered in correlation.")

        # Finally, let's find the maximum value of the correlation
        if len(syncCorr) > 0:
            max_val = np.max(syncCorr)
        #     print("Maximum correlation value:", max_val)
        # else:
        #     print("Correlation array is empty.")

        syncIdeal = np.angle(syncCalc)

        # Diseño filtro gaussiano
        BT = 0.3
        pulseLength = 2
        gx = matlab.gaussdesign(BT, pulseLength, SamplesPerSymbol)
        
        # Filtrado gaussiano para la cancelación de ISI y cálculo de fase
        rxf = lfilter(gx, [1], demodSignal)
        rxAngles = np.unwrap(np.angle(rxf))

        # Corrección fina de frecuencia: considerar los últimos 5 mínimos y los últimos cinco
        # máximos que ocurren antes del último mínimo
        test = rxAngles[:161]

        maxima = np.where((test[:-2] <= test[1:-1]) & (test[1:-1] >= test[2:]))[0] + 1
        minima = np.where((test[:-2] >= test[1:-1]) & (test[1:-1] <= test[2:]))[0] + 1

        lastMinimum = max(minima)
        maxima = maxima[np.where(maxima < lastMinimum)[0]]

        # Calcular correccion de fase
        numMaxima = min(5, len(maxima))
        xx = maxima[-numMaxima:]
        q = np.polyfit(xx, rxAngles[xx], 1)

        numMinima = min(5, len(minima))
        xx = minima[-numMinima:]
        p = np.polyfit(xx, rxAngles[xx], 1)

        # Correccion de fase hecha
        xx = np.arange(len(rxAngles))
        rxAngles = (
            np.mod(rxAngles - np.polyval((p + q) / 2, xx) + np.pi, 2 * np.pi) - np.pi
        )
        rxAngles = np.unwrap(rxAngles)

        # Encontrar la ubicación del preámbulo mediante correlación
        syncCorr = np.zeros(SamplesPerSymbol * 50)
        syncVector = np.zeros(len(syncIdeal))

        if len(rxAngles) > SamplesPerSymbol * 50 + len(syncIdeal):
            for ii in range(SamplesPerSymbol * 50):
                syncVector = rxAngles[ii : ii + len(syncCalc)]
                syncCorr[ii] = (
                    np.mean(syncIdeal * syncVector)
                    - np.mean(syncIdeal) * np.mean(syncVector)
                ) / (np.std(syncIdeal) * np.std(syncVector))
        else:
            syncCorr[0] = 1

        # Calcular la mejor fase de muestra para tomar decisiones de bits. Si hay
        # más de 1 pico en la secuencia de correlación cuyos niveles son
        # bastante similares al más alto, se tomará el último. Esto se hace debido a que
        # hay algunos bits de aumento gradual que pueden confundirnos cuando se trata de encontrar
        # la posición del preámbulo. Se asume que el último pico más alto
        # está asociado con el preámbulo real.

        maxima = (
            np.where(
                (syncCorr[:-2] <= syncCorr[1:-1]) & (syncCorr[1:-1] >= syncCorr[2:])
            )[0]
            + 1
        )
        
        idx = maxima[
            np.max(
                np.where(
                    np.abs(np.max(syncCorr) - syncCorr[maxima]) < 0.1 * np.max(syncCorr)
                )
            )
        ]

        m = syncCorr[idx]
        print("m", m)
        if m < 0.1:
            continue

        # Codigo en el que se se calculan los bits usando la fase corregida
        # de la que se ha quitado el termino lineal en frecuencia
        samplePhase = int(idx + np.floor(SamplesPerSymbol / 2) + 2)

        abits = np.zeros_like(rxAngles[samplePhase::SamplesPerSymbol])

        ind = np.where(
            np.abs(np.diff(rxAngles[samplePhase::SamplesPerSymbol])) > np.pi / 4
        )[0]

        abits[ind] = 1

        # Buscar los primeros 50 bits para la bandera StartByte 0x7E
        # 0111 1110
        sb = 1
        if len(abits) > 50:
            for ii in range(0, 51):
                if abits[ii : ii + 9].tolist() == [0, 1, 1, 1, 1, 1, 1, 0, 0]:
                    sb = ii + 8

        # Leer el tipo de mensaje y dirigir los bits a la función de decodificación correcta
        msgType = 0
        if len(abits) >= sb + 8:
            bits_reversed = [int(x) for x in abits[sb + 2: sb + 7]][::-1]
            msgType = int("".join(map(str, bits_reversed)), 2)

        print("msg: type", msgType)
        # Seguir la especificación AIS para desempaquetar después de 5 unos consecutivos. Esto desempaquetará todo, incluida la bandera de fin en el mensaje AIS.

        ubits = matlab.aisUnstuff(abits[sb:])
        ubits_padded = matlab.pad_to_nearest_multiple_of_eight(ubits)
        ubits_flipped = matlab.bitarray_flip_bytes(ubits_padded)
        ubits_string = matlab.bitarray_to_string(ubits_flipped)
        message = get_message(msgType, ubits_string)

        if matlab.get_checksum(ubits, message.checksum):
            
            print(message.json())
        else:
            print(f"Message Checksym Failed")
