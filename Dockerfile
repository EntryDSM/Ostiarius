FROM python:3.7
MAINTAINER Seonghyeon Kim "seonghyeon@entrydsm.hs.kr"
COPY . .
WORKDIR .
RUN pip install sanic && pip install pyjwt && pip install -r requirements.txt
EXPOSE 7777
ENTRYPOINT ["python"]
CMD ["-m", "ostiarius"]