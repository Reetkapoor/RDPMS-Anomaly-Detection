import socket
import numpy as np
from sklearn.ensemble import IsolationForest
import time

# ── Config ────────────────────────────────────────────────
HOST = '172.20.10.2'
PORT = 5000
WARMUP_SAMPLES = 200
COLUMNS = ['sensor_1', 'sensor_2']

# ── Connect ───────────────────────────────────────────────
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Connected to sensor stream...")
print(f"Collecting {WARMUP_SAMPLES} readings to learn normal baseline...\n")

# ── State ─────────────────────────────────────────────────
warmup_buffer = []
model = None
is_trained = False
leftover = ""

try:
    while True:
        raw = client.recv(1024).decode()
        if not raw:
            print("Stream ended.")
            break

        # ── Fix: handle both \n and \r\n line endings ─────
        raw = leftover + raw
        lines = raw.splitlines()  # handles \n, \r\n, \r all correctly

        # check if last char was a line ending (complete line) or not
        if raw[-1] in ('\n', '\r'):
            leftover = ""
        else:
            leftover = lines[-1]   # incomplete last line, save for next chunk
            lines = lines[:-1]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # ── Parse ─────────────────────────────────────
            try:
                values = [float(x) for x in line.split(',')]
                if len(values) != len(COLUMNS):
                    continue
            except ValueError:
                continue

            # ── Phase 1: Warmup ───────────────────────────
            if not is_trained:
                warmup_buffer.append(values)
                # fixed: use print with newline so you can see progress
                print(f"  Warmup [{len(warmup_buffer)}/{WARMUP_SAMPLES}]: {values}")

                if len(warmup_buffer) >= WARMUP_SAMPLES:
                    X = np.array(warmup_buffer)
                    model = IsolationForest(
                        n_estimators=100,
                        contamination=0.05,
                        random_state=42
                    )
                    model.fit(X)
                    is_trained = True
                    print(f"\n✅ Model trained on {WARMUP_SAMPLES} real readings. Detecting now...\n")

            # ── Phase 2: Detect ───────────────────────────
            else:
                x = np.array(values).reshape(1, -1)
                score = model.decision_function(x)[0]
                pred = model.predict(x)[0]
                timestamp = time.strftime('%H:%M:%S')

                if pred == -1:
                    print(f"[{timestamp}] 🚨 ANOMALY  | {dict(zip(COLUMNS, values))} | score: {score:.4f}")
                else:
                    print(f"[{timestamp}] ✅ Normal   | {dict(zip(COLUMNS, values))} | score: {score:.4f}")

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    client.close()   # always close cleanly so reconnect works next time
    print("Socket closed.")