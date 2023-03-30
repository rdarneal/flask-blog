FROM python:slim

RUN useradd portfolio

WORKDIR /home/portfolio

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY portfolio.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP portfolio.py

RUN chown -R portfolio:portfolio ./
USER portfolio

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]