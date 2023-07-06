FROM python:3.11-slim-bullseye

# Install latest version of tesseract, after installing dependencies.
# Also install poppler-utils, for pdf to image conversion utilities.
RUN apt-get update \
    && apt-get install lsb-release wget apt-transport-https gnupg -y -qq \
    && echo "deb https://notesalexp.org/tesseract-ocr5/$(lsb_release -cs)/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/notesalexp.list \
    && wget -qO- https://notesalexp.org/debian/alexp_key.asc | tee /etc/apt/trusted.gpg.d/alexp_key.asc \
    && apt-get update \
    && apt-get install tesseract-ocr -y -qq \
    && apt-get install poppler-utils -y -qq

# Set correct timezone
RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

# Create non-privileged user and switch context to that user
RUN useradd -c "Campaign Lit app user" -d /home/camplit -s /bin/bash -m camplit
USER camplit

# Copy application files to image, and ensure camplit user owns everything
COPY --chown=camplit:camplit . .

# Include local python bin into user's path, mostly for pip
ENV PATH /home/camplit/.local/bin:${PATH}

# Make sure pip is up to date, and don't complain if it isn't yet
RUN pip install --upgrade pip --disable-pip-version-check

# Install requirements for this application
RUN pip install --no-cache-dir -r requirements.txt --user --no-warn-script-location
