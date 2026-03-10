#!/bin/sh

pip install -r requirements.txt
uvicorn app.main:app --reload
