FROM python:3.10-slim-bullseye

ARG USERNAME=nb_user
ARG UID
ARG GID

RUN groupadd --gid $GID ${USERNAME} \
    && useradd -m -u $UID --gid $GID ${USERNAME}

RUN apt-get update -qq \
    && apt-get install -yqq gcc graphviz graphviz-dev git

RUN pip install -U pip

WORKDIR /assignment

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm ./requirements.txt

USER ${USERNAME}

ENTRYPOINT ["jupyter", "lab", "--no-browser", "--ip=0.0.0.0", "--notebook-dir", "/assignment"]
