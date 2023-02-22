FROM python:3.8.16-alpine3.16

LABEL org.opencontainers.image.authors="Vaibhav Gupta"

COPY ./techtrends/ /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]