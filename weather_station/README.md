# CM3267 Lab Instruction for Weather Station
Ridhuan Syafiq

This folder contains 5 scripts for use:

- `weather.py` is the main data collection script.

- `DHT22_cal.py` helps you find the mean absolute difference between the
  actual and recorded temperature/humidity. You can then append these
  values to `weather.py`.

- `weatherplot.py` takes the output of `weather.py` and outputs a simple
  line plot.

- `weathertest.py` is a diagnostic tool to check the stability of your
  connections by sampling recordings. Execute this script before running
  your experiment with `weather.py`.

- `weatherplot_notebook.py` demonstrates how to interpret the output of
  `weathertest.py` (with `example.tsv` as input) using Python, with
  annotated examples of data visualisation. This file is intended to be
  run on your personal computer in an IDE that supports cell-based
  execution, such as Spyder

## Weather station setup

------------------------------------------------------------------------

### Activating the virtual environment

> [!WARNING]
>
> Make sure the steps in [RPi Setup](../README.md) were followed before
> proceeding. Verify by checking that
> `~/RPi-project/weather_station/venv` exists.

1.  In the terminal, navigate to the project directory and activate the
    virtual environment:

    ``` bash
    cd ~/RPi-project/weather_station
    source venv/bin/activate
    ```

2.  Now, you should be able to execute the python scripts accordingly:

    ``` bash
    python3 weather.py
    python3 DHT22_cal.py
    python3 weatherplot.py
    ```

As with the spectrometer scripts, ensure that the virtual environment is
activated before running any scripts – this is indicated by `(venv)`
appearing at the start of the prompt. Note that the spectrometer and
weather station projects each have their **own separate virtual
environments**. If a script fails unexpectedly, it could be that you may
have the wrong virtual environment active (they are named the same). In
that case, run `deactivate` and repeat from step 1.

3.  Finally, weather.py assumes the particle sensor is located at port /dev/ttyUSB0. Thus, to make sure the particle sensor is active on RPi, enter on Terminal:

    ```ls /dev/tty*``` 

    If /dev/ttyUSB0 is present as one of the folders, then you're correct. Otherwise, reattach your particle sensor to another USB port and repeat the above command until you see the right folder.

------------------------------------------------------------------------

### Execute `weather.py` on boot

If you wish to execute the `weather.py` script on boot, instructions
below allow adding of the python execution to the boot sequence.

1.  Create a shell script named `launcher.sh` in /home/pi/Desktop/:

    ``` bash
    cd ~/Desktop
    nano launcher.sh
    ```

2.  Copy the following into the `launcher.sh` text file:

    ``` bash
    #!/bin/sh
    cd /home/pi/RPi-project/weather_station
    /home/pi/RPi-project/weather_station/venv/bin/python3 weather.py
    ```

3.  Create a log folder for crontab logging via terminal:

    ``` bash
    cd ~
    mkdir logs
    ```

4.  Access crontab (with `sudo crontab -e`) and append the following to
    the end of the crontab script. Use `/bin/nano` as the editor if
    prompted:

    ``` bash
    @reboot sh /home/pi/Desktop/launcher.sh >/home/pi/logs/cronlog 2>&1
    ```

5.  Exit by pressing ‘Ctrl-X’ \> ‘y’ \> enter.

6.  Reboot your RPi and the script will run in the background:

    ``` bash
    sudo reboot
    ```

7.  To deactivate the script from executing on boot, simply access
    `launcher.sh` and comment out the last 2 lines. Then reboot.

NOTE:

- Your RPi will reboot, and you can still use the RPi as per usual as
  the python script is running in the background.

- To check any error occured, simply check the log file by inputting
  `cat ~/logs/cronlog` into the terminal. Otherwise, `Finaltest.csv`
  contains your data collection in
  `/home/pi/RPi-project/weather_station/`.

- Adjust the schedule function calls to acquire readings in an
  appropriate interval.

------------------------------------------------------------------------

> [!WARNING]
>
> Always run `deactivate` in the terminal once you’re done with the
> scripts, to make sure the venv is deactivated.
