# Base image
FROM lsiobase/alpine.python3.arm64

MAINTAINER Alexander Ivanov <oz.sasha.ivanov@gmail.com>

# System envoriments
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

# Target requirements
COPY requirements.txt /opt/app/

WORKDIR /opt/app

# Project's requirements
RUN pip3 install -r requirements.txt

# Target project
COPY . .

# Valid stopping
STOPSIGNAL SIGINT

# Run main executable script
ENTRYPOINT ["python3", "manage.py"]
