FROM python:3.13
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
CMD [ "streamlit", "run", "main.py" ]