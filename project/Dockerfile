# Use the appropriate Odoo version
FROM odoo:16.0

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8

# Update and install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3-passlib python3-wheel openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev \
       libfontconfig1-dev libfreetype6-dev fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Switch back to the odoo user and set the working directory
USER odoo
WORKDIR /mnt/extra-addons

# Copy the custom addons into the image
COPY ./custom-addons .
