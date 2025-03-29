FROM python:3.12-bookworm

COPY . /app
WORKDIR /app

ENV SECRET_KEY=""

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot

ENTRYPOINT ["/app"]

RUN pip install -r requirements.txt

WORKDIR /app/SitePlante

CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"