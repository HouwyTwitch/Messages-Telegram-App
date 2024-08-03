FROM python:3.9-slim

WORKDIR /bot

COPY . /bot

RUN pip install --no-cache-dir aiogram==2.25.2 aiohttp

CMD ["python", "bot.py"]
