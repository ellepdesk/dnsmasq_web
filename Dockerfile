FROM python:3.11-alpine as builder

WORKDIR /install
COPY dnsmasq_web/requirements.txt requirements.txt
RUN pip install setuptools wheel
RUN pip wheel -r requirements.txt

WORKDIR /install/static
RUN wget "https://github.com/twbs/bootstrap/releases/download/v5.3.3/bootstrap-5.3.3-dist.zip"
RUN unzip bootstrap-5.3.3-dist.zip

WORKDIR /install/static/jquery/
RUN wget https://code.jquery.com/jquery-3.7.1.min.js

WORKDIR /install/static/bootstrap-table/
RUN wget https://cdn.jsdelivr.net/npm/bootstrap-table@1.23.5/dist/bootstrap-table.min.css
RUN wget https://cdn.jsdelivr.net/npm/bootstrap-table@1.23.5/dist/bootstrap-table.min.js


# ----------------------------------------------------------------------------------------------

FROM python:3.11-alpine

# install python libs
COPY --from=builder /install/*.whl /tmp/
RUN pip install /tmp/*.whl

# copy static requirements
WORKDIR /app/static
COPY --from=builder /install/static/bootstrap-5.3.3-dist/css/bootstrap.min.css ./
COPY --from=builder /install/static/bootstrap-5.3.3-dist/js/bootstrap.bundle.min.js ./
COPY --from=builder /install/static/jquery/jquery-3.7.1.min.js ./
COPY --from=builder /install/static/bootstrap-table/* ./

# copy application
WORKDIR /app
COPY dnsmasq_web/*.py ./
COPY dnsmasq_web/static/* ./static/

RUN mkdir -p host

# start script
CMD [ "python3", "dnsmasq_web.py"]