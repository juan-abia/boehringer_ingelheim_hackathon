#!/bin/bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 80
