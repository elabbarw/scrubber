FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app
ADD . .
RUN pip install -r requirements.txt
ENV SCRUB_API_KEY = superduperapikey
RUN python -m nltk.downloader stopwords punkt wordnet
EXPOSE 8080

CMD [ "uvicorn", "main:app", "--host=0.0.0.0", "--port=8080" ]


