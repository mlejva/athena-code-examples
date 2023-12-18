FROM python:3.11

RUN mkdir /app
RUN mkdir /app/server
COPY /server /app/server
COPY pyproject.toml /app
WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
# RUN poetry install --no-dev
RUN poetry install
EXPOSE 8000
CMD ["poetry", "run", "start"]
