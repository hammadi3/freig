FROM python:3.7.7
MAINTAINER alaeddine.tmar@siemens.com
USER root
WORKDIR /app
ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN python setup.py install


EXPOSE 5000
CMD ["gunicorn", "--bind" ,"localhost:5000","--workers","3","--worker-class","gevent","--worker-connections","1000","app.app:app"]

