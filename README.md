# Heart Beat from HTTP into PNG

Receives external heart beat HTTP requests into a Flask server (e.g. Amazfit --> Zepp --> 3rd party glue-app --> Tasker --> HTTP GET Task --> TXT file in PC hard drive) and builds a speedometer-looking PNG to be used inside a stream.

It is composed of three parts:

1. An Heart Beat Rate uploader, which can be [this other project](https://github.com/adlerosn/stream_heart_beat_from_BLE_into_HTTP) or [Tasker (paid)](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm).
2. The one that is an HTTP server that writes an integer into `heart_rate.txt`;
3. The one that reads `heart_rate.txt` and writes `vuMeter_rendered.png`, which can be used as an `Image Source` on `OBS`.

## Requirements

Python (3.10) and the libraries:
 - Flask
 - Pillow

## Running

In order to start the first part (HTTP data to file), run `runserver.bat`.

In order to start the second part (file to image), run `rundaemon.bat`.
