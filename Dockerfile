FROM python:3.11-alpine as builder

WORKDIR /install
COPY dnsmasq_web/requirements.txt requirements.txt
RUN pip install setuptools wheel
RUN pip wheel -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app

# install python lib
COPY --from=builder /install/*.whl /tmp/
RUN pip install /tmp/*.whl

COPY dnsmasq_web/*.py ./
COPY dnsmasq_web/static ./static
RUN mkdir -p host

# start script
CMD [ "python3", "dnsmasq_web.py"]