#Dockerfile,Image, Container 

FROM python:2.7
#FROM node:14.15.5  

RUN pip install scipy 
RUN apt-get update

RUN apt-get install nodejs -y
RUN apt-get install npm -y
COPY package*.json ./

RUN npm install


COPY ./vrtsAWS/ /vrtsAWS/
COPY ./testdata/ /testdata/
COPY . .
EXPOSE 3000
#CMD [ "python", "vrtsAWS/MasterDataGenerator.py" ]
CMD [ "node", "index.js" ]

