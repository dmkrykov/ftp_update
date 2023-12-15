# load python 3.8 dependencies using slim debian 10 image.
FROM python:3.10.10-slim-buster

# build variables.
ENV DEBIAN_FRONTEND noninteractive
ENV ACCEPT_EULA=Y

# install Microsoft SQL Server requirements and ru locales
RUN apt-get update -y && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev && apt-get install -y locales locales-all \
  && locale-gen ru_RU.UTF-8 && locale-gen ru_RU.CP1251 && dpkg-reconfigure locales
# Add SQL Server ODBC Driver 18 for Ubuntu 18.04
RUN apt-get install ca-certificates \
#    && apt-get install -y curl apt-transport-https \
    && curl -s https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql18 unixodbc-dev

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# upgrade pip and install requirements.
COPY /requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt

# copy all files to /app directory and move into directory.
COPY openssl.cnf /etc/ssl/openssl.cnf
WORKDIR /app
COPY src/ .

ENTRYPOINT ["sleep",  "infinity"]
#ENTRYPOINT ["python",  "main.py"]
