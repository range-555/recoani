FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /workspace

COPY ./src/app/requirements.txt /workspace/
RUN pip install -r requirements.txt
COPY ./src/app/recoani /workspace/

RUN useradd -m recoani
USER recoani

CMD ["gunicorn", "config.wsgi", "-b", "0.0.0.0:8080"]
