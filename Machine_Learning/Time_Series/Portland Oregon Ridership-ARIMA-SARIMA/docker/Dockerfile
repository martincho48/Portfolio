#sources-YouTube:
#https://www.youtube.com/watch?v=Gs15V79cauo&t=467s
#https://www.youtube.com/watch?v=mUnrWn6flfc&t=2s
#https://www.youtube.com/watch?v=0UG2x2iWerk&t=1s

#Web:
#https://www.analyticsvidhya.com/blog/2022/05/a-complete-guide-for-deploying-ml-models-in-docker/


#takes base image from Docker hub
FROM python:3.9

#working directory-give it whatever name you like
WORKDIR /home

#copy and install requirements, dot is a baselayer of the container
COPY requirements.txt ./
RUN pip install -r requirements.txt


#copy all files into a image
COPY sarima.pkl ./
COPY script_ridership.py ./


#run the main script
CMD ["python", "./script_ridership.py"]
