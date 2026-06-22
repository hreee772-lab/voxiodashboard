import httpx
import base64
from app.core.config import settings

class SarvamService:
    def __init__(self):
        self.api_key = settings.SARVAM_API_KEY
        self.stt_url = "https://api.sarvam.ai/speech-to-text"
        self.tts_url = "https://api.sarvam.ai/text-to-speech"

    async def speech_to_text(self, audio_bytes: bytes) -> str:
        try:
            headers = {
                "api-subscription-key": self.api_key
            }
            files = {
                "file": ("audio.wav", audio_bytes, "audio/wav")
            }
            data = {
                "model": "saarika:v2.5",
                "language_code": "en-IN"
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.stt_url,
                    headers=headers,
                    files=files,
                    data=data
                )
                print(f"Sarvam STT Response: {response.status_code} {response.text}")
                if response.status_code == 200:
                    result = response.json()
                    return result.get("transcript", "")
                else:
                    print(f"Sarvam STT Error: {response.status_code} {response.text}")
                    return ""
        except Exception as e:
            print(f"Sarvam STT Exception: {e}")
            return ""

    async def text_to_speech(self, text: str) -> bytes:
        if not self.api_key:
            print("SARVAM_API_KEY not configured")
            return b""
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "target_language_code": "en-IN",
            "text": text,
            "speaker": "meera",
            "model": "bulbul:v3"
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tts_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                audios = result.get("audios", [])
                if audios:
                    return base64.b64decode(audios[0])
                return b""
        except Exception as e:
            print(f"Sarvam TTS Error: {e}")
            return b""

sarvam_service = SarvamService()
