# stream_heart_beat_from_HTTP

Receives external heart beat HTTP requests into a Flask server (e.g. Amazfit --> Zepp --> 3rd party glue-app --> Tasker --> HTTP GET Task --> TXT file in PC hard drive) and builds a speedometer-looking PNG to be used inside a stream.

It is composed of two parts:

1. The one that is an HTTP server that writes an integer into `heart_rate.txt`;
2. The one that reads `heart_rate.txt` and writes `vuMeter_rendered.png`, which can be used as an `Image Source` on `OBS`.

## Running

In order to start the first part (HTTP data to file), run `runserver.bat`.

In order to start the second part (file to image), run `rundaemon.bat`.
