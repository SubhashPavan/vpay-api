FROM python:3.6
LABEL maintainer="pavansubhash@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]