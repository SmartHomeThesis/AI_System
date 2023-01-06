import time


relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91]
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]
def setDevice1(state, ser):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]
def setDevice2(state, ser):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)

def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

air_temperature = [3, 3, 0, 0, 0, 1, 133, 232]
def readTemperature(ser):
    serial_read_data(ser)
    ser.write(air_temperature)
    time.sleep(1)
    return serial_read_data(ser)

air_humidity = [3, 3, 0, 1, 0, 1, 212, 40]
def readHumidity(ser):
    serial_read_data(ser)
    ser.write(air_humidity)
    time.sleep(1)
    return serial_read_data(ser)