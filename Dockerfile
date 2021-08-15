FROM alpine:3.14

WORKDIR /app

COPY requirements.txt app.py .

RUN apk add python3 py3-pip; pip3 install -r requirements.txt

ENV FLASK_ENV development

ENTRYPOINT ["flask", "run", "--debugger", "--host", "0.0.0.0"]

CMD ["--port", "5000"]
