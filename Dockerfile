FROM coinor/coin-or-optimization-suite
WORKDIR /workdir
RUN apt-get update && apt-get install python3 python3-pip --yes
ADD requirements.txt .
RUN pip install -r requirements.txt