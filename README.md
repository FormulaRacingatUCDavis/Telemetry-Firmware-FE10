# Telemetry Firmware
Viewing live graphs from sensor data. TelemHost sends data via WiFi to TelemTransceiver which is wired to a laptop for viewing.

CAN--> TEENSY --UART--> ESP32 --WIFI--> ESP32 --Serial--> Laptop

Plotting uses pyserial and matplotlib python packages. Change portName in plot_serial_data.py before using. Press any key to pause and resume plotting.
