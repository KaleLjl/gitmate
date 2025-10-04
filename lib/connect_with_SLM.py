"""
SLM Connection Module
Connects to LM Studio local server
"""

import requests
from typing import Optional
from pathlib import Path

class LMStudioConnector:
    """Connect to LM Studio local server"""
    
    def __init__(self, model_name: str = "llama-3.2-1b", host: str = "localhost", port: int = 1234):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/v1/chat/completions"
    
    def check_connection(self) -> bool:
        """Check if LM Studio server is running"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def send_message(self, message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Send message to LM Studio and return response"""
        if not self.check_connection():
            raise ConnectionError("LM Studio server is not running. Start LM Studio and load a model.")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to LM Studio: {e}")
        except KeyError as e:
            raise ValueError(f"Unexpected response format from LM Studio: {e}")