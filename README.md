# RDPMS Anomaly Detection — Setup Guide

## Requirements
- Python 3.9+ (download from python.org)
- The sensor laptop must be on the same network

## One-time Setup

1. Open terminal in this folder
2. Create virtual environment:
   python -m venv rdpms_env

3. Activate it:
   Windows:   rdpms_env\Scripts\activate
   Linux/Mac: source rdpms_env/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

## Before Running — Update the IP

Open client.py and change this line to the sensor laptop's IP:
   HOST = '172.20.10.2'   ← change this

To find the sensor laptop's IP:
   Windows: run `ipconfig` in cmd → look for IPv4 Address

## Run

   python client.py

The script will:
- Collect 200 readings to learn normal baseline
- Then flag anomalies in real time automatically