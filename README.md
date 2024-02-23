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
