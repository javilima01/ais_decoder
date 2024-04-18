from rtlsdr import RtlSdr
import pandas as pd
import numpy as np
from threading import Semaphore, Thread
aux_samples = Semaphore(1)

samples = np.array([], np.complex_)
def add_samples(iq, context):
    global samples
    aux_samples.acquire()
    samples = np.concatenate((samples, iq))
    aux_samples.release()

def read_samples():
    sdr.read_samples_async(add_samples)

if __name__ == "__main__":
    import time
    sdr = RtlSdr()
    
    samples_thread = Thread(target=read_samples)
    samples_thread.start()

    print("Started sleeping")
    time.sleep(10)
    print("Finished sleeping")
    
    sdr.cancel_read_async()
    samples_thread.join()

    df = pd.DataFrame({'real': samples.real, 'imaginary': samples.imag})
    df.to_csv('ais_signals.csv', mode='a', index=False)