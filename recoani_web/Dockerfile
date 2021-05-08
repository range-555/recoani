FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /workspace
WORKDIR /workspace

COPY requirements.txt /workspace/
RUN pip install -r requirements.txt
COPY ./recoani_web /workspace/

RUN useradd -m recoani
USER recoani

CMD ["gunicorn", "config.wsgi", "-b", "0.0.0.0:8080"]
