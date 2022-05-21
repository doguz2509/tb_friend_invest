FROM python:3.8.3-buster

ENV WORK_DIR=/opt
ENV PROJECT_DIR=project
ENV REQUIREMENTS_TXT=requirements.txt
ENV TOKEN=''
ENV VERSION=0.0.2
ENV LEVEL=INFO

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install PyYAML==6.0 \
    && mkdir -p $WORK_DIR/$PROJECT_DIR

ADD . $WORK_DIR/$PROJECT_DIR
WORKDIR $WORK_DIR/$PROJECT_DIR

RUN python3 -m pip install -r requirements.txt \
    && python3 setup.py bdist_wheel \
    && python3 -m pip install dist/*.whl

ENTRYPOINT ["python3", "-m", "share_invest"]

