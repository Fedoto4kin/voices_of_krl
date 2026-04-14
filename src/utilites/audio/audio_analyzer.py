import threading
import time
import numpy as np
import soundfile as sf


class AudioAnalyzer(threading.Thread):
    def __init__(self, filepath, callback, bars=10, interval=0.04):
        super().__init__()
        self.filepath = filepath
        self.callback = callback
        self.bars = bars
        self.interval = interval
        self.running = False
        self.samples, self.samplerate = sf.read(filepath, dtype="float32")
        if len(self.samples.shape) == 2:
            self.samples = self.samples.mean(axis=1)
        self.pos = 0
        self.step = int(self.samplerate * self.interval)

    def run(self):
        self.running = True
        while self.running and self.pos < len(self.samples):
            chunk = self.samples[self.pos:self.pos + self.step]
            self.pos += self.step

            if len(chunk) == 0:
                break
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            fft = np.abs(np.fft.rfft(chunk))
            fft = fft[:self.bars]
            fft = fft / (np.max(fft) + 1e-6)
            self.callback(rms, fft)
            time.sleep(self.interval)

    def stop(self):
        self.running = False
