"""Convenience command: python train_model.py"""
from whatsapp import train_and_select_model
import json

if __name__ == "__main__":
    result = train_and_select_model()
    print(json.dumps(result, indent=2))
