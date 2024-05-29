#set base image 
FROM python:3.10.14

#set working directory
WORKDIR /code

#copy requirement.txt
COPY requirements.txt .

#install dependencies
RUN pip install -r requirements.txt

#copy code to workdir
COPY index.py .

#run code 
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]

