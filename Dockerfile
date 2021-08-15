FROM alpine:3.14

WORKDIR /app

COPY requirements.txt app.py .

RUN apk add python3 py3-pip; pip3 install -r requirements.txt

ENV FLASK_ENV development

ENTRYPOINT ["flask", "run"]

CMD ["--debugger", "--host", "0.0.0.0", "--port", "5000"]
