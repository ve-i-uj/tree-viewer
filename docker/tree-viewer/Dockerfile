FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update

RUN apt-get install -y build-essential python3.7 python3.7-dev python3-pip python3.7-venv \
    && apt-get install -y git

# update pip
RUN python3.7 -m pip install --upgrade pip \
    && python3.7 -m pip install wheel \
    && python3.7 -m pip install --upgrade setuptools


WORKDIR /opt/app
COPY . /opt/app

RUN pip3 install --requirement ./requirements.txt

RUN find . -name __pycache__ -type d | xargs rm -rf

CMD ["python3.7", "./treeviewer/main.py"]
