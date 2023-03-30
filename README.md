<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/rdarneal/flask-blog">
    <img src="app/statics/ico/../../static/ico/android-chrome-192x192.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">flask-blog</h3>

  <p align="center">
    Flask blog template integrated with Bootstrap 5.3 and custom css styling. Based on the tutorial by <a href="https://github.com/miguelgrinberg/microblog/">Miguel Grinberg</a>
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project includes a flask blueprint application divided primarily into 3 parts with various features:
- Blog
  - Post
  - Explore
  - View Users
  - Follow/Unfollow Users
  - Search Posts
  - Profile management
- Authentication
  - Registration
  - Login
  - Password Reset
- Error handling

The app is configured to use a mysql or sqllite database, and the repo is set-up for running via [Docker](https://www.docker.com/).

The search posts capability is provided via [Elasticsearch](https://www.elastic.co/) and is also primarily done through docker-container registration.



<br />

![Flask-microblog](/app/static/img/demo-1-landing.png)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Built With
* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
* ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]
* ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
* ![ElasticSearch](https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch)
* ![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

To fully try this project on your machine you will need at minimum:
* [Python](https://www.python.org/downloads/)
* [Docker](https://www.docker.com/)
* [VSCode](https://code.visualstudio.com/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/rdarneal/flask-blog.git
   ```
2. Navigate to the new folder and open with VS Code
   ```sh
   cd flask-blog
   code .
   ```
3. Create a new virtual environemnt folder `venv`
   ```sh
   python -m venv venv
   ```
4. Activate the virtual environment
   ```sh
   venv/bin/activate
   ```
5. Install Python packages
   ```sh
   pip install requirements.txt
   ```
6. Set the `.flaskenv` file to match your top level `blog.py` filename
   ```sh
   FLASK_APP=blog.py
   ```
7. Create a new `.env` file with vs code. IMPORTANT: Include `.env` in your `.gitignore` file! Don't share secrets.
   ```sh
   SECRET_KEY='yoursecretstring'
   MAIL_SERVER='your.smtp.mailserver.com'
   MAIL_PORT= 443
   MAIL_USERNAME = 'mailusername'
   MAIL_PASSWORD = 'mailpassword'
   MAIL_USE_TLS = 1
   ELASTICSEARCH_URL = 'http://localhost:9200'
   ```
8. Run the app locally to test it:
   ```sh
   flask --debug run
   ```
9. Note that when running with this method, search funtionality will only work if you have an activate Elasticsearch docker image. See docker method below for the command to launch a elasticsearch container.

<br />

### Deploying via Docker
The application is also set-up to be fully deployable via docker containers.

To use the docker method you must first build the application
```sh
docker build -t blog:latest .
```

Three containers are required: MySQL, Elasticsearch, and the blog applciation.
1. Each container can be launched sequentially
   - Mysql
      ```sh
      docker run --name mysql -d -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
      -e MYSQL_DATABASE=flask-blog -e MYSQL_USER=flask-blog \
      -e MYSQL_PASSWORD=<database-password> \
      mysql/mysql-server:latest
      ```
   - Elasticsearch
      ```sh
      docker run --name elasticsearch -d \
      -p 9200:9200 -p 9300:9300 \
      --rm -e "discovery.type=single-node" \
      docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
      ```
   - The app (-e sets the environment variables for the docker container)
      ```sh
      docker run --name flask-blog -d -p 8000:5000 --rm -e SECRET_KEY=my-secret-key \
      -e MAIL_SERVER=smtp.email.com -e MAIL_PORT=587 -e MAIL_USE_TLS=true \
      -e MAIL_USERNAME=<your-email-username> -e MAIL_PASSWORD=<your-email-password> \
      --link mysql:dbserver \
      -e DATABASE_URL=mysql+pymysql://flask-blog:<database-password>@dbserver/flask-blog \
      --link elasticsearch:elasticsearch \
      -e ELASTICSEARCH_URL=http://elasticsearch:9200 \
      flask-blog:latest
      ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Robert Darneal - python-dev@robertdarneal.com

Project Link: [https://github.com/rdarneal/flask-blog](https://github.com/rdarneal/flask-blog)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Miguel Grinberg's Microblog Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* [Stackoverflow](https://stackoverflow.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 