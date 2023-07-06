# campaign-literature-ocr
Experimental project to use OCR and AI/ML on UCLA Campaign Literature Collection

## Developer Information

### Overview of environment

The local development environment requires:
* git (at least version 2)
* docker (current version recommended: 20.10.12)
* docker-compose (at least version 1.25.0; current recommended: 1.29.2)

#### camplit container
Everything important is in the docker container
* [Tesseract OCR 5.3.1](https://tesseract-ocr.github.io/tessdoc/)
* Python 3.11, with the latest versions of several packages
  * [pillow (Python Imaging Library (Fork))](https://pypi.org/project/Pillow/)
  * [pdf2image (wrapper around the pdftoppm and pdftocairo command line tools)](https://pypi.org/project/pdf2image/)
  * [pytesseract (wrapper for Google's Tesseract-OCR)](https://pypi.org/project/pytesseract/)
  * [nltk (Natural Language Toolkit)](https://pypi.org/project/nltk/)
  * [spacy (Industrial-strength Natural Language Processing (NLP) in Python)](https://pypi.org/project/spacy/)
  * [openai (Python client library for the OpenAI API)](https://pypi.org/project/openai/)

See `requirements.txt` for specific versions used, and links to documentation for each package.

### Setup
1. Clone the repository.

   ```$ git clone git@github.com:UCLALibrary/campaign-literature-ocr.git```

2. Change directory into the project.

   ```$ cd campaign-literature-ocr```

3. Build using docker-compose.

   ```$ docker-compose build```

4. Get a copy of `.camplit_secrets.env` from a colleage and place it in the current directory.

5. Bring the system up, with containers running in the background.

   ```$ docker-compose up -d```

6. Logs can be viewed, if needed (`-f` to tail logs).

   ```$ docker-compose logs -f camplit```

7. Run commands in the containers, if needed.

   ```
   # Run python shell
   $ docker-compose exec camplit python
   
   # Run tesseract (better examples to be added...)
   $ docker-compose exec camplit tesseract --version

   # Run bash shell, to just work in the container, as the camplit user
   $ docker-compose exec camplit bash

   # Run a privileged bash shell as root, in case it's needed
   $ docker-compose exec -u root camplit bash

8. Shut down the system when done.

   ```$ docker-compose down```
