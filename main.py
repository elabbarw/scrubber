"""
This script is an API for scrubbing personal identifiable information (PII) from text using FastAPI and the presidio_analyzer library. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. Presidio helps to recognise PII entities in text, annonymize (using the Presidio Anonymizer) and detect necessary system entities.

Firstly, it creates a Presidio RecognizerRegistry and loads a smaller NLP engine. It also loads custom recognizers from a specified JSON file and adds our recognizers to the registry.

An authentication function, get_api_key, is defined to check the provided API key against an expected value.

FastAPI is then set up with endpoint '/scrub' to accept POST requests. A BaseModel using Pydantic is created for the expected request body for validation purposes.

The '/scrub' endpoint uses function scrub_text that calls the scrubber function, which uses Presidio AnalyzerEngine to analyze the text and the AnonymizerEngine to replace detected personal information and postcode from the transcript with ""

Upon successful scrubbing, it returns a JSON response with the scrubbed text. Any error encountered during the process will raise an HTTPException with detail on the error.

The service can be run directly using uvicorn, a ASGI server, listening on host 0.0.0.0 and port 8000.

Wanis
"""
import json
import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from pydantic import BaseModel, Field
from gptrim import trim



# Presidio Registry
PII_REG = RecognizerRegistry()
# Load a large NLP engine for lambda
configuration =  {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_md"}
    ]
}
provider = NlpEngineProvider(nlp_configuration=configuration)
large_engine = provider.create_engine()

# Load Wanis's recognizers json
with open('recognizers.json', 'r', encoding='utf-8') as f:
    recognizers = json.load(f)

# Load predefined recognizers
PII_REG.load_predefined_recognizers()

# and add our recognizers 
for recognizer_name, recognizer_data in recognizers.items():
    pattern_recognizer = PatternRecognizer(
        supported_entity=recognizer_name,
        patterns=[Pattern(**recognizer_data['pattern'])],
        context=recognizer_data['context']
    )
    PII_REG.add_recognizer(pattern_recognizer)
    
    
EXPECTED_API_KEY = os.environ.get('SCRUB_API_KEY')

async def get_api_key(x_api_key: str = Header()):
    "Function to handle authentication"
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return x_api_key

 
app = FastAPI()


### Define our basemodel for validation
class DataModel(BaseModel):
    transcript: str = Field(..., description='Transcription data')
    lang: str = Field('en', description='Language of the transcription')
class TrimModel(BaseModel):
    text: str = Field(..., description='Text to trim')

async def scrubber(transcript: str, lang: str = 'en'):
    """
    Remove Personal Informations & Postcode from the transcript
    """
    engine = AnonymizerEngine()
    analyzer = AnalyzerEngine(nlp_engine=large_engine,registry=PII_REG)

    analyzer_results = analyzer.analyze(text=transcript,
                                        language=lang,
                                        context=[
                                            'full name',
                                            'name',
                                            'postcode',
                                            'birth',
                                            'account',
                                            'address',
                                            'actor',
                                            'Actor Name',
                                            'Actor Name:'
                                            'Actor',
                                            'Message:',
                                        ],
                                        )

    result = engine.anonymize(
        text=transcript,
        analyzer_results=analyzer_results,
        operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"})}) # Replace all detected PII with <REDACTED>

    return result.text

@app.post('/scrub')
async def scrub_text(data: DataModel, x_api_key: str = Depends(get_api_key)):
    try:
        scrubbed = await scrubber(data.transcript, data.lang)
        return JSONResponse(content={'scrubbed_text': scrubbed})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error processing text: {str(e)}'
            )
            
@app.post('/trim')
async def trim_text(data: TrimModel, x_api_key: str = Depends(get_api_key)):
    try:
        trimmed = trim(data.text)
        return JSONResponse(content={'trimmed': trimmed})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error processing text: {str(e)}'
            )


    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
