import sounddevice as sd
from threading import Thread
import assemblyai as aai
import os
import certifi
import threading
from dotenv import load_dotenv
load_dotenv()

from CustomMicrophoneStream import CustomMicrophoneStream

os.environ['SSL_CERT_FILE'] = certifi.where()

# Print available devices
#print(sd.query_devices())

def on_data(transcript: aai.RealtimeTranscript):
  if not transcript.text:
    #print("No data received")
    return

  if isinstance(transcript, aai.RealtimeFinalTranscript):
    #print ("isInstance")
    print(transcript.text, end="\r\n")
  else:
    #print ("NotisInstance")
    print(transcript.text, end="\r")

def on_error(error: aai.RealtimeError):
  print("An error occured:", error)

# Usage example
if __name__ == "__main__":
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
