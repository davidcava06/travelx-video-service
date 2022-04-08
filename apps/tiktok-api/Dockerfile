FROM python:3.9.10-slim
WORKDIR /usr/app

RUN apt-get update
RUN apt-get install -y build-essential

COPY pyproject.toml poetry.lock Makefile ./
RUN pip install poetry==1.1.13
RUN poetry config virtualenvs.create false

RUN make install

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
