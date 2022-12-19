FROM ubuntu 

RUN apt-get update 
RUN apt-get install -y python3 python3-pip

RUN pip install --upgrade pip

COPY . reminder-telegram-bot
WORKDIR reminder-telegram-bot

RUN yes | pip install -r /reminder-telegram-bot/requirements.txt

CMD ["python3", "bot.py"]
