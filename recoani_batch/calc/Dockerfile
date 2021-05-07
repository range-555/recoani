FROM python:3.8
ENV PYTHONUNBUFFERED 1
WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y mecab \
  && apt-get install -y mecab-ipadic \
  && apt-get install -y libmecab-dev \
  && apt-get install -y mecab-ipadic-utf8 \
  && apt-get install -y swig

COPY requirements.txt /workspace/
COPY ./src/ /workspace/
RUN pip install -r requirements.txt

RUN ln -s /etc/mecabrc /usr/local/etc/mecabrc

RUN useradd -m recoani
USER recoani

CMD ["python3", "./calc_recommend_list.py"]
