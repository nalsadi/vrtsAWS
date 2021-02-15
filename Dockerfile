#Dockerfile,Image, Container 

FROM python:2.7


RUN pip install scipy 

COPY ./vrtsAWS/ /vrtsAWS/
COPY ./testdata/ /testdata/
CMD [ "python", "vrtsAWS/MasterDataGenerator.py" ]