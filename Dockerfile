FROM python:3.7
LABEL maintainer="pavansubhash@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5555
ENTRYPOINT ["python"]
CMD ["app.py"]
