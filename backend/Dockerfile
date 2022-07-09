FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip3 install -r /app/requirements.txt --no-cache-dir
ADD commands.sh /commands.sh
RUN chmod a+x /commands.sh
ENTRYPOINT ["/commands.sh"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]