FROM centos:8

WORKDIR /app

COPY requirements.txt app.py .

RUN dnf install python3 -y; pip3 install -r requirements.txt

ENV FLASK_ENV development

ENTRYPOINT ["flask", "run"]

CMD ["--debugger", "--host", "0.0.0.0", "--port", "5000"]
