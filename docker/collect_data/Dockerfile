FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /workspace

RUN apt-get update && apt-get install -y wget gnupg

RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN apt-get update && apt-get install -y google-chrome-stable

RUN google-chrome --version | perl -pe 's/([^0-9]+)([0-9]+\.[0-9]+).+/$2/g' > chrome-version
RUN pip install chromedriver-binary~=`cat chrome-version` && rm chrome-version

RUN apt-get install -y fonts-ipafont-gothic --no-install-recommends

COPY requirements.txt /workspace/
COPY ./src/ /workspace/
RUN pip install -r requirements.txt

RUN useradd -m recoani
USER recoani

CMD ["invoke", "collect"]
