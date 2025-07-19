#!/usr/bin/env python3
"""
Text-to-speech utility for Claude Code hooks.
"""

import os
import sys
import platform

def speak(message):
    """Speak the given message using system text-to-speech."""
    system = platform.system().lower()
    
    try:
        if system == "darwin":  # macOS
            os.system(f'say "{message}"')
        elif system == "linux":
            # Try different Linux TTS options
            if os.system('which espeak > /dev/null 2>&1') == 0:
                os.system(f'espeak "{message}"')
            elif os.system('which festival > /dev/null 2>&1') == 0:
                os.system(f'echo "{message}" | festival --tts')
            else:
                print(f"No TTS system found on Linux. Message: {message}")
        elif system == "windows":
            # For Windows, using PowerShell's speech synthesis
            import subprocess
            powershell_cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{message}\')"'
            subprocess.call(powershell_cmd, shell=True)
        else:
            print(f"Unsupported platform for TTS: {system}")
    except Exception as e:
        print(f"Error using TTS: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
        speak(message)
    else:
        print("Usage: python speech.py \"Your message here\"")
