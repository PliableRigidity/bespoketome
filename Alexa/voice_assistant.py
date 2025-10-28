"""
Voice Assistant with Wake Word Detection, STT, and TTS
Uses: openwakeword, faster_whisper, piper
"""
import time
import queue
import threading
import numpy as np
import pyaudio
import tempfile
import os
from faster_whisper import WhisperModel
from openwakeword import Model
from dispatcher import handle_user_text
from config import (
    WAKE_WORD_MODEL,
    WAKE_WORD_SENSITIVITY,
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    PIPER_MODEL_PATH,
    PIPER_USE_CUDA,
    AUDIO_CHANNELS,
    AUDIO_RATE,
    AUDIO_CHUNK,
    AUDIO_DEVICE_INDEX
)

class VoiceAssistant:
    def __init__(self):
        print("🎤 Initializing Voice Assistant...")
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.rate = AUDIO_RATE
        self.chunk = AUDIO_CHUNK
        self.channels = AUDIO_CHANNELS
        
        # Initialize Wake Word Model
        print("🔊 Loading wake word model...")
        self.wake_word_model = Model(wakeword_models=[WAKE_WORD_MODEL])
        print(f"✅ Wake word model loaded: {WAKE_WORD_MODEL}")
        
        # Initialize Whisper (STT)
        print(f"🎤 Loading Whisper model ({WHISPER_MODEL})...")
        self.whisper_model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print("✅ Whisper model loaded")
        
        # Initialize Piper (TTS) - lazy load
        self.piper_voice = None
        self.piper_model_path = PIPER_MODEL_PATH
        self.piper_use_cuda = PIPER_USE_CUDA
        print("✅ Piper TTS will be loaded on first use")
        
        # State
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
    def play_sound(self, file_path):
        """Play a sound file (optional confirmation beep)."""
        import pygame
        try:
            pygame.mixer.init()
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except Exception as e:
            print(f"Could not play sound: {e}")
    
    def speak(self, text: str):
        """Convert text to speech using Piper and play it."""
        print(f"🗣️ Speaking: {text[:50]}...")
        try:
            # Lazy load Piper if not loaded
            if self.piper_voice is None:
                print("🗣️ Loading Piper TTS model...")
                from piper.voice import PiperVoice
                self.piper_voice = PiperVoice.load(self.piper_model_path, config_path=None, use_cuda=self.piper_use_cuda)
            
            # Generate audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_wav = tmp_file.name
            
            self.piper_voice.synthesize(text, output_file=temp_wav)
            
            # Play the audio file using a simple method
            import wave
            import struct
            
            with wave.open(temp_wav, 'rb') as wf:
                params = wf.getparams()
                frames = wf.readframes(wf.getnframes())
                
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=1024
                )
                
                stream.write(frames)
                stream.stop_stream()
                stream.close()
            
            # Clean up
            os.unlink(temp_wav)
            print("✅ Finished speaking")
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
    
    def listen_for_wake_word(self, frames):
        """Detect wake word in audio frames."""
        ndata = np.frombuffer(frames, dtype=np.int16)
        prediction = self.wake_word_model.predict(ndata)
        
        for mdl in self.wake_word_model.models.keys():
            if prediction[mdl]["probability"] > WAKE_WORD_SENSITIVITY:
                return True
        return False
    
    def record_voice_command(self, duration=5):
        """Record voice command from microphone."""
        print(f"🎤 Listening for {duration} seconds...")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=AUDIO_DEVICE_INDEX,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        audio_data = b''.join(frames)
        print("✅ Recording complete")
        return audio_data
    
    def transcribe_audio(self, audio_bytes):
        """Convert speech to text using Whisper."""
        print("🧠 Transcribing with Whisper...")
        try:
            # Save to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                import wave
                wf = wave.open(tmp_file.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.rate)
                wf.writeframes(audio_bytes)
                wf.close()
                temp_wav = tmp_file.name
            
            segments, info = self.whisper_model.transcribe(
                temp_wav,
                beam_size=5,
                vad_filter=True
            )
            
            # Clean up
            os.unlink(temp_wav)
            
            text = "".join([seg.text for seg in segments]).strip()
            print(f"📝 Transcription: {text}")
            print(f"🌍 Detected language: {info.language} (confidence: {info.language_probability:.2f})")
            
            return text
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def process_command(self, text: str):
        """Process user command through dispatcher."""
        print(f"🤔 Processing: {text}")
        try:
            response = handle_user_text(text)
            return response
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return "Sorry, I encountered an error."
    
    def wake_word_loop(self):
        """Main loop that listens for wake word."""
        print("\n🎧 Starting wake word detection...")
        print("Say the wake word to start!")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=AUDIO_DEVICE_INDEX,
            frames_per_buffer=self.chunk
        )
        
        frames_buffer = []
        
        try:
            while True:
                data = stream.read(self.chunk)
                
                # Check for wake word
                if self.listen_for_wake_word(data):
                    print("\n🔔 WAKE WORD DETECTED!")
                    stream.stop_stream()
                    stream.close()
                    
                    # Record user command
                    audio_command = self.record_voice_command(duration=5)
                    
                    # Transcribe
                    text = self.transcribe_audio(audio_command)
                    
                    if text:
                        # Process and respond
                        response = self.process_command(text)
                        self.speak(response)
                    
                    # Restart listening for wake word
                    stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        input_device_index=AUDIO_DEVICE_INDEX,
                        frames_per_buffer=self.chunk
                    )
                    
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        finally:
            stream.stop_stream()
            stream.close()
            self.audio.terminate()
    
    def run(self):
        """Start the voice assistant."""
        try:
            self.wake_word_loop()
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'audio'):
            self.audio.terminate()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()

