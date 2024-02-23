# AssemblyAI Python Integration with SoundDevice

## Overview

**Transitioning from PyAudio to SoundDevice for macOS M1 Compatibility**

After encountering numerous challenges with PyAudio and PortAudio on the macOS M1 chip, particularly in the context of integrating with AssemblyAI, I decided to explore alternative solutions. My journey led me to adopt SoundDevice, a library that seamlessly operates on macOS without the need for additional external libraries. This decision has significantly streamlined the development process, offering a more stable and efficient audio interfacing solution.

## Custom Implementation

### Extending AssemblyAI's MicrophoneStream with CustomMicrophoneStream

To maintain compatibility with AssemblyAI and leverage SoundDevice's capabilities, I developed `CustomMicrophoneStream`. This class extends AssemblyAI's `extras.MicrophoneStream`, replacing PyAudio with SoundDevice for audio capture and processing. This custom implementation not only facilitates a smoother integration with AssemblyAI's real-time transcription services but also ensures compatibility with macOS M1 chips, circumventing the limitations previously encountered with PyAudio.

### Key Features

- **MacOS M1 Compatibility**: Fully compatible with macOS M1, eliminating the need for PyAudio or PortAudio.
- **Seamless AssemblyAI Integration**: Designed to integrate effortlessly with AssemblyAI, supporting real-time audio transcription without modifying the core workflow.
- **SoundDevice as the Core Audio Library**: Leverages SoundDevice for audio streaming, providing a robust and efficient audio capture mechanism.

## Getting Started

To utilize `CustomMicrophoneStream` in your project, ensure you have SoundDevice installed:

```bash
pip install sounddevice
```

```python

    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    # Initialize your custom microphone stream
    microphone_stream = CustomMicrophoneStream()
    

    transcriber = aai.RealtimeTranscriber(
        on_data=on_data,
        on_error=on_error,
        sample_rate=44_100,
        )
    
    transcriber.connect()

    # To check each chuck of audio uncomment the following lines
    # mic_thread = threading.Thread(target=microphone_stream.run)
    # mic_thread.start()

    try:
        print("Starting transcription stream.")
        transcriber.stream(microphone_stream)
    finally:
        microphone_stream.close()
        #mic_thread.join()

```

## The New Class

```python
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
```

# A Set of issues
##  I have faced in Mac M1 during the pyaudio and portaudio configuration.


```bash
1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for pyaudio
Failed to build pyaudio
```

```bash
An error occured: Could not connect to the real-time service: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1007)
Could not import the PyAudio C module 'pyaudio._portaudio'.
Traceback (most recent call last):
  File "/Users/sajithmr/coding/assemblyai/venv/lib/python3.10/site-packages/assemblyai/extras.py", line 37, in __init__
    import pyaudio
  File "/Users/sajithmr/coding/assemblyai/venv/lib/python3.10/site-packages/pyaudio/__init__.py", line 111, in <module>
    import pyaudio._portaudio as pa
ImportError: dlopen(/Users/sajithmr/coding/assemblyai/venv/lib/python3.10/site-packages/pyaudio/_portaudio.cpython-310-darwin.so, 0x0002): symbol not found in flat namespace '_PaMacCore_SetupChannelMap'
```

### Fix
```python
import certifi
import os

os.environ['SSL_CERT_FILE'] = certifi.where()

```

```bash

||PaMacCore (AUHAL)|| AUHAL component not found.Traceback (most recent call last):
  File "app.py", line 18, in <module>
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
  File "/Users/sajithmr/miniconda3/envs/myconda/lib/python3.8/site-packages/pyaudio/__init__.py", line 639, in open
    stream = PyAudio.Stream(self, *args, **kwargs)
  File "/Users/sajithmr/miniconda3/envs/myconda/lib/python3.8/site-packages/pyaudio/__init__.py", line 441, in __init__
    self._stream = pa.open(**arguments)
OSError: [Errno -9999] Unanticipated host error

```


