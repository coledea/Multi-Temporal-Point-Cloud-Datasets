FROM python:3.10
WORKDIR /usr/local/app

# Copies all files within this folder to the image. If you added additional folders, you might want to exclude them.
COPY . . 

RUN pip install --no-cache-dir -r requirements/requirements-all.txt
RUN apt-get update && apt-get -y --no-install-recommends install libgl1

CMD ["bash"]