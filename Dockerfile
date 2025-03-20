FROM python:3.12.9-slim

RUN mkdir -p /app
COPY . storeapi/main.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8081
CMD ["storeapi/main.py"]
ENTRYPOINT [ "python" ]