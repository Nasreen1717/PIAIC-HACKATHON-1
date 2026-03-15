# Voice command from Whisper transcription
# Represents a transcribed audio input with confidence and metadata

string id                           # Unique identifier (UUID)
builtin_interfaces/Time timestamp   # When audio was captured
string transcript                   # Transcribed text from Whisper
float64 confidence_score            # Whisper confidence (0.0-1.0)
float64 duration_seconds            # Audio duration in seconds
string language                     # Detected language (default: "en")
string model_version                # Whisper model used (base, small, medium, large)
string raw_audio_path               # Optional path to WAV file for debugging
