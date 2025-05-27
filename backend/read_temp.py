from pathlib import Path

def read_temperature():
    base_dir = Path("/sys/bus/w1/devices")
    device_folder = next(base_dir.glob("28-*"), None)

    if not device_folder:
        return None

    device_file = device_folder / "w1_slave"
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
    except:
        return None

    if lines[0].strip()[-3:] != 'YES':
        return None

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) / 1000.0

    return None

if __name__ == "__main__":
    temp = read_temperature()
    if temp is not None:
        print(f"{temp:.2f}")
    else:
        print("NaN")