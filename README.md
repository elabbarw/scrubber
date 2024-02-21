
# PII Scrubbing Application using FastAPI and Presidio Analyzer
This python script is implemented to scrub the Personally Identifiable Information (PII) from the text using Python3.6+, FastAPI and presidio_analyzer. Specifically, it is designed to recognize PII patterns within a given text, anonymize them by replacing the uncovered PII with "" and respond back with the scrubbed text.

## Getting Started
You need to have Python3.6 or higher to run this script. You can clone or download this script and run it locally on your machine.


### Prerequisites
To install all the required packages you can use pip:

```
pip install -r requirements.txt
```
Please note that to run this application, you would also need uvicorn, an ASGI server. If it's not installed, please install it using the following pip command:


```
pip install uvicorn
```

You also need to set the expected api key as an environment variable named SCRUB_API_KEY to use in the authentication process.

### How to use this application
This service listens on host 0.0.0.0 and port 8000. You can make a POST request to /scrub endpoint using the following JSON body:
```
{
  "transcript": "<Your text>",
  "lang": "<language of the text>"
}
```
Please note that transcript is the actual text you want to scrub and it's a mandatory field, and lang is optional where you can specify the language of your text. If nothing is provided it defaults to English 'en'.

x_api_key header should also be provided for the authentication.

Here is how a curl command would look like:
```
curl --location --request POST 'http://localhost:8000/scrub' \
--header 'x-api-key: <Enter your API key here>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "transcript": "<Your text>",
  "lang": "<language of the text>"
}'
```

### Running
To run this application, use the uvicorn command as follows:

```
uvicorn main:app --host=0.0.0.0 --port=8000
```

If everything is fine, your service should now be up and running, ready to listen for incoming requests. You can change the port and ip in the command but by default, it would run on 0.0.0.0:8000

## Built With
FastAPI
Presidio Analyzer

## Author
Wanis Elabbar - github.com/welabbar
