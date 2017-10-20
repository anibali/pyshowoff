FROM ubuntu:16.04

# Install curl, sudo, bzip2, and git
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    bzip2 \
    git \
 && rm -rf /var/lib/apt/lists/*

# Use Tini as the init process with PID 1
RUN curl -Lso /tini https://github.com/krallin/tini/releases/download/v0.14.0/tini \
 && chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# Install Miniconda
RUN curl -so ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.3.27.1-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh

# Create a Python 3.6 environment
RUN /home/user/miniconda/bin/conda install conda-build \
 && /home/user/miniconda/bin/conda create -y --name py36 python=3.6 \
 && /home/user/miniconda/bin/conda clean -ya
ENV PATH=/home/user/miniconda/envs/py36/bin:$PATH \
    CONDA_DEFAULT_ENV=py36 \
    CONDA_PREFIX=/home/user/miniconda/envs/py36

# Install dependencies from pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set the default command to python3
CMD ["python3"]
