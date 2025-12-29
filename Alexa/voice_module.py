"""
Voice Assistant Module
Integrates OpenWakeWord, Whisper, and Piper TTS for voice interaction
"""
import numpy as np
import pyaudio
import threading
import queue
import time
from openwakeword.model import Model
import whisper
import subprocess
import tempfile
import os
import wave
import collections

class VoiceAssistant:
    def __init__(self, callback=None):
        """
        Initialize the voice assistant
        
        Args:
            callback: Function to call when a command is received (receives text, returns response text)
        """
        self.callback = callback
        self.is_running = False
        self.is_listening = False
        
        # Audio settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1280  # 80ms chunks for OpenWakeWord
        
        # Initialize components
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # OpenWakeWord model
        print("Loading wake word model...")
        self.oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        
        # Whisper model (using smaller model for faster processing)
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Piper TTS settings
        self.piper_model_path = None
        self.piper_config_path = None
        
        # Audio queues
        self.audio_queue = queue.Queue()
        self.recording_buffer = []
        
        # Voice Activity Detection (VAD) settings
        self.silence_threshold = 500  # RMS threshold for silence
        self.silence_duration = 1.5  # Seconds of silence to stop recording
        self.max_recording_duration = 10  # Maximum recording time in seconds
        self.min_recording_duration = 0.5  # Minimum recording time in seconds
        
        # Wake word detection settings
        self.wake_word_threshold = 0.6  # Higher threshold to reduce false positives
        self.wake_word_cooldown = 3.0  # Seconds to wait after detection before detecting again
        self.last_wake_word_time = 0
        
        # Status
        self.status = "idle"
        self.status_callback = None
        self.audio_level_callback = None
        
        # Recording state
        self.recording_start_time = 0
        self.silence_start_time = 0
        self.is_speech_detected = False
        
    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def set_audio_level_callback(self, callback):
        """Set callback for audio level updates during speech playback"""
        self.audio_level_callback = callback
        
    def update_status(self, status):
        """Update status and notify callback"""
        self.status = status
        if self.status_callback:
            self.status_callback(status)
    
    def set_piper_model(self, model_path, config_path=None):
        """Set Piper TTS model paths"""
        self.piper_model_path = model_path
        self.piper_config_path = config_path
        
    def start(self):
        """Start the voice assistant"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Open audio stream
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self._audio_callback
        )
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_audio, daemon=True)
        self.processing_thread.start()
        
        self.stream.start_stream()
        self.update_status("listening_for_wake_word")
        print("Voice assistant started. Say 'Hey Jarvis' to activate.")
        
    def stop(self):
        """Stop the voice assistant"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        self.update_status("idle")
        print("Voice assistant stopped.")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for incoming audio"""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def _calculate_rms(self, audio_data):
        """Calculate RMS (Root Mean Square) of audio data for VAD"""
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(audio_array**2))
        return rms
        
    def _process_audio(self):
        """Process audio stream for wake word detection and recording"""
        while self.is_running:
            try:
                # Get audio chunk
                audio_data = self.audio_queue.get(timeout=0.1)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                if not self.is_listening:
                    # Listen for wake word with cooldown
                    current_time = time.time()
                    if current_time - self.last_wake_word_time > self.wake_word_cooldown:
                        prediction = self.oww_model.predict(audio_array)
                        
                        # Check if wake word detected
                        for mdl_name, score in prediction.items():
                            if score > self.wake_word_threshold:
                                print(f"Wake word detected! (confidence: {score:.2f})")
                                self.last_wake_word_time = current_time
                                self.update_status("wake_word_detected")
                                self._start_recording()
                                break
                else:
                    # Record audio for command with VAD
                    self.recording_buffer.append(audio_data)
                    
                    # Calculate RMS for voice activity detection
                    rms = self._calculate_rms(audio_data)
                    current_time = time.time()
                    recording_duration = current_time - self.recording_start_time
                    
                    # Detect speech
                    if rms > self.silence_threshold:
                        self.is_speech_detected = True
                        self.silence_start_time = 0  # Reset silence timer
                    else:
                        # Silence detected
                        if self.is_speech_detected:
                            if self.silence_start_time == 0:
                                self.silence_start_time = current_time
                            else:
                                silence_duration = current_time - self.silence_start_time
                                
                                # Stop recording if silence duration exceeded and minimum recording met
                                if (silence_duration >= self.silence_duration and 
                                    recording_duration >= self.min_recording_duration):
                                    print(f"Silence detected after {recording_duration:.1f}s, stopping recording")
                                    self._stop_recording()
                    
                    # Stop recording if max duration exceeded
                    if recording_duration >= self.max_recording_duration:
                        print(f"Max recording duration reached ({self.max_recording_duration}s)")
                        self._stop_recording()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
                
    def _start_recording(self):
        """Start recording user command"""
        self.is_listening = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        self.silence_start_time = 0
        self.is_speech_detected = False
        self.update_status("recording")
        print("Listening for command...")
        
    def _stop_recording(self):
        """Stop recording and process command"""
        if not self.is_listening:
            return
            
        self.is_listening = False
        self.update_status("processing")
        
        # Check if we have enough audio
        if len(self.recording_buffer) < 5:  # At least 5 chunks
            print("Recording too short, ignoring")
            self.update_status("listening_for_wake_word")
            return
        
        print("Processing command...")
        
        # Convert recorded audio to numpy array
        audio_data = b''.join(self.recording_buffer)
        
        # Save to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
            
            # Write WAV file
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data)
        
        try:
            # Transcribe with Whisper
            print("Transcribing audio...")
            result = self.whisper_model.transcribe(
                temp_path, 
                language="en",
                fp16=False,  # Use FP32 for CPU
                verbose=False
            )
            command_text = result["text"].strip()
            
            print(f"Recognized: '{command_text}'")
            
            # Only process if we got meaningful text
            if command_text and len(command_text) > 2:
                # Get response from callback
                if self.callback:
                    response_text = self.callback(command_text)
                    print(f"Response: {response_text}")
                    
                    # Speak response if Piper is configured
                    if self.piper_model_path:
                        self._speak(response_text)
                    else:
                        print("(Piper TTS not configured, skipping speech output)")
                else:
                    print("No callback set for processing command")
            else:
                print("No meaningful command recognized")
                
        except Exception as e:
            print(f"Error transcribing audio: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
        self.update_status("listening_for_wake_word")
        
    def _speak(self, text):
        """Convert text to speech using Piper and play it"""
        if not self.piper_model_path:
            return
            
        self.update_status("speaking")
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                output_path = temp_output.name
            
            # Run Piper TTS
            cmd = [
                'piper',
                '--model', self.piper_model_path,
                '--output_file', output_path
            ]
            
            if self.piper_config_path:
                cmd.extend(['--config', self.piper_config_path])
            
            # Send text to Piper via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            process.communicate(input=text.encode('utf-8'))
            
            # Play audio file
            if os.path.exists(output_path):
                self._play_audio_file(output_path)
                os.unlink(output_path)
            else:
                print("Failed to generate speech")
                
        except Exception as e:
            print(f"Error generating speech: {e}")
        finally:
            self.update_status("listening_for_wake_word")
            
    def _play_audio_file(self, filepath):
        """Play an audio file and emit audio levels for visualization"""
        try:
            # Read WAV file
            with wave.open(filepath, 'rb') as wf:
                # Open output stream
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # Play audio and calculate levels
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    
                    # Calculate audio level for visualization
                    if self.audio_level_callback and len(data) > 0:
                        try:
                            # Convert to numpy array and calculate RMS
                            audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                            rms = np.sqrt(np.mean(audio_array**2))
                            
                            # Normalize to 0-1 range (assuming 16-bit audio)
                            normalized_level = min(rms / 3000.0, 1.0)
                            
                            # Emit audio level
                            self.audio_level_callback(normalized_level)
                        except Exception as e:
                            pass  # Silently ignore audio level calculation errors
                    
                    data = wf.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def __del__(self):
        """Cleanup"""
        self.stop()
        if hasattr(self, 'audio'):
            self.audio.terminate()
