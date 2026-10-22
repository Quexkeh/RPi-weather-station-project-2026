# CM3267 RPi Projects
Ridhuan Syafiq

## Documentation

Data collection projects with RPi 5.

1.  Spectrometer project
2.  Weather station project

Originally developed for RPi 3 — this repo contains the upgraded, tested
version for RPi 5.

------------------------------------------------------------------------

## Hardware & OS

- **Device:** Raspberry Pi 5
- **OS:** Raspberry Pi OS Trixie (Debian 13), 64-bit — released
  2026-04-21
- **Kernel:** 6.12.75 (check with `uname -r`)
- **Python:** 3.13.5 (check with `python3 --version`)

------------------------------------------------------------------------

## Repo Structure

    RPi-project/
    ├── spectrometer/
    │   ├── README.md
    │   ├── spectrometer_reqs.txt
    │   ├── blinkatest.py             # tests if interfaces work correctly
    │   ├── voltage_read.py           # tests if photodiode works detects a signal
    │   └── spectrometer.py           # main spectrometer script
    ├── weather_station/
    │   ├── README.md
    │   ├── weather_station_reqs.txt
    │   ├── example.tsv               # example output of weather.py
    │   ├── weatherplot_notebook      # data visualisation examples
    │   ├── weathertest.py            # diagnostic tool for weather.py
    │   ├── DHT22_cal.py              # calibration script for DHT22 sensor
    │   ├── weatherplot.py            # quick plotting script
    │   └── weather.py                # main weather station script
    ├── setup.sh
    └── README.md

Each project has its own virtual environment and dependencies to avoid
conflicts.

------------------------------------------------------------------------

## Protocol for setting up new RPis

1.  Download [Raspberry Pi
    Imager](https://www.raspberrypi.com/software/).

2.  Plug in microsd card into a USB reader and follow set-up
    instructions on the imager app.

3.  Specifications

    <table>
    <colgroup>
    <col style="width: 22%" />
    <col style="width: 77%" />
    </colgroup>
    <thead>
    <tr>
    <th>Setup steps</th>
    <th>Specs</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td>Device</td>
    <td>Raspberry Pi 5</td>
    </tr>
    <tr>
    <td>OS</td>
    <td><p>Raspberry Pi OS (64-bit). Released 2026-04-21.</p>
    <p>64 bit is important for RPi5 compatibility.<br />
    Version is important for consistency. Might have to an additional step
    of downloading this particular image from archive if newer versions are
    released.</p></td>
    </tr>
    <tr>
    <td>Storage</td>
    <td>Select the USB reader</td>
    </tr>
    <tr>
    <td>Hostname</td>
    <td>***</td>
    </tr>
    <tr>
    <td>Localisation</td>
    <td>Capital city &gt; Singapore (Singapore)<br />
    Timezone &gt; Asia/Singapore<br />
    Keyboard layout &gt; us</td>
    </tr>
    <tr>
    <td>User</td>
    <td>Username &gt; pi<br />
    Password &gt; 12345</td>
    </tr>
    <tr>
    <td>Wi-Fi</td>
    <td><strong>OPTIONAL<br />
    </strong>SSID &gt; NUS_Guest</td>
    </tr>
    <tr>
    <td>Remote authentication/Raspberry Pi Connect</td>
    <td>Default settings (not activated)</td>
    </tr>
    </tbody>
    </table>

4.  Write to the disk. If a dialogue box pops up, press “x” (NOT
    CANCEL).

5.  This will wipe the sd card and automatically format to FAT32.

6.  Plug-and-play into the RPi 5.

7.  Connect to the internet. NUSGuest is often unstable so it's recommended to hotspot to your phone data for now. Then go to terminal to check date and time. On the sudo lines, if you're prompted to enter password, enter '12345' (without the '').

``` bash
# Check date and time
timedatectl

# Change date and time, set location, then ensure that it syncs to internet time.
sudo date -s "25 MAY 2026 11:37:00" # Edit accordingly
sudo timedatectl set-timezone Asia/Singapore
sudo timedatectl set-ntp true
```

8.  Hold kernel and OS versions and freeze dependencies:

``` bash
# Hold kernel and OS
sudo apt-mark hold linux-headers-6.12.75+rpt-rpi-2712
sudo apt-mark hold linux-headers-rpi-2712
sudo apt-mark hold linux-image-6.12.75+rpt-rpi-2712
sudo apt-mark hold linux-image-rpi-2712

# Hold python
sudo apt-mark hold python3

# Freeze updates (disable auto-update)
sudo systemctl disable apt-daily.service
sudo systemctl disable apt-daily-upgrade.service
sudo systemctl disable apt-daily.timer
sudo systemctl disable apt-daily-upgrade.timer
```

------------------------------------------------------------------------

## RPi Setup

Open a terminal and clone the repo onto the Pi:

``` bash
cd ~
git clone https://github.com/BeeHoonGoreng/RPi-project.git
cd RPi-project
bash setup.sh
```

You will now have a copy of the repo with the above structure as a
folder labelled *RPi-project*. The bash script *setup.sh* creates the
virtual environments and downloads dependencies for you.

------------------------------------------------------------------------

## Usage

Before running any `.py` script, you have activate the relevant venv by
going into the correct project folder and running
`source venv/bin/activate`. Run `deactivate` after to prevent conflicts.
Example:

``` bash
cd ~/RPi-project/spectrometer
source venv/bin/activate

## Run scripts and collect data

deactivate
```

Each project folder has its own README.md which details the functions of
the scripts they contain.

------------------------------------------------------------------------

## Notes

- Original code was written for RPi 3 — dependencies updated for RPi 5 /
  Python 3.13.5 compatibility

  - Weather station - adafruit-dht is depreciated.
    [adafruit-circuitpython-dht](https://github.com/adafruit/Adafruit_CircuitPython_DHT)
    is used instead

- `*_reqs.txt` in each folder pins exact package versions (using
  `pip freeze`) for reproducibility.
