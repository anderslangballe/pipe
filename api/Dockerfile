FROM python:3.7

# Install Java
RUN apt-get update && apt-get install openjdk-8-jdk -y

# Copy files
COPY pipe /opt/pipe
COPY libs /opt/pipe/libs
COPY engines /opt/pipe/engines
RUN mkdir -p /opt/pipe/logs
WORKDIR /opt/pipe

# Install requirements and run the PIPE API
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
#CMD ["gunicorn" , "-b", "0.0.0.0:8080", "app:app"]

EXPOSE 8000
