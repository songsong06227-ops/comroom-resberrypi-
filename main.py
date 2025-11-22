# main.py

from max30102_driver import MAX30102
from heart_rate import HeartRate
import time

def main():
    sensor = MAX30102(address=0x57, bus=1)
    hr = HeartRate(frequency=100)

    print("MAX30102 Heart Rate Measurement Started...")

    while True:
        try:
            ir, red = sensor.read_fifo()
        except OSError as e:
            print("I2C read error:", e)
            time.sleep(0.1)
            continue

        hr.add_sample(ir, red)
        bpm = hr.get()

        # print(f"? {hr}, {bpm}")
        
        if bpm == -1:
            print("No finger detected...")
        else:
            print(f"Heart Rate: {bpm} bpm")

        time.sleep(0.01)

if __name__ == "__main__":
    main()
