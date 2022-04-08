FROM python:3.9.10-slim
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1
WORKDIR /usr/app

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update
RUN apt-get install -y build-essential libpq-dev --no-install-recommends
RUN python -m venv /venv

COPY requirements/main.txt requirements.txt
RUN /venv/bin/pip install -r requirements.txt

ENV ENVIRONMENT=nonprod

COPY src src

RUN apt-get update && apt-get install -qq -y bash ca-certificates openssl --no-install-recommends
RUN sed -i 's/DEFAULT@SECLEVEL=2/DEFAULT@SECLEVEL=1/g' /etc/ssl/openssl.cnf
RUN sed -i 's/DEFAULT@SECLEVEL=2/DEFAULT@SECLEVEL=1/g' /usr/lib/ssl/openssl.cnf
COPY gunicorn.py ./
COPY main.py ./
COPY src ./src
EXPOSE 8000

CMD ["/venv/bin/gunicorn", "-c", "gunicorn.py", "-k", "uvicorn.workers.UvicornWorker", "main"]
