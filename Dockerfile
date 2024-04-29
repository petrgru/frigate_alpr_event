FROM python:3.11.2-alpine
ENV APP=/app
RUN mkdir $APP
WORKDIR $APP
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "mqtt_sub.py"]

