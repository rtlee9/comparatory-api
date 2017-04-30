FROM python:2.7
MAINTAINER Ryan Lee "ryantlee9@gmail.com"
RUN apt-get update -y
COPY . /comparatory
WORKDIR /comparatory
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["gunicorn", "--config=gunicorn.py"]
CMD ["app:app"]
