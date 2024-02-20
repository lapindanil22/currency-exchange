FROM python:3.12-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY . .
RUN python -m pip install -r requirements.txt

WORKDIR /src

CMD ["uvicorn", "--host", "0.0.0.0", "main:app"]
