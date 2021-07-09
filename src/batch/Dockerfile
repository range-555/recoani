FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /workspace

# calc側パッケージ
RUN apt-get update \
  && apt-get install -y mecab \
  && apt-get install -y mecab-ipadic \
  && apt-get install -y libmecab-dev \
  && apt-get install -y mecab-ipadic-utf8 \
  && apt-get install -y swig

# crawl側
RUN apt-get update && apt-get install -y wget gnupg
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN apt-get update && apt-get install -y google-chrome-stable
# "google chrome 80.1~~~" → 80.1
RUN google-chrome --version | perl -pe 's/([^0-9]+)([0-9]+\.[0-9]+).+/$2/g' > chrome-version
RUN pip install chromedriver-binary~=`cat chrome-version` && rm chrome-version
RUN apt-get install -y fonts-ipafont-gothic --no-install-recommends

# 共通
COPY ./src/batch/requirements.txt /workspace/
COPY ./src/batch/tasks.py /workspace/
COPY ./src /workspace/src/
RUN pip install -r requirements.txt
RUN ln -s /etc/mecabrc /usr/local/etc/mecabrc

RUN useradd -m recoani
USER recoani

ENV PYTHONPATH "${PYTHONPATH}:/workspace"

CMD ["invoke", "batch"]
