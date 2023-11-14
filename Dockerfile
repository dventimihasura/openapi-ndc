FROM python:3.12.0-slim-bullseye
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
COPY config.json /config.json
EXPOSE 8080
ENV FLASK_APP=app.py
ENV CONFIG_FILE=/config.json
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "8080"]
