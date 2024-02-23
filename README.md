# Assemblyai Python Library with sounddevice
## (Instead of pyaudio)

After a serios of fight in making pyaudio and portaudio in Mac M1 chip, for AssemblyAI, I finally decided to write code in some other library which is sounddevice, working fine in Mac without any additional external libraries.

Exteted the class of Assemblyai Extras, MicrophoneStream, to CustomMicrophoneStream, and which uses sounddevice as the audio interfacing library instead of pyaudio
