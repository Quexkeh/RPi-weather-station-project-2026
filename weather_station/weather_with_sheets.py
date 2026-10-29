#!/usr/bin/env python3 -u

############################################################
# Initialisation                                           #
############################################################

###### Import modules ######################################
import time, struct
from datetime import datetime

import serial
import schedule
import adafruit_dht
import board
import gspread
from google.oauth2.service_account import Credentials
import csv

############################################################
# INPUT SECTION                                            #
############################################################

# [EDIT] Change output file name
filename = "weather_log"

# [EDIT] Calibration result
temperature_error = -0.7
humidity_error = 0

# [EDIT] Set recording interval here in minutes
recording_interval = 5

# Based on your calibration or the determination of error,
# change the temperature and humidity error below.
# e.g calibration result: humidity = actual - 0.3. Update
# humidity_error = -0.3

############################################################
# GOOGLE SHEETS STUFF (Thanks chatgpt)                     #
############################################################
SPREADSHEET_ID = "1cKf14QsvX0Flm7gRxxmZlrO4z-VHLUk5V8hBc-u0jlA"
CREDENTIALS_FILE = "./service_account.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

sheet = None
last_uploaded_row = 0

############################################################
# CHANNEL CREATION OF HUMIDITY AND TEMPERATURE DHT22 SENSOR#
############################################################

DHT_PIN = 4
DHT_SENSOR = adafruit_dht.DHT22(board.D4)                            ### Pin number can change with your preference, check GPIO pinout for reference

############################################################
# CHANNEL CREATION OF NOVA PM SENSOR                       #
############################################################

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1
PERIOD_CONTINUOUS = 0

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
ser.open()
ser.flushInput()

byte, data = 0, ""

def read_response():
    byte = 0
    while byte != b"\xaa":
        byte = ser.read(size=1)

    d = ser.read(size=9)

    if DEBUG:
        dump(d, '< ')
    return byte + d

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = b"\xaa\xb4" + bytes([cmd])
    ret += bytes(data)
    ret += b"\xff\xff" + bytes([checksum]) + b"\xab"

    if DEBUG:
        dump(ret, '> ')
    return ret

def process_data(d):
    r = struct.unpack('<HHxxBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(d[2:8])%256
    return [pm25, pm10]

def cmd_query_data():
    ser.write(construct_command(CMD_QUERY_DATA))
    d = read_response()
    values = []
    if d[1:2] == b"\xc0":
        values = process_data(d)
    return values

def cmd_set_sleep(sleep):
    mode = 0 if sleep else 1
    ser.write(construct_command(CMD_SLEEP, [0x1, mode]))
    read_response()
    
def cmd_set_mode(mode=MODE_QUERY):
    ser.write(construct_command(CMD_MODE, [0x1, mode]))
    read_response()
    
def cmd_set_working_period(period):
    ser.write(construct_command(CMD_WORKING_PERIOD, [0x1, period]))
    read_response()

cmd_set_sleep(0)
cmd_set_working_period(PERIOD_CONTINUOUS)
cmd_set_mode(MODE_QUERY)



############################################################
# FUNCTIONS FOR READING AND RECORDING SENSORS              #
############################################################

def main():
    #schedule.every(5).seconds.do(recording)
    # schedule.every().hour.at(":30").do(recording)
    # schedule.every().hour.at(":00").do(recording)
    schedule.every(recording_interval).minutes.do(recording)
    # schedule.every().day.do(recording)

    # Best to keep interval in whole 'hour' format as seen
    # above. Change the schedule only if you are mindful of
    # data processing e.g at the 15/30/45th minute of every
    # hour works too. Any other denomination would be
    # tedious though i.e last 3 options

    print("recording data...")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)     # while loop is checked every second (the smallest interval is per second)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print("Program end")

# recording() writes the data into a tab-delimited format:
# column namnes : TIMESTAMP | HOUR | PM2.5 | PM10 | TEMPERATURE | HUMIDITY
def recording():
    cmd_set_sleep(0)
    try:
        temperature = DHT_SENSOR.temperature + temperature_error
        humidity = DHT_SENSOR.humidity + humidity_error

    except Exception as e:
        print(f"DHT22 read failed: {e}, retrying next cycle...")
        return
    
    try:
        values = cmd_query_data()
    except Exception as e:
        print(f"PM sensor read failed: {e}, retrying next cycle...")
        return
    
    if values is not None and len(values) == 2 and humidity is not None and temperature is not None:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        h = datetime.now().hour
        
        data_pt = f"{timestamp}\t{h:1}\t{values[0]:.2f}\t{values[1]:.2f}\t{temperature:.2f}\t{humidity:.2f}\n"

        with open(filename + ".tsv", 'a') as f:
            f.write(data_pt)
            upload_to_sheets()
        
        print(timestamp)
        print(f"Hour= {h:1}  PM2.5 = {values[0]:1.2f}ug/m^3  PM10= {values[1]:1.2f}ug/m^3  Temp= {temperature:1.2f}*C  Humidity= {humidity:1.2f}%")
    
    elif values is None:
        print("Problem occurred with Air Quality sensor")
    elif humidity is None or temperature is None:
        print("Problem occurred with DHT22 sensor")
    else:
        print ("Failed to retrieve data from sensors")


############################################################
# GOOGLE SHEET FUNCTIONS (thanks chatgpt)                  #
############################################################

def connect_to_sheets():
    global sheet, last_uploaded_row

    try:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )

        client = gspread.authorize(creds)

        sheet = client.open_by_key(
            SPREADSHEET_ID
        ).worksheet("Sheet1")

        # Assuming row 1 contains headers
        last_uploaded_row = max(
            0,
            len(sheet.col_values(1)) - 1
        )

        print("Connected to Google Sheets")
        return True

    except Exception as e:
        sheet = None
        print(f"Google Sheets connection failed: {e}")
        return False

#def upload_to_sheets(data):
#    try:
#        sheet.append_row(
#            data,
#            value_input_option="USER_ENTERED"
#        )
#        print("Uploaded to Google Sheets")
#
#    except Exception as e:
#        print(f"Google Sheets upload failed: {e}")

def upload_to_sheets():
    global sheet, last_uploaded_row

    # Connect only when needed
    if sheet is None:
        if not connect_to_sheets():
            print("Google Sheets unavailable.")
            return

    try:
        with open(filename + ".tsv", "r") as f:
            reader = csv.reader(f, delimiter="\t")

            for row_number, row in enumerate(reader, start=1):

                # Skip previously uploaded rows
                if row_number <= last_uploaded_row:
                    continue

                # Upload one row at a time
                sheet.append_row(
                    row,
                    value_input_option="USER_ENTERED",
                    table_range="A1:F"
                )

                # Update only after successful upload
                last_uploaded_row = row_number

        print("Google Sheets synchronized")

    except Exception as e:
        print(f"Google Sheets upload failed: {e}")
        sheet = None

############################################################
# EXECUTION OF WEATHER STATION                             #
############################################################

if __name__ == "__main__":
    main()
