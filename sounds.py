"""
Sound effects for the Robotic Microscope GUI
Generates and plays simple audio cues using numpy + WAV + aplay
"""

import os
import wave
import struct
import threading
import subprocess
import numpy as np

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound_cache")


def _ensure_sounds_dir():
    os.makedirs(SOUNDS_DIR, exist_ok=True)


def _generate_wav(filename: str, samples: np.ndarray, sample_rate: int = 44100):
    """Write a numpy float array (-1.0 to 1.0) to a 16-bit WAV file"""
    _ensure_sounds_dir()
    filepath = os.path.join(SOUNDS_DIR, filename)
    if os.path.exists(filepath):
        return filepath
    
    # Convert to 16-bit PCM
    audio_16bit = (samples * 32767).astype(np.int16)
    
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_16bit.tobytes())
    
    return filepath


def _generate_startup_chime():
    """Generate a pleasant 3-note ascending chime"""
    sample_rate = 44100
    
    # Three ascending notes: C5, E5, G5 (major chord arpeggio)
    freqs = [523.25, 659.25, 783.99]
    note_duration = 0.18
    pause_duration = 0.06
    fade_duration = 0.08
    
    samples = np.array([], dtype=np.float64)
    
    for i, freq in enumerate(freqs):
        t = np.linspace(0, note_duration, int(sample_rate * note_duration), endpoint=False)
        # Sine wave with gentle harmonics for warmth
        note = 0.7 * np.sin(2 * np.pi * freq * t)
        note += 0.2 * np.sin(2 * np.pi * freq * 2 * t)  # Octave harmonic
        note += 0.1 * np.sin(2 * np.pi * freq * 3 * t)  # Fifth harmonic
        
        # Apply envelope (attack + decay)
        attack = int(sample_rate * 0.01)
        decay_start = int(sample_rate * (note_duration - fade_duration))
        envelope = np.ones_like(t)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[decay_start:] = np.linspace(1, 0, len(envelope[decay_start:]))
        note *= envelope
        
        samples = np.concatenate([samples, note])
        
        # Add pause between notes (except after last)
        if i < len(freqs) - 1:
            pause = np.zeros(int(sample_rate * pause_duration))
            samples = np.concatenate([samples, pause])
    
    # Final sustain on last note
    t_sustain = np.linspace(0, 0.3, int(sample_rate * 0.3), endpoint=False)
    sustain = 0.5 * np.sin(2 * np.pi * freqs[-1] * t_sustain)
    sustain += 0.15 * np.sin(2 * np.pi * freqs[-1] * 2 * t_sustain)
    decay_env = np.exp(-t_sustain * 8)
    sustain *= decay_env
    samples = np.concatenate([samples, sustain])
    
    # Normalize
    samples = samples / np.max(np.abs(samples)) * 0.8
    
    return _generate_wav("startup_chime.wav", samples, sample_rate)


def _generate_warning_beep():
    """Generate a short warning beep (two quick descending tones)"""
    sample_rate = 44100
    
    # Two quick descending tones
    freqs = [880, 660]
    note_duration = 0.08
    pause_duration = 0.03
    
    samples = np.array([], dtype=np.float64)
    
    for i, freq in enumerate(freqs):
        t = np.linspace(0, note_duration, int(sample_rate * note_duration), endpoint=False)
        note = 0.8 * np.sin(2 * np.pi * freq * t)
        note += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        
        # Sharp envelope
        attack = int(sample_rate * 0.005)
        decay_start = int(sample_rate * (note_duration - 0.02))
        envelope = np.ones_like(t)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[decay_start:] = np.linspace(1, 0, len(envelope[decay_start:]))
        note *= envelope
        
        samples = np.concatenate([samples, note])
        
        if i < len(freqs) - 1:
            pause = np.zeros(int(sample_rate * pause_duration))
            samples = np.concatenate([samples, pause])
    
    # Normalize
    samples = samples / np.max(np.abs(samples)) * 0.7
    
    return _generate_wav("warning_beep.wav", samples, sample_rate)


def _play_wav(filepath: str):
    """Play a WAV file asynchronously using aplay"""
    def _play():
        try:
            subprocess.run(
                ["aplay", "-q", filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
        except Exception:
            pass
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()


# Pre-generate sounds on import
_startup_chime_path = None
_warning_beep_path = None


def play_startup_chime():
    """Play the startup chime sound"""
    global _startup_chime_path
    if _startup_chime_path is None:
        _startup_chime_path = _generate_startup_chime()
    _play_wav(_startup_chime_path)


def play_warning_beep():
    """Play the warning beep sound"""
    global _warning_beep_path
    if _warning_beep_path is None:
        _warning_beep_path = _generate_warning_beep()
    _play_wav(_warning_beep_path)
