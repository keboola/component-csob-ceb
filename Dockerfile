FROM quay.io/keboola/docker-custom-python:latest
ENV PYTHONIOENCODING utf-8

COPY . /code/

RUN pip install -r /code/requirements.txt

WORKDIR /code/



CMD ["python", "-u", "/code/src/component.py"]
