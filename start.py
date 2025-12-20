#!/usr/bin/env python3
"""Start the FastAPI server with Railway's PORT variable"""
import os
import sys

port = os.getenv('PORT', '8000')
os.system(f'uvicorn src.api.main:app --host 0.0.0.0 --port {port}')
