import sounddevice as sd
import numpy as np
import queue
import wave

class CustomMicrophoneStream:
    
    def __init__(self, sample_rate=44100, chunk_size=4410, file_duration=5):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.file_duration = file_duration
        self.audio_buffer = queue.Queue()
        self.frames_written = 0
        self.file_index = 0
        self.stream = sd.InputStream(callback=self.audio_callback, 
                                     samplerate=self.sample_rate, 
                                     channels=1, 
                                     blocksize=self.chunk_size)
        self.stream.start()
        self._open = True  # Initialize the _open attribute
        print("Audio stream started.")

        self.prepare_new_file()

    def prepare_new_file(self):
        self.current_file = wave.open(f"part_{self.file_index}.wav", 'wb')
        self.current_file.setnchannels(1)
        self.current_file.setsampwidth(2)  # Assuming 16-bit audio
        self.current_file.setframerate(self.sample_rate)
        self.frames_written = 0
        self.file_index += 1


    def audio_callback(self, indata, frames, time, status):
        
        if status:
            print(f"Stream status: {status}")
        # Flatten the array and convert it to bytes
        audio_bytes = (indata * 32767).astype(np.int16).tobytes()
        #audio_bytes = indata.flatten().tobytes()
        self.audio_buffer.put(audio_bytes)
        #print(f"Audio callback: Buffer size is now {self.audio_buffer.qsize()} chunks.")

    def write_to_file(self):
        
        while not self.audio_buffer.empty():
            data = self.audio_buffer.get()
            self.current_file.writeframes(data)
            self.frames_written += len(data)
            
            # Check if it's time to start a new file
            if self.frames_written >= self.sample_rate * self.file_duration:
                self.current_file.close()
                self.prepare_new_file()

    def read(self, size):
        # Read size bytes. If not enough data is available, block until enough is available.
        requested_frames = size // 2  # 2 bytes per frame (16-bit audio)
        frames_to_deliver = b''
        while len(frames_to_deliver) < size:
            frames_to_deliver += self.audio_buffer.get()
        #print(f"Read {len(frames_to_deliver)} bytes from buffer.")
        return frames_to_deliver[:size]
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._open:
            # Implement fetching the next chunk of audio data. You might need to adjust this logic.
            try:
                data = self.read(self.chunk_size)
                if data:
                    return data
                else:
                    # End of data or handle accordingly.
                    raise StopIteration
            except queue.Empty:
                # End of data or handle accordingly.
                raise StopIteration
        else:
            # Stream is closed, stop iteration.
            raise StopIteration


    def close(self):
        self.stream.stop()
        self.stream.close()
        self._open = False
        print("Audio stream closed.")
        self.current_file.close()


    def run(self):
        try:
            while self._open:
                self.write_to_file()
        finally:
            self.close()