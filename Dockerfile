FROM ubuntu:latest
MAINTAINER Frederik Baumgardt "frederik.baumgardt@tufts.edu"
RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential curl
ADD ./ /app
WORKDIR /app
RUN ls -la
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["run.py"]