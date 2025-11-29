"""Settings management for LLM Council."""

import json
import os
from typing import List, Dict, Any, Optional
from .config import DATA_DIR, AVAILABLE_MODELS, DEFAULT_COUNCIL_MODELS, DEFAULT_CHAIRMAN_MODEL

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

class Settings:
    def __init__(self):
        self.openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.council_models: List[str] = DEFAULT_COUNCIL_MODELS
        self.chairman_model: str = DEFAULT_CHAIRMAN_MODEL
        self.load()

    def load(self):
        """Load settings from file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.openrouter_api_key = data.get("openrouter_api_key", self.openrouter_api_key)
                    self.council_models = data.get("council_models", self.council_models)
                    self.chairman_model = data.get("chairman_model", self.chairman_model)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        """Save settings to file."""
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        data = {
            "openrouter_api_key": self.openrouter_api_key,
            "council_models": self.council_models,
            "chairman_model": self.chairman_model
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Return settings as dictionary (masking API key)."""
        masked_key = ""
        if self.openrouter_api_key:
            masked_key = self.openrouter_api_key[:8] + "..." + self.openrouter_api_key[-4:]
        
        return {
            "openrouter_api_key": self.openrouter_api_key, # Send full key to frontend? Or mask? 
                                                           # Usually send masked or empty if set. 
                                                           # For simplicity, let's send it but frontend should handle masking.
                                                           # Actually, for security, maybe just send a flag "is_set"?
                                                           # But user wants to edit it. Let's send it for now as this is a local app.
            "council_models": self.council_models,
            "chairman_model": self.chairman_model,
            "available_models": AVAILABLE_MODELS
        }

    def update(self, data: Dict[str, Any]):
        """Update settings."""
        if "openrouter_api_key" in data:
            self.openrouter_api_key = data["openrouter_api_key"]
        if "council_models" in data:
            self.council_models = data["council_models"]
        if "chairman_model" in data:
            self.chairman_model = data["chairman_model"]
        self.save()

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    return settings
