# Django Starter | Django Base project clone, save the hustle

This is a simple django CRUD project

## Project Features

1. **Account Functionality:** Complete account management.
2. **PostgreSql Integration:** Utilized as a database.
3. **AWS S3/MinIO Integration:** For file storage.
4. **Redis Integration:** Utilized for caching and message pub/sub.
5. **MailJet Integration:** Used for email services.
6. **Dockerized Project:** Fully containerized for easy deployment.
7. **Kubernetes-native** Kubernetes support also available.
8. **CI/CD Pipeline:** Continuous integration and deployment included using Jenkins.

# Starter Project 

Can be cloned and used as a base project for any django project

-Deployed on AWS / Now in My Own Home Ubuntu Server LTS 22.0 / Hostinger VPS Server

1. Used Ubuntu 22.0 LTS
2. Used Nginx as a Web Proxy Server
3. Used Let's Encrypt Wildcard certificate 
4. Used Acme-dns server for automating renewal of wildcard certificates
5. Used docker to run inside a container since other projects are also running on the same server
6. Used Jenkins for CI/CD Integration Jenkins Server Running at: https://jenkins.arpansahu.me
7. Used AWS Elastic Cache for redis which is not accessible outside AWS, Used Redis Server, hosted on Home Server itself as Redis on Home Server
8. Used PostgresSql Schema based Database, all projects are using single Postgresql. 
9. PostgresSQL is also hosted on Home Server Itself.
10. Using MINIIO as self hosted S3 Storage Server.

## What is Python ?
Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the
use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming 
paradigms, including structured, object-oriented and functional programming.

## What is Django ?
Django is a Python-based free and open-source web framework that follows the model-template-view architectural pattern.

## What is Redis ?
    
Redis is an in-memory data structure project implementing a distributed, in-memory key-value database with optional durability. 
The most common Redis use cases are session cache, full-page cache, queues, leader boards and counting, publish-subscribe, and much more. in this case, we will use Redis as a message broker.


## Tech Stack

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Javascript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://www.javascript.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)
[![Github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://www.github.com/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
![Harbor](https://img.shields.io/badge/HARBOR-TEXT?style=for-the-badge&logo=harbor&logoColor=white&color=blue)(https://goharbor.io/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-326ce5.svg?&style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=Jenkins&logoColor=white)](https://www.jenkins.io/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/en/)
![MINIIO](https://img.shields.io/badge/MINIO-TEXT?style=for-the-badge&logo=minio&logoColor=white&color=%23C72E49)(https://min.io/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![Mail Jet](https://img.shields.io/badge/MAILJET-9933CC?style=for-the-badge&logo=minutemailer&logoColor=white)](https://mailjet.com/)



## Demo

Available at: https://django-starter.arpansahu.me

admin login details:--
username: arpansahu
password: showmecode

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Installation

Installing Pre requisites
```bash
  pip install -r requirements.txt
```

Create .env File and don't forget to add .env to gitignore
```bash
  add variables mentioned in .env.example
```

Making Migrations and Migrating them.
```bash
  python manage.py makemigrations
  python manage.py migrate
```
Run update_data Command
```
  python manage.py update_data
```
Creating Super User
```bash
  python manage.py createsuperuser
```

Installing Redis On Local (For ubuntu) for other Os Please refer to their website https://redis.io/
```bash
  curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
  sudo apt-get update
  sudo apt-get install redis
  sudo systemctl restart redis.service
```
to check if its running or not
```bash
  sudo systemctl status redis
```

Run Server
```bash
  python manage.py runserver

  or 

  gunicorn --bind 0.0.0.0:8016 django_starter.wsgi
```

Use these CACHE settings

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_CLOUD_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

Change settings.py static files and media files settings | Now I have added support for BlackBlaze Static Storage also which also based on AWS S3 protocols 

```python
if not DEBUG:
    BUCKET_TYPE = BUCKET_TYPE

    if BUCKET_TYPE == 'AWS':
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_DEFAULT_ACL = 'public-read'
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400'
        }
        AWS_LOCATION = 'static'
        AWS_QUERYSTRING_AUTH = False
        AWS_HEADERS = {
            'Access-Control-Allow-Origin': '*',
        }
        # s3 static settings
        AWS_STATIC_LOCATION = f'portfolio/{PROJECT_NAME}/static'
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
        STATICFILES_STORAGE = f'{PROJECT_NAME}.storage_backends.StaticStorage'
        # s3 public media settings
        AWS_PUBLIC_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/media'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_PUBLIC_MEDIA_LOCATION}/'
        DEFAULT_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PublicMediaStorage'
        # s3 private media settings
        PRIVATE_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/private'
        PRIVATE_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PrivateMediaStorage'

    elif BUCKET_TYPE == 'BLACKBLAZE':
        AWS_S3_REGION_NAME = 'us-east-005'

        AWS_S3_ENDPOINT = f's3.{AWS_S3_REGION_NAME}.backblazeb2.com'
        AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_ENDPOINT}'
        
        AWS_DEFAULT_ACL = 'public-read'
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }

        AWS_LOCATION = 'static'
        AWS_QUERYSTRING_AUTH = False
        AWS_HEADERS = {
            'Access-Control-Allow-Origin': '*',
        }
        # s3 static settings
        AWS_STATIC_LOCATION = f'portfolio/{PROJECT_NAME}/static'
        STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{AWS_STATIC_LOCATION}/'
        STATICFILES_STORAGE = f'{PROJECT_NAME}.storage_backends.StaticStorage'
        # s3 public media settings
        AWS_PUBLIC_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/media'
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{AWS_PUBLIC_MEDIA_LOCATION}/'
        DEFAULT_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PublicMediaStorage'
        # s3 private media settings
        PRIVATE_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/private'
        PRIVATE_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PrivateMediaStorage'

    elif BUCKET_TYPE == 'MINIO':
        AWS_S3_REGION_NAME = 'us-east-1'  # MinIO doesn't require this, but boto3 does
        AWS_S3_ENDPOINT_URL = 'https://minio.arpansahu.me'
        AWS_DEFAULT_ACL = 'public-read'
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        AWS_LOCATION = 'static'
        AWS_QUERYSTRING_AUTH = False
        AWS_HEADERS = {
            'Access-Control-Allow-Origin': '*',
        }

        # s3 static settings
        AWS_STATIC_LOCATION = f'portfolio/{PROJECT_NAME}/static'
        STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}/{AWS_STATIC_LOCATION}/'
        STATICFILES_STORAGE = f'{PROJECT_NAME}.storage_backends.StaticStorage'

        # s3 public media settings
        AWS_PUBLIC_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/media'
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}/{AWS_PUBLIC_MEDIA_LOCATION}/'
        DEFAULT_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PublicMediaStorage'

        # s3 private media settings
        PRIVATE_MEDIA_LOCATION = 'portfolio/borcelle_crm/private'
        PRIVATE_FILE_STORAGE = 'borcelle_crm.storage_backends.PrivateMediaStorage'
else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.2/howto/static-files/

    STATIC_URL = '/static/'

    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]
```

run below command 

```bash
python manage.py collectstatic
```

and you are good to go


## Custom Django Management Commands

1. Test DB
  Django management command designed to test the basic functionality of the database. It performs a series of CRUD (Create, Read, Update, Delete) operations to ensure the database is working correctly.
```bash
python manage.py test_db
```

2. Test Cache
   Django management command designed to test the basic functionality of the caching system. It performs a set and get operation to ensure the cache is working correctly and validates the expiration of cache entries.
```bash
python manage.py test_cache
```

## Readme Manager

Each repository contains an `update_readme.sh` script located in the `readme_manager` directory. This script is responsible for updating the README file in the repository by pulling in content from various sources.

### What it Does

The `update_readme.sh` script performs the following actions:

1. **Clone Required Files**: Clones the `requirements.txt`, `readme_updater.py`, and `baseREADME.md` files from the `common_readme` repository.
2. **Set Up Python Environment**: Creates and activates a Python virtual environment.
3. **Install Dependencies**: Installs the necessary dependencies listed in `requirements.txt`.
4. **Run Update Script**: Executes the `readme_updater.py` script to update the README file using `baseREADME.md` and other specified sources.
5. **Clean Up**: Deactivates the Python virtual environment and removes it.

### How to Use

To run the `update_readme.sh` script, navigate to the `readme_manager` directory and execute the script:

```bash
cd readme_manager && ./update_readme.sh
```

This will update the `README.md` file in the root of the repository with the latest content from the specified sources.

### Updating Content

If you need to make changes that are specific to the project or project-specific files, you might need to update the content of the partial README files. Here are the files that are included:

- **Project-Specific Files**: 
  - `env.example`
  - `docker-compose.yml`
  - `Dockerfile`
  - `Jenkinsfile`

- **Project-Specific Partial Files**:
  - `INTRODUCTION`: `../readme_manager/partials/introduction.md`
  - `DOC_AND_STACK`: `../readme_manager/partials/documentation_and_stack.md`
  - `TECHNOLOGY QNA`: `../readme_manager/partials/technology_qna.md`
  - `DEMO`: `../readme_manager/partials/demo.md`
  - `INSTALLATION`: `../readme_manager/partials/installation.md`
  - `DJANGO_COMMANDS`: `../readme_manager/partials/django_commands.md`
  - `NGINX_SERVER`: `../readme_manager/partials/nginx_server.md`

These files are specific to the project and should be updated within the project repository.

- **Common Files**:
  - All other files are common across projects and should be updated in the `common_readme` repository.

There are a few files which are common for all projects. For convenience, these are inside the `common_readme` repository so that if changes are made, they will be updated in all the projects' README files.

```python
# Define a dictionary with the placeholders and their corresponding GitHub raw URLs or local paths

include_files = {
    # common files

    "README of Docker Installation": "https://raw.githubusercontent.com/arpansahu/common_readme/main/Docker%20Readme/docker_installation.md",
    "DOCKER_END": "https://raw.githubusercontent.com/arpansahu/common_readme/main/Docker%20Readme/docker_end.md",
    "README of Nginx Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/nginx.md",
    "README of Nginx HTTPS Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/nginx_https.md",
    "README of Jenkins Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Jenkins/Jenkins.md",
    "JENKINS_END": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Jenkins/jenkins_end.md",
    "README of PostgreSql Server With Nginx Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Postgres.md",
    "README of PGAdmin4 Server With Nginx Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Pgadmin.md",
    "README of Portainer Server With Nginx Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Portainer.md",
    "README of Redis Server Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Redis.md",
    "README of Redis Commander Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/RedisComander.md",
    "README of Minio Server Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Minio.md",
    "README of RabbitMQ Server Setup": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Rabbitmq.md",
    "README of Intro": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/Intro.md",
    "README of Readme Manager": "https://raw.githubusercontent.com/arpansahu/common_readme/main/Readme%20manager/readme_manager.md",
    "AWS DEPLOYMENT INTRODUCTION": "https://raw.githubusercontent.com/arpansahu/common_readme/main/Introduction/aws_desployment_introduction.md",
    "STATIC_FILES": "https://raw.githubusercontent.com/arpansahu/common_readme/main/Introduction/static_files_settings.md",
    "README of Harbor" : "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/harbor/harbor.md",
    "HARBOR DOCKER COMPOSE": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/harbor/docker-compose.md",
    "INCLUDE FILES": "https://raw.githubusercontent.com/arpansahu/common_readme/main/include_files.py",
    "MONITORING": "https://raw.githubusercontent.com/arpansahu/arpansahu-one-scripts/main/README.md?token=GHSAT0AAAAAACTHOPGXTRCHN6GJQNHQ43QKZUKVMPA",

    #kubernetes
    "KIND CONFIG MD": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/kind-config.md",
    "KUBELET CONFIG MD": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/kubelet-config.md",
    "DASHBOARD ADMIN USER MD": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashboard-adminuser.md",
    "DASHBOARD ADMIN USER ROLE BIND MD": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashboard-adminuser-rolebinding.md",
    "DASHBOARD SERVICE": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashbord-service.md",
    "DASHBOARD ADMIN SA MD": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashboard-admin-sa.md",
    "DASHBOARD ADMIN SA BINDING": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashboard-admin-sa-binding.md",
    "DASHBOARD ADMIN SA SECRET": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/yaml_md_files/dashboard-admin-sa-secret.md",
    "KUBE WITH DASHBOARD" : "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/kube_with_dashboard.md", 
    "KUBE DEPLOYMENT": "https://raw.githubusercontent.com/arpansahu/common_readme/main/AWS%20Deployment/kubernetes/deployment.md",

    # project files
    "env.example": "../env.example",
    "docker-compose.yml": "../docker-compose.yml",
    "Dockerfile": "../Dockerfile",
    "Jenkinsfile-deploy": "../Jenkinsfile-deploy",
    "Jenkinsfile-build": "../Jenkinsfile-build",
    "DEPLOYMENT YAML": "../deployment.yaml",
    "SERVICE YAML": "../service.yaml",
    
    
    # project partials files
    "INTRODUCTION": "../readme_manager/partials/introduction.md",
    "INTRODUCTION MAIN": "../readme_manager/partials/introduction_main.md",
    "DOC_AND_STACK": "../readme_manager/partials/documentation_and_stack.md",
    "TECHNOLOGY QNA": "../readme_manager/partials/technology_qna.md",
    "DEMO": "../readme_manager/partials/demo.md",
    "INSTALLATION": "../readme_manager/partials/installation.md",
    "DJANGO_COMMANDS": "../readme_manager/partials/django_commands.md",
    "NGINX_SERVER": "../readme_manager/partials/nginx_server.md",
    "SERVICES": "../readme_manager/partials/services.md",
    "JENKINS PROJECT NAME": "../readme_manager/partials/jenkins_project_name.md",
    "JENKINS BUILD PROJECT NAME": "../readme_manager/partials/jenkins_build_project_name.md",
    "STATIC PROJECT NAME": "../readme_manager/partials/static_project_name.md",
    "PROJECT_NAME_DASH" : "../readme_manager/partials/project_name_with_dash.md",
    "PROJECT_DOCKER_PORT": "../readme_manager/partials/project_docker_port.md",
    "PROJECT_NODE_PORT": "../readme_manager/partials/project_node_port.md",
    "DOMAIN_NAME": "../readme_manager/partials/project_domain_name.md"
}
```

Also, remember if you want to include new files, you need to change the `baseREADME` file and the `include_files` array in the `common_readme` repository itself.

## Deployment on AWS EC2/ Home Server Ubuntu 22.0 LTS/ Hostinger VPS Server

Previously This project was hosted on Heroku, but so I started hosting this and all other projects in a 
Single EC2 Machine, which cost me a lot, so now I have shifted all the projects to my own Home Server with 
Ubuntu 22.0 LTS Server, except for portfolio project at https://www.arpansahu.me along with Nginx 


Now there is an EC2 server running with an nginx server and arpansahu.me portfolio
Nginx forwarded https://arpansahu.me/ to the Home Server 

Multiple Projects are running inside dockers so all projects are dockerized.
You can refer to all projects at https://www.arpansahu.me/projects

Every project has a different port on which it runs predefined inside Dockerfile and docker-compose.yml

![EC2 and Home Server along with Nginx, Docker and Jenkins Arrangement](https://github.com/arpansahu/common_readme/blob/main/Images/ec2_and_home_server.png)

Note: Update as of Aug 2023, I have decided to make some changes to my lifestyle, and from now I will be constantly on the go
 from my experience with running a free EC2 server for arpansahu. me and nginx in it and then using another home server
 with all the other projects hosted, my experience was
      
 1. Downtime due to Broadband Service Provider Issues
 2. Downtime due to Weather Sometimes
 3. Downtime due to Machine Breakdown
 4. Downtime due to Power Cuts (even though I had an inverted battery setup for my room)
 5. Remotely it would be harder to fix these problems 

 and due to all these reasons I decided to shift all the projects to a single EC2 Server, at first I was using t2.medium which costs more than 40$ a month 
 then I switched to t2.small and it only costs you 15$ if we take pre-paid plans prices can be slashed much further. 

 Then again I shifted to Hostinger VPS which was more cost-friendly than EC2 Server. On Jan 2024

Now My project arrangements look something similar to this

![EC2 Sever along with Nginx, Docker and Jenkins Arrangement](https://github.com/arpansahu/common_readme/blob/main/Images/One%20Server%20Configuration%20for%20arpanahuone.png)

### Step 1: Dockerize

#### Installing Redis Commander

Reference: https://docs.docker.com/engine/install/ubuntu/

1. Setting up the Repository
   1. Update the apt package index and install packages to allow apt to use a repository over HTTPS: 

       ```bash
       sudo apt-get update
    
       sudo apt-get install \
       ca-certificates \
       curl \
       gnupg \
       lsb-release
       ```

   2. Add Docker’s official GPG key:

       ```bash
       sudo mkdir -p /etc/apt/keyrings
       
       curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
       ```

   3. Use the following command to set up the repository:

       ```bash
       echo \
         "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
         $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
       ```

2. Install Docker Engine
    
   1. Update the apt package index:

      ```bash
       sudo apt-get update
      ```
    
      1. Receiving a GPG error when running apt-get update?

         Your default umask may be incorrectly configured, preventing detection of the repository public key file. Try granting read permission for the Docker public key file before updating the package index:
         
            ```bash
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            sudo apt-get update
            ```
            
   2. Install Docker Engine, containerd, and Docker Compose.

        ```bash
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
        ```


   3. Start Docker Engine

        ```bash
        sudo systemctl start docker
        ```

    4. Enable Docker Engine

        ```bash
        sudo systemctl enable docker
        ```
   
    5. Verify that the Docker Engine installation is successful by running the hello-world image:

        ```bash
         sudo docker run hello-world
        ```

Now in your Git Repository

Create a file named Dockerfile with no extension and add following lines in it

### Step 2: Private Docker Registry


## Harbor (Self hosted Private Docker Registry)

Harbor is an open-source container image registry that secures images with role-based access control, scans images for vulnerabilities, and signs images as trusted. It extends the Docker Distribution by adding functionalities usually required by enterprise users, such as security, identity, and management.

### Installing Harbor

1. **Download Harbor:**
   Go to the Harbor releases page and download the latest offline installer tarball, e.g., harbor-offline-installer-<version>.tgz.
   Alternatively, you can use wget to download it directly:

    ```bash
    wget https://github.com/goharbor/harbor/releases/download/v2.4.2/harbor-offline-installer-v2.4.2.tgz
    ```

2. **Extract the tarball:**

    ```bash
    tar -zxvf harbor-offline-installer-v2.4.2.tgz
    cd harbor
    ```

3. **Configure Harbor:**
    Note: I am having multiple projects running in single machine and 1 nginx is handling subdomains and domain arpansahu.me. Similarly i want my harbor to be accessible 
    from harbor.arpansahu.me. 

    1.	Copy and edit the configuration file:

        ```bash
        cp harbor.yml.tmpl harbor.yml
        vi harbor.yml
        ```

    2. Edit harbor.yml 
        ```bash
        # Configuration file of Harbor

        # The IP address or hostname to access admin UI and registry service.
        # DO NOT use localhost or 127.0.0.1, because Harbor needs to be accessed by external clients.
        hostname: harbor.arpansahu.me

        # http related config
        http:
        # port for http, default is 80. If https enabled, this port will redirect to https port
        port: 8601
        # https related config
        https:
        # https port for harbor, default is 443
        port: 8602
        # The path of cert and key files for nginx
        certificate: /etc/letsencrypt/live/arpansahu.me/fullchain.pem 
        private_key: /etc/letsencrypt/live/arpansahu.me/privkey.pem


        .......
        more lines
        .......
        ```

        There are almost 250 lines of code in this yml file but we have to make sure to edit this much configuration particularly 
        default http port is 80 and https port is 443 since default harbor docker-compose.yml have nginx setup also. But we have our own nginx
        thats why we will change these both ports to available free port on the machine. I picked 8081 for http and 8443 for https. You can choose accordingly.


    3. Edit docker-compose.yml

        Here docker-compose.yml file only be available after running the below install command

        ```bash
            sudo ./install.sh --with-notary --with-trivy --with-chartmuseum
        ```

        Note: If docker compose is not available you need to install it

            1. Installing docker compose
                ```bash
                    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                ```
            2. Next, set the correct permissions so that the docker-compose command is executable:

                ```bash
                    sudo chmod +x /usr/local/bin/docker-compose
                ```
            
            3. To verify that the installation was successful, you can run:

                ```bash
                    docker-compose --version
                ```

        It might get success then you can see this file

        ```bash
            vi docker-compose.yml
        ```

        ```bash
                version: '2.3'
        services:
        log:
            image: goharbor/harbor-log:v2.4.2
            container_name: harbor-log
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - DAC_OVERRIDE
            - SETGID
            - SETUID
            volumes:
            - /var/log/harbor/:/var/log/docker/:z
            - type: bind
                source: ./common/config/log/logrotate.conf
                target: /etc/logrotate.d/logrotate.conf
            - type: bind
                source: ./common/config/log/rsyslog_docker.conf
                target: /etc/rsyslog.d/rsyslog_docker.conf
            ports:
            - 127.0.0.1:1514:10514
            networks:
            - harbor
        registry:
            image: goharbor/registry-photon:v2.4.2
            container_name: registry
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            volumes:
            - /data/registry:/storage:z
            - ./common/config/registry/:/etc/registry/:z
            - type: bind
                source: /data/secret/registry/root.crt
                target: /etc/registry/root.crt
            - type: bind
                source: ./common/config/shared/trust-certificates
                target: /harbor_cust_cert
            networks:
            - harbor
            depends_on:
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "registry"
        registryctl:
            image: goharbor/harbor-registryctl:v2.4.2
            container_name: registryctl
            env_file:
            - ./common/config/registryctl/env
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            volumes:
            - /data/registry:/storage:z
            - ./common/config/registry/:/etc/registry/:z
            - type: bind
                source: ./common/config/registryctl/config.yml
                target: /etc/registryctl/config.yml
            - type: bind
                source: ./common/config/shared/trust-certificates
                target: /harbor_cust_cert
            networks:
            - harbor
            depends_on:
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "registryctl"
        postgresql:
            image: goharbor/harbor-db:v2.4.2
            container_name: harbor-db
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - DAC_OVERRIDE
            - SETGID
            - SETUID
            volumes:
            - /data/database:/var/lib/postgresql/data:z
            networks:
            harbor:
            harbor-notary:
                aliases:
                - harbor-db
            env_file:
            - ./common/config/db/env
            depends_on:
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "postgresql"
            shm_size: '1gb'
        core:
            image: goharbor/harbor-core:v2.4.2
            container_name: harbor-core
            env_file:
            - ./common/config/core/env
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - SETGID
            - SETUID
            volumes:
            - /data/ca_download/:/etc/core/ca/:z
            - /data/:/data/:z
            - ./common/config/core/certificates/:/etc/core/certificates/:z
            - type: bind
                source: ./common/config/core/app.conf
                target: /etc/core/app.conf
            - type: bind
                source: /data/secret/core/private_key.pem
                target: /etc/core/private_key.pem
            - type: bind
                source: /data/secret/keys/secretkey
                target: /etc/core/key
            - type: bind
                source: ./common/config/shared/trust-certificates
                target: /harbor_cust_cert
            networks:
            harbor:
            harbor-notary:
            harbor-chartmuseum:
                aliases:
                - harbor-core
            depends_on:
            - log
            - registry
            - redis
            - postgresql
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "core"
        portal:
            image: goharbor/harbor-portal:v2.4.2
            container_name: harbor-portal
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            - NET_BIND_SERVICE
            volumes:
            - type: bind
                source: ./common/config/portal/nginx.conf
                target: /etc/nginx/nginx.conf
            networks:
            - harbor
            depends_on:
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "portal"
        jobservice:
            image: goharbor/harbor-jobservice:v2.4.2
            container_name: harbor-jobservice
            env_file:
            - ./common/config/jobservice/env
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            volumes:
            - /data/job_logs:/var/log/jobs:z
            - type: bind
                source: ./common/config/jobservice/config.yml
                target: /etc/jobservice/config.yml
            - type: bind
                source: ./common/config/shared/trust-certificates
                target: /harbor_cust_cert
            networks:
            - harbor
            depends_on:
            - core
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "jobservice"
        redis:
            image: goharbor/redis-photon:v2.4.2
            container_name: redis
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            volumes:
            - /data/redis:/var/lib/redis
            networks:
            harbor:
            harbor-chartmuseum:
                aliases:
                - redis
            depends_on:
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "redis"
        proxy:
            image: goharbor/nginx-photon:v2.4.2
            container_name: nginx
            restart: always
            cap_drop:
            - ALL
            cap_add:
            - CHOWN
            - SETGID
            - SETUID
            - NET_BIND_SERVICE
            volumes:
            - ./common/config/nginx:/etc/nginx:z
            - /data/secret/cert:/etc/cert:z
            - type: bind
                source: ./common/config/shared/trust-certificates
                target: /harbor_cust_cert
            networks:
            - harbor
            - harbor-notary
            ports:
            - 8601:8080
            - 8602:8443
            - 4443:4443
            depends_on:
            - registry
            - core
            - portal
            - log
            logging:
            driver: "syslog"
            options:
                syslog-address: "tcp://localhost:1514"
                tag: "proxy"
        notary-server:
            image: goharbor/notary-server-photon:v2.4.2
            container_name: notary-server
            restart: always
            networks:
            - notary-sig
            - harbor-notary
            volumes:
            - ./common/config/notary:/etc/notary:z
            - type: bind
                source: /data/secret/notary/notary-signer-ca
        ```


        As you can see the ports we used in harbor.yml are configured here and nginx service have been removed.
        ports:
          - 8601:8080
          - 8602:8443
          - 4443:4443

4. **Run the Harbor install script:**
   
   ```bash
    sudo ./install.sh --with-notary --with-trivy --with-chartmuseum
   ```

5. **Complete Setup:**
   Follow the on-screen instructions to complete the setup process. You may choose to deploy a local agent for better performance, but it's not required for basic functionality.

Once the setup is complete, you should have access to the Portainer dashboard, where you can manage and monitor your Docker containers, images, volumes, and networks through a user-friendly web interface.

Keep in mind that the instructions provided here assume a basic setup. For production environments, it's recommended to secure the Portainer instance, such as by using HTTPS and setting up authentication. Refer to the [Portainer documentation](https://documentation.portainer.io/) for more advanced configurations and security considerations.


### Configuring Nginx as Reverse proxy

1. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```

2. Add this server configuration

    ```bash
    server {
        listen         80;
        server_name    harbor.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }

        location / {
            proxy_pass              https://127.0.0.1:8443;
            proxy_set_header        Host $host;
            proxy_set_header    X-Forwarded-Proto $scheme;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

3. Test the Nginx Configuration

    ```bash
    sudo nginx -t
    ```

4. Reload Nginx to apply the new configuration

    ```bash
    sudo systemctl reload nginx
    ```

### Access Harbor UI

Harbor UI can be accessed here : https://portainer.arpansahu.me/

### Connecting Docker Registry 

Login to Docker Registry

You can connect to my Docker Registry  

```bash
    docker login harbor.arpansahu.me
```

### Pushing Image to Harbor Docker Registry

1. Tag Image

```bash
    docker tag image_name harbor.arpansahu.me/library/image_name:latest
```

2. Push Image

```bash
    docker push harbor.arpansahu.me/library/image_name:latest
```

### Create Image Retention Policy

Inside project, default project is library 
 
Go to >>> Library project
Go to >>> Policy
Click on >>> Add Policy

For the repositories == matching **
By artifact count or number of days == retain the most recently pulled # artifacts  Count = 2/3 no of last no of images 
tags == matching      Untagged artifacts = ticketed

This is one time task for entire project 

Same as below

![Add Retention Rule](https://github.com/arpansahu/common_readme/blob/main/AWS%20Deployment/harbor/retention_rule_add.png)

After adding rule schedule it as per requirement as below

![Add Retention Rule S](https://github.com/arpansahu/common_readme/blob/main/AWS%20Deployment/harbor/retention_rule_schedule.png)

```bash
FROM python:3.10.7

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8016

CMD bash -c "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8016 django_starter.wsgi"
```

Create a file named docker-compose.yml and add following lines in it

```bash
version: '3'

services:
  web:
    build:  # This section will be used when running locally
      context: .
      dockerfile: Dockerfile
    image: harbor.arpansahu.me/library/django_starter:latest
    env_file: ./.env
    command: bash -c "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8016 django_starter.wsgi"
    container_name: django_starter
    volumes:
      - .:/django_starter
    ports:
      - "8016:8016"
    restart: unless-stopped
```

### **What is Difference in Dockerfile and docker-compose.yml?**

A Dockerfile is a simple text file that contains the commands a user could call to assemble an image whereas Docker Compose is a tool for defining and running multi-container Docker applications.

Docker Compose define the services that make up your app in docker-compose.yml so they can be run together in an isolated environment. It gets an app running in one command by just running docker-compose up. Docker compose uses the Dockerfile if you add the build command to your project’s docker-compose.yml. Your Docker workflow should be to build a suitable Dockerfile for each image you wish to create, then use compose to assemble the images using the build command.

Running Docker 

```bash
docker compose up --build --detach 
```

--detach tag is for running the docker even if terminal is closed
if you remove this tag it will be attached to terminal, and you will be able to see the logs too

--build tag with docker compose up will force image to be rebuild every time before starting the container

### Step 3: Containerizing with Kubernetes

## Installing Kubernetes cluster and Setting A Dashboard

### Install Kind and Kubernetes CLI (kubectl)

1.	Install Kind:

    ```bash
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    ```

2. Install kubectl:

    ```bash
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    ```

### Create a Kind Cluster with Port Mappings

1. 	Create a configuration file for Kind:

    ```bash
        touch kind-config.yaml
        vi kind-config.yaml
    ```

    paste the below code into the file

    ```yaml
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    nodes:
    - role: control-plane
      extraPortMappings:
      - containerPort: 80
        hostPort: 7800
      - containerPort: 443
        hostPort: 7801
      extraMounts:
      - hostPath: /etc/kubernetes/kubelet-config.yaml
        containerPath: /var/lib/kubelet/config.yaml
    ```

2. 	Create a kubelet configuration file for Kind:

    ```bash
        touch kubelet-config.yaml
        vi kubelet-config.yaml
    ```

    paste the below code into the file

    ```yaml
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    nodes:
    - role: control-plane
      extraPortMappings:
      - containerPort: 80
        hostPort: 7800
      - containerPort: 443
        hostPort: 7801
      extraMounts:
      - hostPath: /etc/kubernetes/kubelet-config.yaml
        containerPath: /var/lib/kubelet/config.yaml
    ```

3. Create the Kind cluster:

    ```bash
        kind create cluster --config kind-config.yaml
    ```

###  Label the Node

1. Label the node to match the required node selectors:

    ```bash
        kubectl label node kind-control-plane ingress-ready=true
        kubectl label node kind-control-plane kubernetes.io/os=linux
    ```

### Deploy the Kubernetes Dashboard

1. Create the kubernetes-dashboard namespace:

    ```bash
        kubectl create namespace kubernetes-dashboard
    ```

2. Deploy the Kubernetes Dashboard:

    ```bash
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
    ```

3. Create an admin user:

    Create a file named dashboard-adminuser.yaml

    ```bash
        touch dashboard-adminuser.yaml
        vi dashboard-adminuser.yaml
    ```

    copy and paste below content into it

    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: admin-user
      namespace: kubernetes-dashboard
    ```

4. Create ClusterRoleBinding:

    Create a file named dashboard-adminuser-rolebinding.yaml

    ```bash
        touch dashboard-adminuser-rolebinding.yaml
        vi dashboard-adminuser-rolebinding.yaml
    ```

    copy and paste below content into it

    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: admin-user
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: cluster-admin
    subjects:
    - kind: ServiceAccount
      name: admin-user
      namespace: kubernetes-dashboar
    ```
5. Apply both the files

    ```bash
        kubectl apply -f dashboard-adminuser.yaml
        kubectl apply -f dashboard-adminuser-rolebinding.yaml
    ```

6. Get the admin user token:

    ```bash
        kubectl -n kubernetes-dashboard create token admin-user
    ```

### Expose the Kubernetes Dashboard Service using NodePort

1. Edit the Kubernetes Dashboard service:

    ```bash
        kubectl -n kubernetes-dashboard edit service kubernetes-dashboard
    ```

2. Modify the service to use NodePort (do not copy blindly just make the mentioned changes):

    ```yaml
    # Please edit the object below. Lines beginning with a '#' will be ignored,
    # and an empty file will abort the edit. If an error occurs while saving this file will be
    # reopened with the relevant failures.
    #
    apiVersion: v1
    kind: Service
    metadata:
      annotations:
        kubectl.kubernetes.io/last-applied-configuration: |
          {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"k8s-app":"kubernetes-dashboard"},"name":"kubernetes-dashboard","namespace":"kubernetes-dashboard"},"spec":{"ports":[{"port":443,"targetPort":8443}],"selector":{"k8s-app":"kubernetes-dashboard"}}}
      creationTimestamp: "2024-07-06T11:14:04Z"
      labels:
        k8s-app: kubernetes-dashboard
      name: kubernetes-dashboard
      namespace: kubernetes-dashboard
      resourceVersion: "1668"
      uid: e4211a82-97a1-4a65-b52e-be3bcb3b5150
    spec:
      clusterIP: 10.96.128.226
      clusterIPs:
      - 10.96.128.226
      externalTrafficPolicy: Cluster
      internalTrafficPolicy: Cluster
      ipFamilies:
      - IPv4
      ipFamilyPolicy: SingleStack
      ports:
      - nodePort: 31000
        port: 443
        protocol: TCP
        targetPort: 8443
      selector:
        k8s-app: kubernetes-dashboard
      sessionAffinity: None
      type: NodePort
    status:
      loadBalancer: {}
    ```


### Configure On-Premises Nginx as a Reverse Proxy

1. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```


2. To know Internal ip of kind cluster

    ```bash
        kubectl get nodes -o wide
    ```

3. Add this server configuration

    ```bash
    server {
        listen         80;
        server_name    kube.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }

        location / {
            proxy_pass              proxy_pass https://<INTERNAL-IP>:31000;
            proxy_set_header        Host $host;
            proxy_set_header    X-Forwarded-Proto $scheme;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```


4. Test the Nginx Configuration

    ```bas
    sudo nginx -t
    ```

5. Reload Nginx to apply the new configuration

    ```bash
    sudo systemctl reload nginx
    ```

### Get the admin user token for login:

    Access:  https://kube.arpansahu.me

    then generate token from host server by running the following command

    ```bash
        kubectl -n kubernetes-dashboard create token admin-user
    ```

    Note: The token generated by this command will have expiry and you may need to generate token again and again

### Generate token without expiry

1.	Delete the old ServiceAccount and ClusterRoleBinding:

    ```bash
        kubectl -n kubernetes-dashboard delete serviceaccount admin-user
        kubectl delete clusterrolebinding admin-user
    ```

2. Create and apply the ServiceAccount:

    ```bash
        touch dashboard-admin-sa.yaml
        vi dashboard-admin-sa.yaml
    ```

    copy this and past it in the file

    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: dashboard-admin-sa
      namespace: kubernetes-dashboard
    ```

3. Create and apply the ClusterRoleBinding:

    ```bash
        touch dashboard-admin-sa-binding.yaml
        vi dashboard-admin-sa-binding.yaml
    ```

    copy this and past it in the file

    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: dashboard-admin-sa-binding
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: cluster-admin
    subjects:
    - kind: ServiceAccount
      name: dashboard-admin-sa
      namespace: kubernetes-dashboard
    ``` 

4. Create the secret for the ServiceAccount:

    ```bash
        touch dashboard-admin-sa-secret.yaml
        vi dashboard-admin-sa-secret.yaml
    ```

    copy this and past it in the file

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: dashboard-admin-sa-token
      namespace: kubernetes-dashboard
      annotations:
        kubernetes.io/service-account.name: dashboard-admin-sa
    type: kubernetes.io/service-account-token
    ``` 


5. Apply all the files

    ```bash
        kubectl apply -f dashboard-admin-sa.yaml
        kubectl apply -f dashboard-admin-sa-binding.yaml
        kubectl apply -f dashboard-admin-sa-secret.yaml
    ```

6. Check the Secret

    ```bash
        kubectl -n kubernetes-dashboard get secret dashboard-admin-sa-token
    ```

7. Patch the ServiceAccount:

    ```bash
        kubectl -n kubernetes-dashboard patch serviceaccount dashboard-admin-sa -p '{"secrets":[{"name":"dashboard-admin-sa-token"}]}'
    ```

8. Retrieve the token:

    ```bash
        SECRET_NAME=$(kubectl -n kubernetes-dashboard get sa dashboard-admin-sa -o jsonpath="{.secrets[0].name}")
        kubectl -n kubernetes-dashboard get secret $SECRET_NAME -o jsonpath="{.data.token}" | base64 --decode
    ```

### Accessing 

Access the Dashboard

https://kube.arpansahu.me

you will be required to fill token for login

Access the cluster via Cli using kubectl

```bash
    kubectl get nodes
```
### Deployment

1. Create Harbor Secret

```yaml
kubectl create secret docker-registry harbor-registry-secret \
  --docker-server=harbor.arpansahu.me \
  --docker-username=HARBOR_USERNAME \
  --docker-password=HARBOR_PASSWORD \
  --docker-email=YOUR_EMAIL_ID
```

2. Create deployment.yaml file and fill it with the below contents.

```yaml
  apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-starter-app
  labels:
    app: django-starter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: django-starter
  template:
    metadata:
      labels:
        app: django-starter
    spec:
      imagePullSecrets:
        - name: harbor-registry-secret
      containers:
        - image: harbor.arpansahu.me/library/django_starter:latest
          name: django-starter
          envFrom:
            - secretRef:
                name: django-starter-secret
          ports:
            - containerPort: 8016
              name: gunicorn
```

3. Create a service.yaml file and fill it with the below contents.

```yaml
  apiVersion: v1
kind: Service
metadata:
  name: django-starter-service
spec:
  selector:
    app: django-starter
  ports:
    - protocol: TCP
      port: 8016
      targetPort: 8016
      nodePort: 32016
  type: NodePort
```

4. Create Env Secret for the project

```
  kubectl create secret generic <SECRET_NAME> --from-env-file=/root/projectenvs/<PROJECT_NAME>/.env
```

### Step 4: Serving the requests from Nginx

#### Installing the Nginx server

```bash
sudo apt-get install nginx
```

Starting Nginx and checking its status 

```bash
sudo systemctl start nginx
sudo systemctl status nginx
```

#### Modify DNS Configurations

Add these two records to your DNS Configurations

```bash
A Record	*	0.227.49.244 (public IP of ec2)	Automatic
A Record	@	0.227.49.244 (public IP of ec2)	Automatic
```

Note: now you will be able to see nginx running page if you open the public IP of the machine
IP
Make Sure your EC2 security Group have these entry inbound rules 

```bash
random-hash-id	IPv4	HTTP	TCP	80	0.0.0.0/0	–
```

Open a new Nginx Configuration file name can be anything i am choosing arpansahu since my domain is arpansahu.me. there is already a default configuration file but we will leave it like that only

```bash
sudo vi /etc/nginx/sites-available/arpansahu
```

paste this content in the above file

```bash
server_tokens               off;
access_log                  /var/log/nginx/supersecure.access.log;
error_log                   /var/log/nginx/supersecure.error.log;

server {
  server_name               arpansahu.me;        
  listen                    80;
  location / {
    proxy_pass              http://{ip_of_home_server/localhost}:8000;
    proxy_set_header        Host $host;
  }
}
```

This single Nginx File will be hosting all the multiple projects which I have listed before also.

Checking if the configurations file is correct

```bash
sudo service nginx configtest /etc/nginx/sites-available/arpansahu
```

Now you need to symlink this file to the sites-enabled directory:

```bash
cd /etc/nginx/sites-enabled
sudo ln -s ../sites-available/arpansahu
```

Restarting Nginx Server 

```bash
sudo systemctl restart nginx
```

Now it's time to enable HTTPS for this server

### Step 5: Enabling HTTPS 


1. Base Domain:  Enabling HTTPS for base domain only or a single subdomain

    To allow visitors to access your site over HTTPS, you’ll need an SSL/TLS certificate that sits on your web server. Certificates are issued by a Certificate Authority (CA). We’ll use a free CA called Let’s Encrypt. To install the certificate, you can use the Certbot client, which gives you an utterly painless step-by-step series of prompts.
    Before starting with Certbot, you can tell Nginx up front to disable TLS versions 1.0 and 1.1 in favour of versions 1.2 and 1.3. TLS 1.0 is end-of-life (EOL), while TLS 1.1 contained several vulnerabilities that were fixed by TLS 1.2. To do this, open the file /etc/nginx/nginx.conf. Find the following line:

    Open nginx.conf file end change ssl_protocols 
    
    ```bash
    sudo vi /etc/nginx/nginx.conf
    
    From ssl_protocols TLSv1 TLSv1.1 TLSv1.2; to ssl_protocols TLSv1.2 TLSv1.3;
    ```
    
    Use this command to verify if nginx.conf file is correct or not
    
    ```bash
    sudo nginx -t
    ```
    
    Now you’re ready to install and use Certbot, you can use Snap to install Certbot:
    
    ```bash
    sudo snap install --classic certbot
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
    ```
    
    Now installing certificate
    
    ```bash
    sudo certbot --nginx --rsa-key-size 4096 --no-redirect
    ```
    
    It will ask for the domain name then you can enter your base domain 
    I have generated SSL for arpansahu.me
    
    Then a few questions will be asked answer them all and your SSL certificate will be generated

    Now These lines will be added to your # Nginx configuration: /etc/nginx/sites-available/arpansahu
    
    ```bash
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/www.supersecure.codes/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.supersecure.codes/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    ```
    
    Redirecting HTTP to HTTPS
    Open the nginx configuration file  and make it like this

    ```bash
    sudo vi /etc/nginx/sites-available/arpansahu
    ```

    ```bash
    server_tokens               off;
    access_log                  /var/log/nginx/supersecure.access.log;
    error_log                   /var/log/nginx/supersecure.error.log;
     
    server {
      server_name               arpansahu.me;
      listen                    80;
      return                    307 https://$host$request_uri;
    }
    
    server {
    
      location / {
        proxy_pass              http://{ip_of_home_server/ localhost}:8000;
        proxy_set_header        Host $host;
        
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }                          
    ``` 
    
    You can dry run and check whether it's renewal is working or not

    ```bash
    sudo certbot renew --dry-run
    ```
    
    Note: this process was for arpansahu.me and not for all subdomains.
    For all subdomains, we will have to set a wildcard SSL certificate


2. Enabling a Wildcard certificate

    Here we will enable an SSL certificate for all subdomains at once
        
    Run the following Command

    ```bash
    sudo certbot certonly --manual --preferred-challenges dns
    ```
    
    Again you will be asked domain name and here you will use *.arpansahu.me. and second domain you will use is
    arpansahu.me.
    
    Now, you should have a question in your mind about why we are generating SSL for arpansahu.me separately.
    It's because Let's Encrypt does not include a base domain with wildcard certificates for subdomains.

    After running the above command you will see a message similar to this
      
    ```bash
    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Please enter the domain name(s) you would like on your certificate (comma and/or
    space separated) (Enter 'c' to cancel): *.arpansahu.me
    Requesting a certificate for *.arpansahu.me
    
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Please deploy a DNS TXT record under the name:
    
    _acme-challenge.arpansahu.me.
    
    with the following value:
    
    dpWCxvq3mARF5iGzSfaRNXwmdkUSs0wgsTPhSaX1gK4
    
    Before continuing, verify the TXT record has been deployed. Depending on the DNS
    provider, this may take some time, from a few seconds to multiple minutes. You can
    check if it has finished deploying with the aid of online tools, such as Google
    Admin Toolbox: https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.arpansahu.me.
    Look for one or more bolded line(s) below the line '; ANSWER'. It should show the
    value(s) you've just added.
   
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Press Enter to Continue
    ```
   
    You will be given a DNS challenge called ACME challenger you have to create a DNS TXT record in DNS.
    Similar to the below record.
        
    ```bash
    TXT Record  _acme-challenge dpWCxvq3mARF5iGzSfaRNXwmdkUSs0wgsTPhSaX1gK4 5 Automatic
    ```
    
    Now, use this URL to verify whether records are updated or not

    https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.arpansahu.me (arpansahu.me is domain)

    If it's verified then press enter the terminal as mentioned above
        
    Then your certificate will be generated

    ```bash
    Successfully received a certificate.
    The certificate is saved at: /etc/letsencrypt/live/arpansahu.me-0001/fullchain.pem            (use this in your nginx configuration file)
    Key is saved at:         /etc/letsencrypt/live/arpansahu.me-0001/privkey.pem
    This certificate expires on 2023-01-20.
    These files will be updated when the certificate is renewed.
    ```
        
    You can notice here, the certificate generated is arpansahu.me-0001 and not arpansahu.me
    because we already generated a certificate named arpansahu.me
        
    So remember to delete it before generating this wildcard certificate
    using command

    ```bash
    sudo certbot delete
    ```
        
    Note: This certificate will not be renewed automatically. Auto-renewal of --manual certificates requires the use of an authentication hook script (--manual-auth-hook) but one was not provided. To renew this certificate, repeat this same Certbot command before the certificate's expiry date.

3. Generating Wildcard SSL certificate and Automating its renewal

    1. Modify your ec2 inbound rules 
    
      ```bash
      –	sgr-0219f1387d28c96fb	IPv4	DNS (TCP)	TCP	53	0.0.0.0/0	–	
      –	sgr-01b2b32c3cee53aa9	IPv4	SSH	TCP	22	0.0.0.0/0	–
      –	sgr-0dfd03bbcdf60a4f7	IPv4	HTTP	TCP	80	0.0.0.0/0	–
      –	sgr-02668dff944b9b87f	IPv4	HTTPS	TCP	443	0.0.0.0/0	–
      –	sgr-013f089a3f960913c	IPv4	DNS (UDP)	UDP	53	0.0.0.0/0	–
      ```
    
   2. Install acme-dns Server

      * Create a folder for acme-dns and change the directory

        ```bash
         sudo mkdir /opt/acme-dns
         cd !$
        ```

      * Download and extract tar with acme-dns from GitHub

        ```bash
        sudo curl -L -o acme-dns.tar.gz \
        https://github.com/joohoi/acme-dns/releases/download/v0.8/acme-dns_0.8_linux_amd64.tar.gz
        sudo tar -zxf acme-dns.tar.gz
        ```

      * List files

        ```bash
        sudo ls
        ```

      * Clean Up

        ```bash
        sudo rm acme-dns.tar.gz
        ```

      * Create a soft link

        ```bash
        sudo ln -s \
        /opt/acme-dns/acme-dns /usr/local/bin/acme-dns
        ```

      * Create a minimal acme-dns user

         ```bash
         sudo adduser \
         --system \	
         --gecos "acme-dns Service" \
         --disabled-password \
         --group \
         --home /var/lib/acme-dns \
         acme-dns
        ```

      * Update default acme-dns config compared with IP from the AWS console. Can't bind to the public address need to use private one.

        ```bash
        IP addr
	  
        sudo mkdir -p /etc/acme-dns
	  
        sudo mv /opt/acme-dns/config.cfg /etc/acme-dns/
	  
        sudo vim /etc/acme-dns/config.cfg
        ```
      
      * Replace

        ```bash
        listen = "127.0.0.1:53” to listen = “private IP of the ec2 instance” 172.31.93.180:53(port will be 53)
 
        Similarly, Edit other details mentioned below  

        # domain name to serve the requests off of
        domain = "auth.arpansahu.me"
        # zone name server
        nsname = "auth.arpansahu.me"
        # admin email address, where @ is substituted with .
        nsadmin = "admin@arpansahu.me"


        records = [
          # domain pointing to the public IP of your acme-dns server
           "auth.arpansahu.me. A 44.199.177.138. (public elastic IP)”,
          # specify that auth.example.org will resolve any *.auth.example.org records
           "auth.arpansahu.me. NS auth.arpansahu.me.”,
        ]
	
        [api]
        # listen IP eg. 127.0.0.1
        IP = "127.0.0.1”. (Changed)

        # listen port, eg. 443 for default HTTPS
        port = "8080" (Changed).         ——— We will use port 8090 because we will also use Jenkins which will be running on 8080 port
        # possible values: "letsencrypt", "letsencryptstaging", "cert", "none"
        tls = "none"   (Changed)

        ```

      * Move the systemd service and reload

        ```bash
        cat acme-dns.service
     
        sudo mv \
        acme-dns.service /etc/systemd/system/acme-dns.service
	  
        sudo systemctl daemon-reload
        ```

      * Start and enable acme-dns server

        ```bash
        sudo systemctl enable acme-dns.service
        sudo systemctl start acme-dns.service
        ```

      * Check acme-dns for possible errors

        ```bash
        sudo systemctl status acme-dns.service
        ```

      * Use journalctl to debug in case of errors

         ```bash
         journalctl --unit acme-dns --no-pager --follow
         ```

      * Create A record for your domain

         ```bash
         auth.arpansahu.me IN A <public-IP>
         ```

      * Create NS record for auth.arpansahu.me pointing to auth.arpansahu.me. This means, that auth.arpansahu.me is
        responsible for any *.auth.arpansahu.me records

        ```bash
        auth.arpansahu.me IN NS auth.arpansahu.me
        ```

      * Your DNS record will be looking like this

        ```bash
        A Record	auth	44.199.177.138	Automatic	
        NS Record	auth	auth.arpansahu.me.	Automatic
        ```

      * Test acme-dns server (Split the screen)

        ```bash
        journalctl -u acme-dns --no-pager --follow
        ```

      * From the local host try to resolve the random DNS record

        ```bash
        dig api.arpansahu.me
        dig api.auth.arpansahu.me
        dig 7gvhsbvf.auth.arpansahu.me
        ``` 
        
   3. Install acme-dns-client 

     ```bash
     sudo mkdir /opt/acme-dns-client
     cd !$
    
     sudo curl -L \
     -o acme-dns-client.tar.gz \
     https://github.com/acme-dns/acme-dns-client/releases/download/v0.2/acme-dns-client_0.2_linux_amd64.tar.gz
    
     sudo tar -zxf acme-dns-client.tar.gz
     ls
     sudo rm acme-dns-client.tar.gz
     sudo ln -s \
     /opt/acme-dns-client/acme-dns-client /usr/local/bin/acme-dns-client 
     ```

   4. Install Certbot

     ```bash
     cd
     sudo snap install core; sudo snap refresh core
     sudo snap install --classic certbot
     sudo ln -s /snap/bin/certbot /usr/bin/certbot
     ```

    Note: you can skip this step if Certbot is already installed

    5. Get Letsencrypt Wildcard Certificate
       * Create a new acme-dns account for your domain and set it up

         ```bash
         sudo acme-dns-client register \
         -d arpansahu.me -s http://localhost:8090
         ```

        The above command is old now we will use the new command 

         ```bash
         sudo acme-dns-client register \
          -d arpansahu.me \
          -allow 0.0.0.0/0 \
          -s http://localhost:8080
         ```

         Note: When we edited acme-dns config file there we mentioned the port 8090 and thats why we are using this port here also
         
       * Creating Another DNS Entry 

         ```bash
         CNAME Record	_acme-challenge	e6ac0f0a-0358-46d6-a9d3-8dd41f44c7ec.auth.arpansahu.me.	Automatic
         ```

        Since the last update in  the last step now two more entries should be added 

         ```bash
         CAA Record @	0 issuewild "letsencrypt.org; validationmethods=dns-01; accounturi=https://acme-v02.api.letsencrypt.org/acme/acct/1424899626"  Automatic

         CAA Record @	0 issue "letsencrypt.org; validationmethods=dns-01; accounturi=https://acme-v02.api.letsencrypt.org/acme/acct/1424899626"
         Automatic
         ```

        Same as an entry that needs to be added to complete a time challenge as previously we did.
       * Check whether the entry is added successfully or not

         ```bash
         dig _acme-challenge.arpansahu.me
         ```

       * Get a wildcard certificate

         ```bash
         sudo certbot certonly \
         --manual \
         --test-cert \ 
         --preferred-challenges dns \ 
         --manual-auth-hook 'acme-dns-client' \ 
         -d ‘*.arpansahu.me’ -d arpansahu.me
         ```

        Note: Here we have to mention both the base and wildcard domain names with -d since let's encrypt don't provide base domain ssl by default in wildcard domain ssl
       
       * Verifying the certificate

         ```bash
         sudo openssl x509 -text -noout \
         -in /etc/letsencrypt/live/arpansahu.me/fullchain.pem
         ```

       * Renew certificate (test)

         ```bash
         sudo certbot renew \
         --manual \ 
         --test-cert \ 
         --dry-run \ 
         --preferred-challenges dns \
         --manual-auth-hook 'acme-dns-client'       
         ```
         
       * Renew certificate (actually)

         ```bash
         sudo certbot renew \
         --manual \
         --preferred-challenges dns \
         --manual-auth-hook 'acme-dns-client'       
         ```

       * Check the entry is added successfully or not

         ```bash
         dig _acme-challenge.arpansahu.me
         ```

    6. Setup Auto-Renew for Letsencrypt WILDCARD Certificate
       * Setup cronjob

         ```bash
         sudo crontab -e
         ```

       * Add the following lines to the file

         ```bash
         0 */12 * * * certbot renew --manual --test-cert --preferred-challenges dns --manual-auth-hook 'acme-dns-client'
         ```

After all these steps your Nginx configuration file located at /etc/nginx/sites-available/arpansahu will be looking similar to this

```bash
server_tokens               off;
access_log                  /var/log/nginx/supersecure.access.log;
error_log                   /var/log/nginx/supersecure.error.log;

server {
    listen         80;
    server_name    django-starter.arpansahu.me;
    # force https-redirects
    if ($scheme = http) {
        return 301 https://$server_name$request_uri;
        }

    location / {
         proxy_pass              http://{ip_of_home_server}:8016;
         proxy_set_header        Host $host;
         proxy_set_header        X-Forwarded-Proto $scheme;

	 # WebSocket support
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

### Step 6: CI/CD using Jenkins

### Installing Jenkins

Reference: https://www.jenkins.io/doc/book/installing/linux/

Jenkins requires Java to run, yet certain distributions don’t include this by default and some Java versions are incompatible with Jenkins.

There are multiple Java implementations which you can use. OpenJDK is the most popular one at the moment, we will use it in this guide.

Update the Debian apt repositories, install OpenJDK 11, and check the installation with the commands:

```bash
sudo apt update

sudo apt install openjdk-11-jre

java -version
openjdk version "11.0.12" 2021-07-20
OpenJDK Runtime Environment (build 11.0.12+7-post-Debian-2)
OpenJDK 64-Bit Server VM (build 11.0.12+7-post-Debian-2, mixed mode, sharing)
```

Long Term Support release

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
```

Start Jenkins

```bash
sudo systemctl enable jenkins
```

You can start the Jenkins service with the command:

```bash
sudo systemctl start jenkins
```

You can check the status of the Jenkins service using the command:

```bash
sudo systemctl status jenkins
```

Now for serving the Jenkins UI from Nginx add the following lines to the Nginx file located at 
/etc/nginx/sites-available/service by running the following command

Edit Nginx Configuration

```bash
sudo vi /etc/nginx/sites-available/services
```

if /etc/nginx/sites-available/services does not exists

    1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

    ```bash
        touch /etc/nginx/sites-available/services
        vi /etc/nginx/sites-available/services
    ```


* Add these lines to it.

    ```bash
    server {
        listen         80;
        server_name    jenkins.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }
    
        location / {
             proxy_pass              http://{ip_of_home_server}:8080;
             proxy_set_header        Host $host;
             proxy_set_header    X-Forwarded-Proto $scheme;
        }
    
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

You can add all the server blocks to the same nginx configuration file
just make sure you place the server block for the base domain at the last

* To copy .env from the local server directory while building image

add Jenkins ALL=(ALL) NOPASSWD: ALL
inside /etc/sudoers file

and then put 

```bash
stage('Dependencies') {
            steps {
                script {
                    sh "sudo cp /root/env/project_name/.env /var/lib/jenkins/workspace/pipeline_project_name"
                }
            }
        }
```

* Also we Need to modify the Nginx Configuration File

1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

  ```bash
    touch /etc/nginx/sites-available/django_starter
    vi /etc/nginx/sites-available/django_starter
  ```

2.	Add the server block configuration: Copy and paste your server block configuration into this new file.

  We can have two configurations, one for docker and one for kubernetes deployment, out jenkins deployment file will handle it accordingly.

  1. Nginx for Docker Deployment 

    ```bash
        server {
            listen 80;
            server_name django-starter.arpansahu.me;

            # Force HTTPS redirects
            if ($scheme = http) {
                return 301 https://$server_name$request_uri;
            }

            location / {
                proxy_pass http://0.0.0.0:8016;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-Proto $scheme;

                # WebSocket support
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
            }

            listen 443 ssl; # managed by Certbot
            ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
            ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
            include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
            ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
        }
    ```

  2. Nginx for Kubernetes Deployment 

    ```bash
        server {
            listen 80;
            server_name django-starter.arpansahu.me;

            # Force HTTPS redirects
            if ($scheme = http) {
                return 301 https://$server_name$request_uri;
            }

            location / {
                proxy_pass http://<CLUSTER_IP_ADDRESS>:32016;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-Proto $scheme;

                # WebSocket support
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
            }

            listen 443 ssl; # managed by Certbot
            ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
            ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
            include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
            ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
        }
    ```

3.	Enable the new configuration: Create a symbolic link from this file to the sites-enabled directory.

    ```bash
      sudo ln -s /etc/nginx/sites-available/django_starter /etc/nginx/sites-enabled/
    ```

4.	Test the Nginx configuration: Ensure that the new configuration doesn’t have any syntax errors.

  ```bash
    sudo nginx -t
  ```
  
5.	Reload Nginx: Apply the new configuration by reloading Nginx.

  ```bash
    sudo systemctl reload nginx
  ```

in Jenkinsfile-build to copy .env file into build directory

* Now Create a file named Jenkinsfile-build at the root of Git Repo and add following lines to file

```bash
pipeline {
    agent any
    parameters {
        booleanParam(name: 'skip_checks', defaultValue: false, description: 'Skip the Check for Changes stage')
    }
    environment {
        REGISTRY = "harbor.arpansahu.me"
        REPOSITORY = "library/django_starter"
        IMAGE_TAG = "${env.BUILD_ID}"
        COMMIT_FILE = "${env.WORKSPACE}/last_commit.txt"
        ENV_PROJECT_NAME = "django_starter"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Check for Changes') {
            steps {
                script {
                    if (params.skip_checks) {
                        echo "Skipping Checks is True. Proceeding with build."
                        BUILD_STATUS = 'BUILT'
                        currentBuild.description = "${currentBuild.fullDisplayName} Skipping Checks is True. Proceeding with build."
                    } else {
                        // Get the current commit hash
                        def currentCommit = sh(script: "git rev-parse HEAD", returnStdout: true).trim()
                        echo "Current commit: ${currentCommit}"

                        // Check if the last commit file exists
                        if (fileExists(COMMIT_FILE)) {
                            def lastCommit = readFile(COMMIT_FILE).trim()
                            echo "Last commit: ${lastCommit}"

                            // Compare the current commit with the last commit
                            if (currentCommit == lastCommit) {
                                echo "No changes detected. Skipping build."
                                currentBuild.description = "${currentBuild.fullDisplayName} build skipped due to no changes detected"
                                return
                            } else {
                                // Check for changes in relevant files
                                def changes = sh(script: "git diff --name-only ${lastCommit} ${currentCommit}", returnStdout: true).trim().split("\n")
                                def relevantChanges = changes.findAll { 
                                    !(it in ['README.md', 'SECURITY.md', 'CHANGELOG.md', '.github/dependabot.yml'])
                                }
                                
                                if (relevantChanges.isEmpty()) {
                                    echo "No relevant changes detected. Skipping build."
                                    currentBuild.description = "${currentBuild.fullDisplayName} build skipped due to no relevant changes"
                                    return
                                } else {
                                    echo "Relevant changes detected. Proceeding with build."
                                    BUILD_STATUS = 'BUILT'
                                }
                            }
                        } else {
                            echo "No last commit file found. Proceeding with initial build."
                            BUILD_STATUS = 'BUILT'
                        }

                        // Save the current commit hash to the file
                        writeFile(file: COMMIT_FILE, text: currentCommit)
                    }
                }
            }
        }
        stage('Dependencies') {
            when {
                expression { return BUILD_STATUS != 'NOT_BUILT' }
            }
            steps {
                script {
                    // Copy .env file to the workspace
                    sh "sudo cp /root/projectenvs/${ENV_PROJECT_NAME}/.env ${env.WORKSPACE}/"
                }
            }
        }
        stage('Build Image') {
            when {
                expression { return BUILD_STATUS != 'NOT_BUILT' }
            }
            steps {
                script {
                    // Ensure Docker is running and can be accessed
                    sh 'docker --version'

                    // Log the image details
                    echo "Building Docker image: ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG}"

                    // Build the Docker image
                    sh """
                    docker build -t ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG} .
                    docker tag ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG} ${REGISTRY}/${REPOSITORY}:latest
                    """
                }
            }
        }
        stage('Push Image') {
            when {
                expression { return BUILD_STATUS != 'NOT_BUILT' }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'harbor-credentials', passwordVariable: 'DOCKER_REGISTRY_PASSWORD', usernameVariable: 'DOCKER_REGISTRY_USERNAME')]) {
                    script {
                        // Log in to Docker registry using environment variables without direct interpolation
                        sh '''
                        echo $DOCKER_REGISTRY_PASSWORD | docker login ${REGISTRY} -u $DOCKER_REGISTRY_USERNAME --password-stdin
                        '''

                        // Push the Docker image to the registry
                        sh '''
                        docker push ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG}
                        docker push ${REGISTRY}/${REPOSITORY}:latest
                        '''
                    }
                }
            }
        }
    }
    post {
        success {
            script {
                if (!currentBuild.description) {
                    currentBuild.description = "Image: ${REGISTRY}/${REPOSITORY}:${IMAGE_TAG} built and pushed successfully"
                }
                
                // Send success notification email
                sh """curl -s \
                -X POST \
                --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
                https://api.mailjet.com/v3.1/send \
                -H "Content-Type:application/json" \
                -d '{
                    "Messages":[
                            {
                                    "From": {
                                            "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                            "Name": "ArpanSahuOne Jenkins Notification"
                                    },
                                    "To": [
                                            {
                                                    "Email": "$MY_EMAIL_ADDRESS",
                                                    "Name": "Development Team"
                                            }
                                    ],
                                    "Subject": "${currentBuild.description}",
                                    "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} : ${currentBuild.description}",
                                    "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} : ${currentBuild.description} </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                            }
                    ]
                }'"""

                // Trigger django_starter job only if the build is stable
                build job: 'django_starter', parameters: [booleanParam(name: 'DEPLOY', value: true)], wait: false
            }
        }
        failure {
            script {
                // Send failure notification email
                sh """curl -s \
                -X POST \
                --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
                https://api.mailjet.com/v3.1/send \
                -H "Content-Type:application/json" \
                -d '{
                    "Messages":[
                            {
                                    "From": {
                                            "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                            "Name": "ArpanSahuOne Jenkins Notification"
                                    },
                                    "To": [
                                            {
                                                    "Email": "$MY_EMAIL_ADDRESS",
                                                    "Name": "Development Team"
                                            }
                                    ],
                                    "Subject": "${currentBuild.fullDisplayName} build failed",
                                    "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} build failed ${currentBuild.description} ",
                                    "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} build failed </h3> <br> <p> ${currentBuild.description}  </p>"
                            }
                    ]
                }'"""
            }
        }
    }
}
```

* Now Create a file named Jenkinsfile-deploy at the root of Git Repo and add following lines to file

```bash
pipeline {
    agent { label 'local' }
    parameters {
        booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Skip the Check for Changes stage')
        choice(name: 'DEPLOY_TYPE', choices: ['kubernetes', 'docker'], description: 'Select deployment type')
    }
    environment {
        REGISTRY = "harbor.arpansahu.me"
        REPOSITORY = "library/django_starter"
        IMAGE_TAG = "latest"  // or use a specific tag if needed
        KUBECONFIG = "${env.WORKSPACE}/kubeconfig"  // Set the KUBECONFIG environment variable
        NGINX_CONF = "/etc/nginx/sites-available/django-starter"
        ENV_PROJECT_NAME = "django_starter"
        DOCKER_PORT = "8016"
        PROJECT_NAME_WITH_DASH = "django-starter"
        SERVER_NAME= "django-starter.arpansahu.me"
        BUILD_PROJECT_NAME = "django_starter_build"
        JENKINS_DOMAIN = "jenkins.arpansahu.me"
        SENTRY_ORG="arpansahu"
        SENTRY_PROJECT="django_starter"
    }
    stages {
        stage('Initialize') {
            steps {
                script {
                    echo "Current workspace path is: ${env.WORKSPACE}"
                }
            }
        }
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Setup Kubernetes Config') {
            when {
                expression { return params.DEPLOY_TYPE == 'kubernetes' }
            }
            steps {
                script {
                    // Copy the kubeconfig file to the workspace
                    sh "sudo cp /root/.kube/config ${env.WORKSPACE}/kubeconfig"
                    // Change permissions of the kubeconfig file
                    sh "sudo chmod 644 ${env.WORKSPACE}/kubeconfig"
                }
            }
        }
        stage('Check & Create Nginx Configuration') {
            steps {
                script {
                    // Check if the Nginx configuration file exists
                    def configExists = sh(script: "test -f ${NGINX_CONF} && echo 'exists' || echo 'not exists'", returnStdout: true).trim()

                    if (configExists == 'not exists') {
                        echo "Nginx configuration file does not exist. Creating it now..."

                        // Create or overwrite the NGINX_CONF file with the content of nginx.conf using sudo tee
                        sh "sudo cat nginx.conf | sudo tee ${NGINX_CONF} > /dev/null"

                        // Replace placeholders in the configuration file
                        sh "sudo sed -i 's|SERVER_NAME|${SERVER_NAME}|g' ${NGINX_CONF}"
                        sh "sudo sed -i 's|DOCKER_PORT|${DOCKER_PORT}|g' ${NGINX_CONF}"

                        echo "Nginx configuration file created."

                        // Ensure Nginx is aware of the new configuration
                        sh "sudo ln -sf ${NGINX_CONF} /etc/nginx/sites-enabled/"
                    } else {
                        echo "Nginx configuration file already exists."
                    }                    
                }
            }
        }
        stage('Retrieve Image Tag from Build Job') {
            when {
                expression { params.DEPLOY && params.DEPLOY_TYPE == 'kubernetes' }
            }
            steps {
                script {
                    echo "Retrieve image tag from ${BUILD_PROJECT_NAME}"

                    // Construct the API URL for the latest build
                    def api_url = "https://${JENKINS_DOMAIN}/job/${BUILD_PROJECT_NAME}/lastSuccessfulBuild/api/json"

                    // Log the API URL for debugging purposes
                    echo "Hitting API URL: ${api_url}"
                    
                    withCredentials([usernamePassword(credentialsId: 'fc364086-fb8b-4528-bc7f-1ef3f42b71c7', usernameVariable: 'JENKINS_USER', passwordVariable: 'JENKINS_PASS')]) {
                        // Execute the curl command to retrieve the JSON response
                        echo "usernameVariable: ${JENKINS_USER}, passwordVariable: ${JENKINS_PASS}"
                        def buildInfoJson = sh(script: "curl -u ${JENKINS_USER}:${JENKINS_PASS} ${api_url}", returnStdout: true).trim()

                        // Log the raw JSON response for debugging
                        echo "Raw JSON response: ${buildInfoJson}"

                        def imageTag = sh(script: """
                            echo '${buildInfoJson}' | grep -oP '"number":\\s*\\K\\d+' | head -n 1
                        """, returnStdout: true).trim()

                        echo "Retrieved image tag (build number): ${imageTag}"

                        // Replace the placeholder in the deployment YAML
                        sh "sed -i 's|:latest|:${imageTag}|g' ${WORKSPACE}/deployment.yaml"

                        // Ensure the correct image tag is used in the docker-compose.yml
                        sh '''
                        sed -i "s|image: .*|image: ${REGISTRY}/${REPOSITORY}:${imageTag}|" docker-compose.yml
                        '''
                    }
                }
            }
        }
        stage('Deploy') {
            when {
                expression { params.DEPLOY }
            }
            steps {
                script {
                    if (params.DEPLOY_TYPE == 'docker') {

                        // Copy the .env file to the workspace
                        sh "sudo cp /root/projectenvs/${ENV_PROJECT_NAME}/.env ${env.WORKSPACE}/"

                        // Deploy using Docker Compose
                        sh 'docker-compose down'
                        sh 'docker-compose pull'
                        sh 'docker-compose up -d'

                        // Wait for a few seconds to let the app start
                        sleep 10

                        // Verify the container is running
                        def containerRunning = sh(script: "docker ps -q -f name=${ENV_PROJECT_NAME}", returnStdout: true).trim()
                        if (!containerRunning) {
                            error "Container ${ENV_PROJECT_NAME} is not running"
                        } else {
                            echo "Container ${ENV_PROJECT_NAME} is running"
                            // Execute curl and scale down Kubernetes deployment if curl is successful
                            sh """
                                # Fetch HTTP status code
                                HTTP_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" -L http://0.0.0.0:${DOCKER_PORT})
                                echo "HTTP Status: \$HTTP_STATUS"
                                
                                # Update Nginx configuration if status code is 200 (OK)
                                if [ "\$HTTP_STATUS" -eq 200 ]; then
                                    sudo sed -i 's|proxy_pass .*;|proxy_pass http://0.0.0.0:${DOCKER_PORT};|' ${NGINX_CONF}
                                    sudo nginx -s reload
                                    echo 'Nginx configuration updated and reloaded successfully.'
                                else
                                    echo 'Service not available. Nginx configuration not updated.'
                                fi

                                # Scale down Kubernetes deployment if it exists and is running
                                replicas=\$(kubectl get deployment ${PROJECT_NAME_WITH_DASH}-app -o=jsonpath='{.spec.replicas}') || true
                                if [ "\$replicas" != "" ] && [ \$replicas -gt 0 ]; then
                                    kubectl scale deployment ${PROJECT_NAME_WITH_DASH}-app --replicas=0
                                    echo 'Kubernetes deployment scaled down successfully.'
                                else
                                    echo 'No running Kubernetes deployment to scale down.'
                                fi
                            """
                        }
                    } else if (params.DEPLOY_TYPE == 'kubernetes') {
                        // Copy the .env file to the workspace
                        sh "sudo cp /root/projectenvs/${ENV_PROJECT_NAME}/.env ${env.WORKSPACE}/"

                        // Check if the file is copied successfully
                        if (fileExists("${env.WORKSPACE}/.env")) {
                            echo ".env file copied successfully."
                            
                            // Verify Kubernetes configuration
                            sh 'kubectl cluster-info'
                            
                            // Print current directory
                            sh 'pwd'
                            
                            // Delete existing secret if it exists
                            sh """
                            kubectl delete secret ${PROJECT_NAME_WITH_DASH}-secret || true
                            """

                            // Delete the existing service and deployment
                            sh """
                            kubectl delete service ${PROJECT_NAME_WITH_DASH}-service || true
                            kubectl scale deployment ${PROJECT_NAME_WITH_DASH}-app --replicas=0 || true
                            kubectl delete deployment ${PROJECT_NAME_WITH_DASH}-app || true
                            """

                            // Deploy to Kubernetes
                            sh """
                            kubectl create secret generic ${PROJECT_NAME_WITH_DASH}-secret --from-env-file=${WORKSPACE}/.env
                            kubectl apply -f ${WORKSPACE}/service.yaml
                            kubectl apply -f ${WORKSPACE}/deployment.yaml
                            """
                            
                            // Wait for a few seconds to let the app start
                            sleep 60

                            // Check deployment status
                            sh """
                            kubectl rollout status deployment/${PROJECT_NAME_WITH_DASH}-app
                            """
                            
                            // Verify service and get NodePort
                            def nodePort = sh(script: "kubectl get service ${PROJECT_NAME_WITH_DASH}-service -o=jsonpath='{.spec.ports[0].nodePort}'", returnStdout: true).trim()
                            echo "Service NodePort: ${nodePort}"

                            // Get cluster IP address
                            def clusterIP = sh(script: "kubectl get nodes -o=jsonpath='{.items[0].status.addresses[0].address}'", returnStdout: true).trim()
                            echo "Cluster IP: ${clusterIP}"

                            // Verify if the service is accessible and delete the Docker container if accessible and update nginx configuration
                            sh """
                                HTTP_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" -L http://${clusterIP}:${nodePort})
                                echo "HTTP Status: \$HTTP_STATUS"
                                
                                if [ "\$HTTP_STATUS" -eq 200 ]; then
                                    echo "Service is reachable at http://${clusterIP}:${nodePort}"

                                    echo "Updating Nginx configuration at ${NGINX_CONF}..."
                                    sudo sed -i 's|proxy_pass .*;|proxy_pass http://${clusterIP}:${nodePort};|' ${NGINX_CONF}
                                    
                                    if [ \$? -ne 0 ]; then
                                        echo "Failed to update Nginx configuration"
                                        exit 1
                                    fi
                                    
                                    echo "Reloading Nginx..."
                                    sudo nginx -s reload
                                    
                                    if [ \$? -ne 0 ]; then
                                        echo "Failed to reload Nginx"
                                        exit 1
                                    fi
                                    
                                    echo "Nginx reloaded successfully"
                                    
                                    DOCKER_CONTAINER=\$(docker ps -q -f name=${ENV_PROJECT_NAME})
                                    
                                    if [ "\$DOCKER_CONTAINER" ]; then
                                        echo "Docker container ${ENV_PROJECT_NAME} is running. Removing it..."
                                        docker rm -f ${ENV_PROJECT_NAME}
                                        
                                        if [ \$? -ne 0 ]; then
                                            echo "Failed to remove Docker container ${ENV_PROJECT_NAME}"
                                            exit 1
                                        fi
                                        
                                    else
                                        echo "Docker container ${ENV_PROJECT_NAME} is not running. Skipping removal"
                                    fi

                                else
                                    echo "Service is not reachable at http://${clusterIP}:${nodePort}. HTTP Status: \$HTTP_STATUS"
                                    exit 1
                                fi
                            """
                        } else {
                            error ".env file not found in the workspace."
                        }
                    }
                    currentBuild.description = 'DEPLOYMENT_EXECUTED'
                }
            }
        }
        stage('Sentry release') {
            when {
                expression { params.DEPLOY }
            }
            steps {
                script {
                    echo "Sentry Release ..."

                    sh """
                        # Get the current git commit hash
                        VERSION=\$(git rev-parse HEAD)

                        sentry-cli releases -o ${SENTRY_ORG} -p ${SENTRY_PROJECT} new \$VERSION

                        # Associate commits with the release
                        sentry-cli releases -o ${SENTRY_ORG} -p ${SENTRY_PROJECT} set-commits --auto \$VERSION

                        # Deploy the release (optional step for marking the release as deployed)
                        sentry-cli releases -o ${SENTRY_ORG} -p ${SENTRY_PROJECT} deploys \$VERSION new -e production
                    """
                }
            }
        }
    }
    post {
        success {
            script {
                if (currentBuild.description == 'DEPLOYMENT_EXECUTED') {
                    sh """curl -s \
                    -X POST \
                    --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
                    https://api.mailjet.com/v3.1/send \
                    -H "Content-Type:application/json" \
                    -d '{
                        "Messages":[
                                {
                                        "From": {
                                                "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                                "Name": "ArpanSahuOne Jenkins Notification"
                                        },
                                        "To": [
                                                {
                                                        "Email": "$MY_EMAIL_ADDRESS",
                                                        "Name": "Development Team"
                                                }
                                        ],
                                        "Subject": "Jenkins Build Pipeline your project ${currentBuild.fullDisplayName} Ran Successfully",
                                        "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed",
                                        "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                                }
                        ]
                    }'"""
                }
                // Trigger the common_readme job on success when last commit is not Automatic Update from common_readme
                def commitMessage = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
                if (!commitMessage.contains("Automatic Update")) {
                    def expandedProjectUrl = "https://github.com/arpansahu/${ENV_PROJECT_NAME}"
                    build job: 'common_readme', parameters: [
                        string(name: 'project_git_url', value: expandedProjectUrl),
                        string(name: 'environment', value: 'prod')
                    ], wait: false
                } else {
                    echo "Skipping common_readme job trigger due to commit message: ${commitMessage}"
                }            
            }
        }
        failure {
            sh """curl -s \
            -X POST \
            --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
            https://api.mailjet.com/v3.1/send \
            -H "Content-Type:application/json" \
            -d '{
                "Messages":[
                        {
                                "From": {
                                        "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                        "Name": "ArpanSahuOne Jenkins Notification"
                                },
                                "To": [
                                        {
                                                "Email": "$MY_EMAIL_ADDRESS",
                                                "Name": "Developer Team"
                                        }
                                ],
                            "Subject": "Jenkins Build Pipeline your project ${currentBuild.fullDisplayName} Ran Failed",
                            "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} deployment failed",
                            "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is not deployed, Build Failed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                        }
                ]
            }'"""
        }
    }
}
```

Note: agent {label 'local'} is used to specify which node will execute the jenkins job deployment. So local linux server is labelled with 'local' are the project with this label will be executed in local machine node.

* Configure a Jenkins project from jenkins ui located at https://jenkins.arpansahu.me

Make sure to use Pipeline project and name it whatever you want I have named it as per django_starter

![Jenkins Pipeline Configuration](/Jenkins-deploy.png)

* Configure another Jenkins project from jenkins ui located at https://jenkins.arpansahu.me

Make sure to use Pipeline project and name it whatever you want I have named it as django_starter_build

![Jenkins Build Pipeline Configuration](/Jenkins-build.png)

This pipeline is triggered on another branch named as build. Whenever a new commit is pushed, it checks 
if there are changes in the files other then few .md files and dependabot.yml file. If, changes are there it pushed the image.
If image is pushed successfully, email is sent to notify and then another Jenkins Pipeline django_starter_build is called.


In this above picture you can see credentials right? you can add your github credentials and harbor credentials use harbor-credentials as id for harbor credentials.
from Manage Jenkins on home Page --> Manage Credentials

and add your GitHub credentials from there

* Add a .env file to you project using following command (This step is no more required stage('Dependencies'))

    ```bash
    sudo vi  /var/lib/jenkins/workspace/django_starter/.env
    ```

    Your workspace name may be different.

    Add all the env variables as required and mentioned in the Readme File.

* Add Global Jenkins Variables from Dashboard --> Manage --> Jenkins
  Configure System
 
  * MAIL_JET_API_KEY
  * MAIL_JET_API_SECRET
  * MAIL_JET_EMAIL_ADDRESS
  * MY_EMAIL_ADDRESS

Now you are good to go.

# Services on AWS EC2/ Home Server Ubuntu 22.0 LTS s

## Postgresql Server

IT would be a nightmare to have your own vps to save cost and not hosting your own postgresql server.

postgresql_server can be access accessed

### Installing PostgreSql

1. Update the package list to make sure you have the latest information

    ```bash
    sudo apt update
    ```

2. Install the PostgreSQL package

    ```bash
    sudo apt install postgresql postgresql-contrib
    ```

3. PostgreSQL should now be installed on your server. By default, PostgreSQL creates a user named `postgres` with administrative privileges. You can switch to this user to perform administrative tasks:

    ```bash
    sudo -i -u postgres
    ```

4. Access the PostgreSQL interactive terminal by running:

    ```bash
    psql
    ```

5. Set a password for the `postgres` user:

    ```sql
    ALTER USER postgres WITH PASSWORD 'your_password';
    ```

   Replace `'your_password'` with the desired password.

6. Exit the PostgreSQL shell:

    ```sql
    \q
    ```

7. Exit the `postgres` user session:

    ```bash
    exit
    ```

Now, PostgreSQL is installed on your Ubuntu server. You can access the PostgreSQL database by logging in with the `postgres` user and the password you set.

Remember to configure your PostgreSQL server according to your security needs, such as modifying the `pg_hba.conf` file to control access, setting up SSL for secure connections, and configuring other PostgreSQL settings as required for your environment.


## Configuring Postgresql

1. open postgresql.conf file

    ```bash
    sudo vi /etc/postgresql/14/main/postgresql.conf
    ```
     
    14 is the version which i have installed your version can be different

2. Find the listen_addresses line and set it to:

    ```bash
    listen_addresses = 'localhost'
    ```

    Now the thing is if u don't want to serve it using nginx u can also set it to * all so that database can be connected from any where

3. 	Edit pg_hba.conf to allow connections:

    ```bash
    sudo nano /etc/postgresql/14/main/pg_hba.conf
    ```

    14 is the version which i have installed your version can be different

4. 	Add the following line in the end:

    ```bash
    host    all             all             127.0.0.1/32            md5
    ```

    if u want to use without nginx

    ```bash
    host    all             all             0.0.0.0/0            md5
    ```

    I have added both 

5. Restart PostgreSQL to apply changes:

    ```bash
    sudo systemctl restart postgresql
    ```

## Configuring Nginx as Reverse proxy

Note: In previous steps we have already seen how to setup the reverse proxy with Nginx for Django projects and installation process and everything

1.	Install the nginx-extras package to support the stream module:

    ```bash
    sudo apt install nginx-extras
    ````

2.	Add a stream configuration file for the PostgreSQL stream:

    ```bash
    sudo vi /etc/nginx/nginx.conf
    ```

    1.	Add the following configuration:

    ```bash
    stream {
        upstream postgresql_upstream {
            server 127.0.0.1:5432;  # PostgreSQL server
        }

        server {
            listen 9550 ssl;  # Use SSL on port 443
            proxy_pass postgresql_upstream;

            ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem;  # SSL certificate
            ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem;  # SSL certificate key
            ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;  # SSL DH parameters
            include /etc/letsencrypt/options-ssl-nginx.conf;  # SSL options

            proxy_timeout 600s;
            proxy_connect_timeout 600s;
        }
    }
    ```

    Since i have generated ssl certs already in nginx setup i am using those certificates here itself

    2. 	Test the Nginx Configuration:

    ```bash
    sudo nginx -t
    ```

    If error comes nginx: [emerg] "stream" directive is not allowed here in /etc/nginx/conf.d/postgresql.conf:1
    nginx: configuration file /etc/nginx/nginx.conf test failed    

    Follow these steps: 

        0.	Remove the custom configuration file:

            ```bash
            sudo rm /etc/nginx/conf.d/postgresql.conf
            ```

        1.	Open the main Nginx configuration file: 

            ```bash
            sudo nano /etc/nginx/nginx.conf
            ```

        2.	Add the Stream Block at the Appropriate Place
        Add the following stream block at the end of the nginx.conf file, or within the appropriate context:

            ```bash
            user www-data;
            worker_processes auto;
            pid /run/nginx.pid;
            include /etc/nginx/modules-enabled/*.conf;

            events {
                worker_connections 768;
            }

            http {
                sendfile on;
                tcp_nopush on;
                tcp_nodelay on;
                keepalive_timeout 65;
                types_hash_max_size 2048;

                include /etc/nginx/mime.types;
                default_type application/octet-stream;

                access_log /var/log/nginx/access.log;
                error_log /var/log/nginx/error.log;

                gzip on;
                gzip_disable "msie6";

                include /etc/nginx/conf.d/*.conf;
                include /etc/nginx/sites-enabled/*;
            }

            stream {
                upstream postgresql_upstream {
                    server 127.0.0.1:5432;  # PostgreSQL server
                }

                server {
                    listen 9550 ssl;  # Use SSL on port different 443
                    proxy_pass postgresql_upstream;

                    ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem;  # SSL certificate
                    ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem;  # SSL certificate key
                    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;  # SSL DH parameters
                    include /etc/letsencrypt/options-ssl-nginx.conf;  # SSL options

                    proxy_timeout 600s;
                    proxy_connect_timeout 600s;
                }
            }
            ```
        
        3.	Test the Nginx Configuration
        
            ```bash
            sudo nginx -t
            ```

    3. Reload Nginx to apply the new configuration:

    ```bash
    sudo systemctl reload nginx
    ```

3. Testing connecting with postgres without ip and using domain

    ```bash
    psql "postgres://username:password@domain/database_name?sslmode=require"
    ```

    
```bash
psql "postgres://user:user_pass@arpansahu.me/database_name?sslmode=require"
```

### Installing PgAdmin

1. **Create a Virtual Environment:**

   It's good practice to use virtual environments to isolate your project's dependencies. This helps avoid conflicts with system packages. You can create a virtual environment like this:

   ```bash
   python3 -m venv pgadmin_venv
   source pgadmin_venv/bin/activate
   ```

2. **Install pgAdmin 4:**

   Once you are in the virtual environment, install pgAdmin 4:

   ```bash
   pip install pgadmin4
   ```

   If you encounter any dependency conflicts, the virtual environment will help isolate the packages.

3. **Run pgAdmin 4:**

   After installing, try running pgAdmin 4:

   ```bash
   pgadmin4
   ```
    
By using a virtual environment, you avoid potential conflicts with system packages, and you can manage dependencies for pgAdmin 4 more effectively.

Remember to activate your virtual environment whenever you want to run pgAdmin 4:

```bash
source pgadmin_venv/bin/activate
pgadmin4
```

### Manage PgAdmin using Pm2

1. Create a Startup Script for pgAdmin 4

    ```bash
        touch /root/run_pgadmin.sh 
    ```

2. Edit this script and add following 

    ```bash
        vi /root/run_pgadmin.sh 
    ```
    ```bash
        source pgadmin_venv/bin/activate
        pgadmin4
    ```

3. Making Script Executable

    ```bash
        chmod +x /root/run_pgadmin.sh
    ```

4. Installing pm2

    ```bash
        npm install pm2 -g
    ```

5. Start pgAdmin 4 with PM2

    ```bash
        pm2 start /root/run_pgadmin.sh --name pgadmin4
    ```

6. Save PM2 configuration

    ```bash
        pm2 save
    ```

7. Set PM2 to Start on Boot

    ```bash
        pm2 startup
    ```

And deactivate it when you're done:

```bash
deactivate
```



4. Edit Host from 127.0.0.1 tto 0.0.0.0

```bash
vi /root/pgadmin_venv/lib/python3.10/site-packages/pgadmin4/config.py
```


### Configuring Nginx as Reverse proxy

1. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```


2. Add this server configuration

    ```bash
    server {
        listen         80;
        server_name    pgadmin.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }

        location / {
            proxy_pass              http://0.0.0.0:9997;
            proxy_set_header        Host $host;
            proxy_set_header    X-Forwarded-Proto $scheme;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

3. Test the Nginx Configuration

    ```bash
    sudo nginx -t
    ```

4. Reload Nginx to apply the new configuration

    ```bash
    sudo systemctl reload nginx
    ```

### Conclusion

This approach should help you manage the dependencies and resolve the version conflicts more effectively while ensuring pgAdmin runs in the background and is accessible via Nginx as a reverse proxy.

My PGAdmin4 can be accessed here : https://pgadmin.arpansahu.me/

## Portainer
   
Portainer is a web UI to manage your docker, and kubernetes. Portainer consists of two elements, the Portainer Server, and the Portainer Agent. Both elements run as lightweight Docker containers on a Docker engine.

### Installing Portainer

1. **Create a Docker Volume for Portainer Data (optional but recommended):**
   This step is optional but recommended as it allows you to persist Portainer's data across container restarts.

    ```bash
    docker volume create portainer_data
    ```

2. **Run Portainer Container:**
   Run the Portainer container using the following command. Replace `/var/run/docker.sock` with the path to your Docker socket if it's in a different location.

    ```bash
    docker run -d -p 0.0.0.0:9998:9000 -p 9444:8000 -p 9443:9443 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
    to use it in nginx server configuration
    ```

   This command pulls the Portainer Community Edition image from Docker Hub, creates a persistent volume for Portainer data, and starts the Portainer container. The `-p 9000:9000` option maps Portainer's web interface to port 9000 on your host.

3. **Access Portainer UI:**
   Open your web browser and go to `http://localhost:9000` (or replace `localhost` with your server's IP address if you are using a remote server). You will be prompted to set up an admin user and password.

4. **Connect Portainer to the Docker Daemon:**
   On the Portainer setup page, choose the "Docker" environment, and connect Portainer to the Docker daemon. You can usually use the default settings (`unix:///var/run/docker.sock` for the Docker API endpoint).

5. **Complete Setup:**
   Follow the on-screen instructions to complete the setup process. You may choose to deploy a local agent for better performance, but it's not required for basic functionality.

Once the setup is complete, you should have access to the Portainer dashboard, where you can manage and monitor your Docker containers, images, volumes, and networks through a user-friendly web interface.

Keep in mind that the instructions provided here assume a basic setup. For production environments, it's recommended to secure the Portainer instance, such as by using HTTPS and setting up authentication. Refer to the [Portainer documentation](https://documentation.portainer.io/) for more advanced configurations and security considerations.


### Configuring Nginx as Reverse proxy

1. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```


    
2. Add this server configuration

    ```bash
    server {
        listen         80;
        server_name    portainer.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }

        location / {
            proxy_pass              http://0.0.0.0:9998;
            proxy_set_header        Host $host;
            proxy_set_header    X-Forwarded-Proto $scheme;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

3. Test the Nginx Configuration

    ```bash
    sudo nginx -t
    ```

4. Reload Nginx to apply the new configuration

    ```bash
    sudo systemctl reload nginx
    ```

### Running Portainer Agent 

1. Run this command to start the portainer agent docker container

    ```bash
        docker run -d -p 9995:9001 \
        --name portainer_agent \
        --restart=always \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /var/lib/docker/volumes:/var/lib/docker/volumes \
        portainer/agent:2.19.5
    ```

2. Configuring Nginx as Reverse proxy

    1. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```


    2. Add this server configuration

        ```bash
        server {
            listen         80;
            server_name    portainer-agent.arpansahu.me;
            # force https-redirects
            if ($scheme = http) {
                return 301 https://$server_name$request_uri;
                }

            location / {
                proxy_pass              http://0.0.0.0:9995;
                proxy_set_header        Host $host;
                proxy_set_header    X-Forwarded-Proto $scheme;
            }

            listen 443 ssl; # managed by Certbot
            ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
            ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
            include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
            ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
        }
        ```

    3. Test the Nginx Configuration

        ```bash
        sudo nginx -t
        ```

    4. Reload Nginx to apply the new configuration

        ```bash
        sudo systemctl reload nginx
        ```
3. Adding Environment

    1. Go to environment ---> Choose Docker Standalone ----> Start Wizard

    2. Will show you a command same as step 1. Run this command to start the portainer agent docker container, this is default command we have modified ports although

        ```bash
            docker run -d -p 9001:9001 \    
            --name portainer_agent \
            --restart=always \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v /var/lib/docker/volumes:/var/lib/docker/volumes \
            portainer/agent:2.19.5
        ```

    3. Add Name, I have used docker-prod-env
    4. Add Environment address domain:port combination is needed in my case portainer-agent.arpansahu.me: 9995
    5. Click Connect

My Portainer can be accessed here : https://portainer.arpansahu.me/

## Redis Server

Redis is versatile and widely used for its speed and efficiency in various applications. Its ability to serve different roles, such as caching, real-time analytics, and pub/sub messaging, makes it a valuable tool in many technology stacks.

### Installing Redis and Setting Up Authentication


1. Step 1: Install Redis on Ubuntu

   1. **Update your package list:**
      ```sh
      sudo apt update
      ```

   2. **Install Redis:**
      ```sh
      sudo apt install redis-server
      ```

   3. **Start and enable Redis:**
      ```sh
      sudo systemctl start redis
      sudo systemctl enable redis
      ```

2. Step 2: Configure Redis

   1. **Open the Redis configuration file:**
      ```sh
      sudo vi /etc/redis/redis.conf
      ```

   2. **Change the host to 0.0.0.0:**
      Find the line with `bind 127.0.0.1 ::1` and change it to:
      ```
      bind 0.0.0.0
      ```

   3. **Set up authentication:**
      Find the line with `# requirepass foobared` and uncomment it. Replace `foobared` with your desired password:
      ```
      requirepass your_secure_password
      ```

   4. **Save and exit the editor** (`esc + :wq + enter` in vi).

   5. **Restart Redis to apply the changes:**
      ```sh
      sudo systemctl restart redis
      ```

3. Step 3: Verify Configuration

   1. **Connect to Redis using the CLI:**
      ```sh
      redis-cli
      ```

   2. **Authenticate with your password:**
      ```sh
      AUTH your_secure_password
      ```

   3. **Check the connection:**
      ```sh
      PING
      ```
      You should receive a response:
      ```
      PONG
      ```

   4. **Verify the binding to 0.0.0.0:**
      ```sh
      sudo netstat -tulnp | grep redis
      ```
      You should see Redis listening on `0.0.0.0:6379`.

4. Step 4: Connecting to Redis

   1. **Connect to Redis using the CLI from a remote host:**
      ```sh
      redis-cli -h arpansahu.me -p 6379 -a your_secure_password
      ```

## Note: If you want to use SSL connection

1. Open the Redis configuration file:
    ```sh
    sudo vi /etc/redis/redis.conf
    ```

2. Add the following configuration:
    ```
    tls-port 6379
    port 0

    tls-cert-file /path/to/redis.crt
    tls-key-file /path/to/redis.key
    tls-dh-params-file /path/to/dhparam.pem

    tls-auth-clients no
    ```

Mostly Redis is used as cache and we want it to be super fast; hence, we are not putting it behind a reverse proxy like Nginx, similar to PostgreSQL.

Mostly redis is used as cache and we want it to be super fast hence we are not putting it behind reverse proxy e.g. nginx same as postgres

Also one more thing redis by default don't support ssl connections even if u use ssl

redis server can be accessed

```bash
redis-cli -h arpansahu.me -p 6379 -a password_required
```

## Redis Commander

Redis Commander is a web-based management tool for Redis databases. It provides a user-friendly interface to interact with Redis, making it easier to manage and monitor your Redis instances.

### Installing Redis Commander

1. Installation:
    You can install redis-commander globally using npm (Node Package Manager) with the following command:

    ```bash
    npm install -g redis-commander
    ```

2. Run

    ```bash
    redis-commander --redis-host your-redis-server-ip --redis-port your-redis-port --redis-password your-redis-password --port 9996
    ```

### Serving with Nginx, as well password protecting Redis Commander

Redis Commander d'ont have native password protection enabled

1. Create a Basic Authentication File
    Use the htpasswd utility to create a username and password combination. Replace your_username with your desired username.

    ```bash
    sudo htpasswd -c /etc/nginx/.htpasswd your_username
    ```

    You’ll be prompted to enter a password.

2. Edit Nginx Configuration

    ```bash
    sudo vi /etc/nginx/sites-available/services
    ```

    if /etc/nginx/sites-available/services does not exists

        1. Create a new configuration file: Create a new file in the Nginx configuration directory. The location of this directory varies depending on your  operating system and Nginx installation, but it’s usually found at /etc/nginx/sites-available/.

        ```bash
            touch /etc/nginx/sites-available/services
            vi /etc/nginx/sites-available/services
        ```


3. Add this server block to it.

    ```bash
    server {
        listen         80;
        server_name    redis.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }

        location / {
            proxy_pass              http://127.0.0.1:9996;
            proxy_set_header        Host $host;
            proxy_set_header    X-Forwarded-Proto $scheme;
            auth_basic "Restricted Access";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    }
    ```

4. Test the Nginx Configuration

    ```bash
    sudo nginx -t
    ```
    
5. Reload Nginx to apply the new configuration

    ```bash
    sudo systemctl reload nginx
    ```

### Running Redis Commander in background Using pm2

1.	Install pm2 globally (if not already installed):

    ```bash
    npm install -g pm2
    ```


2. Start redis-commander with pm2:

    ```bash
    pm2 start redis-commander --name redis-commander -- --port 9996 --redis-host your-redis-server-ip --redis-port your-redis-port --redis-password your-redis-password
    ```

    This starts redis-commander with pm2 and names the process “redis-commander.”

3. 	Optionally, you can save the current processes to ensure they restart on system reboot:

    ```bash
    pm2 save
    ```

    ```bash
    pm2 startup
    ```

Now, redis-commander is running in the background managed by pm2. You can view its status, logs, and manage it using pm2 commands. For example:

4. View the status:

    ```bash
    pm2 status  
    ```

    Stop the process:

    ```bash
    pm2 stop redis-commander
    ```

    Restart the process:

    ```bash
    pm2 restart redis-commander
    ```

    View logs:

    ```bash
    pm2 logs redis-commander
    ```

My Redis Commander can be accessed here : https://redis.arpansahu.me/


## MiniIo (Self hosted S3 Storage)

MinIO is a high-performance, distributed object storage system designed for large-scale data infrastructures. It is open-source and compatible with the Amazon S3 API, making it a popular choice for organizations looking for scalable, secure, and cost-effective storage solutions. 

### Installing Minio

1. Install MinIO on your server. You can download it from the official website or use a package manager if available.

    ```bash
    wget https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    sudo mv minio /usr/local/bin
    ```

2. Generate SSL Certificates using Certbot
    While setting up nginx we already automated this auto regeneration of certificates every3 months 
    The certificates will be stored in /etc/letsencrypt/live/arpansahu.me/.
    
3. Configure MinIO with SSL Certificates:
    Configure MinIO to use the SSL certificates generated by Certbot. Create a directory to store the certificates and copy them from the Certbot directory.

    ```bash
    sudo mkdir -p /etc/minio/certs
    sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/minio/certs/public.crt
    sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/minio/certs/private.key
    ```

4. Environment File Configuration
    Ensure your environment file, usually located at /etc/default/minio, has the following content: if the file is not present create it

    ```bash
    MINIO_VOLUMES="/mnt/minio"

    # Define where to find the TLS certificates
    MINIO_OPTS="--certs-dir /etc/minio/certs --console-address :9001"

    # Define the admin user (min 3 characters)
    MINIO_ROOT_USER=user_edit_this

    # Define the default admin user password (min 8 characters)
    MINIO_ROOT_PASSWORD=password_edit_this
    ```

5. Setup Directory and Permissions

    ```bash
    sudo mkdir -p /mnt/minio
    sudo chown -R minio-user:minio-user /mnt/minio
    
    sudo mkdir -p /etc/minio/certs
    sudo chown -R minio-user:minio-user /etc/minio/certs
    
    sudo chown minio-user:minio-user /etc/minio/certs/public.crt
    sudo chown minio-user:minio-user /etc/minio/certs/private.key
    ```

6. Reload Systemd and Start MinIO
 Reload the system daemon and start the MinIO service
    
    ```echo
    sudo systemctl daemon-reload
    sudo systemctl start minio
    ```
Note: minio api and ui server both run at 0.0.0.0 host by default


### Nginx Setup as Reverse Proxy

Note: Nginx is already set in the other steps as seen before right now I will discuss server configuration for minio and minioui

1. Nginx Server configuration for minio API server 

     ```bash
    server {
        listen         80;
        server_name    minio.arpansahu.me;

        # Redirect HTTP to HTTPS
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen         443 ssl;
        server_name    minio.arpansahu.me;

        # SSL certificates
        ssl_certificate /etc/minio/certs/public.crt;
        ssl_certificate_key /etc/minio/certs/private.key;

        # Allow special characters in headers
        ignore_invalid_headers off;

        # Allow any size file to be uploaded.
        # Set to a value such as 1000m; to restrict file size to a specific value
        client_max_body_size 0;

        # Disable buffering
        proxy_buffering off;
        proxy_request_buffering off;

        location / {
            proxy_pass          https://0.0.0.0:9000;
            proxy_set_header    Host $host;
            proxy_set_header    X-Real-IP $remote_addr;
            proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header    X-Forwarded-Proto $scheme;

            # Set maximum allowed body size for uploads
            client_max_body_size 0; # Adjust the value as needed

            proxy_connect_timeout 300;
            # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            chunked_transfer_encoding off;
        }
    }
    ```

2. Nginx Server configuration for minio ui server 

    ```bash
    server {
        listen         80;
        server_name    minioui.arpansahu.me;
        # force https-redirects
        if ($scheme = http) {
            return 301 https://$server_name$request_uri;
            }
    
        location / {
             proxy_pass               https://0.0.0.0:9001;
             proxy_set_header        Host $host;
             proxy_set_header    X-Forwarded-Proto $scheme;
    
             # WebSocket support
             proxy_http_version 1.1;
             proxy_set_header Upgrade $http_upgrade;
             proxy_set_header Connection "upgrade";
        }
    
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/arpansahu.me/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/arpansahu.me/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

#### Setup Copy Cron to copy whenever cerbot updates the certificate to /etc/minio/certs

1. Create a Cron Shell file 

    ```bash
    sudo vi /usr/local/bin/update_minio_certs.sh
    ```


2. Add this script to update_minio_certs.sh

    ```bash
    #!/bin/bash
    # Paths to the Let's Encrypt certificates
    CERT_SRC_DIR="/etc/letsencrypt/live/yourdomain.com"
    CERT_DST_DIR="/etc/minio/certs"

    # Path to the public certificate and private key in the source directory
    SRC_PUBLIC_CERT="${CERT_SRC_DIR}/fullchain.pem"
    SRC_PRIVATE_KEY="${CERT_SRC_DIR}/privkey.pem"

    # Path to the public certificate and private key in the destination directory
    DST_PUBLIC_CERT="${CERT_DST_DIR}/public.crt"
    DST_PRIVATE_KEY="${CERT_DST_DIR}/private.key"

    # Function to send email using Mailjet API
    send_email() {
        local subject=$1
        local body=$2

        python3 <<END
    import os
    from mailjet_rest import Client

    api_key = 'your-mailjet-api-key'
    api_secret = 'your-mailjet-api-secret'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
    'Messages': [
        {
        "From": {
            "Email": "your-email@example.com",
            "Name": "MinIO Cert Update"
        },
        "To": [
            {
            "Email": "recipient-email@example.com",
            "Name": "Recipient"
            }
        ],
        "Subject": "$subject",
        "TextPart": "$body"
        }
    ]
    }

    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    END
    }

    # Check if the certificates have changed and copy if they have
    if ! cmp -s "$SRC_PUBLIC_CERT" "$DST_PUBLIC_CERT" || ! cmp -s "$SRC_PRIVATE_KEY" "$DST_PRIVATE_KEY"; then
        sudo cp "$SRC_PUBLIC_CERT" "$DST_PUBLIC_CERT"
        sudo cp "$SRC_PRIVATE_KEY" "$DST_PRIVATE_KEY"
        sudo systemctl restart minio
        echo "MinIO certificates updated and service restarted at $(date)" >> /var/log/minio_cert_update.log
        send_email "MinIO Certificates Updated" "MinIO certificates were updated and the service was restarted on $(date)."
    else
        echo "No changes detected in MinIO certificates at $(date)" >> /var/log/minio_cert_update.log
        send_email "No Changes in MinIO Certificates" "No changes were detected in MinIO certificates on $(date)."
    fi
    ```

    Here you need to replace your-mailjet-api-key, your-mailjet-api-secret, your-email@example.com and yourdomain.com

    1. Get Api Credentials from mailJet visit https://www.mailjet.com


3. Changing permissions to execute update_minio_certs.sh

    ```bash
    sudo chmod +x /usr/local/bin/update_minio_certs.sh
    ```
    
4.  Update Cron Job or Systemd Timer

    ```bash
    sudo crontab -e
    ```

    Add the following line to run the script every day at midnight:

    ```bash
    0 0 * * * /usr/local/bin/update_minio_certs.sh
    ```

5. Install mailjet-rest python module

    ```bash
    pip install mailjet-rest
    ```

6. Test the script 

    ```bash
        cd /usr/local/bin
        ./update_minio_certs.sh
    ```

You can connect to my MiniIo Server using terminal 
```bash
  mc alias set myminio https://arpansahu.me api_key api_secret --api S3v4
  mc ls
```



# Website Uptime Monitor

This project monitors the uptime of specified websites and sends an email alert if any website is down or returns a non-2xx status code. The project uses a shell script to set up a virtual environment, install dependencies, run the monitoring script, and then clean up the virtual environment.

## Prerequisites

- Python 3
- Pip (Python package installer)
- Mailjet account for email alerts
- Cron for scheduling the script

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/website-uptime-monitor.git
cd website-uptime-monitor
```

### 2. Create a `.env` File

Create a `.env` file in the root directory and add the following content:

```env
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_SECRET_KEY=your_mailjet_secret_key
SENDER_EMAIL=your_sender_email@example.com
RECEIVER_EMAIL=your_receiver_email@example.com
```

## Running the Script

To run the script manually, give permissions and execute:

```sh
chmod +x ./setup_and_run.sh
./setup_and_run.sh
```

```sh
chmod +x ./docker_cleanup_mail.sh
./docker_cleanup_mail.sh
```

## Setting Up a Cron Job

To run the script automatically at regular intervals, set up a cron job:

1. Edit the crontab:

```sh
crontab -e
```

2. Add the following line to run the script every 5 hours:

```sh
0 */5 * * * /bin/bash /root/arpansahu-one-scripts/setup_and_run.sh >> /root/logs/website_up_time.log 2>&1
0 0 * * * export MAILJET_API_KEY="MAILJET_API_KEY" && export MAILJET_SECRET_KEY="MAILJET_SECRET_KEY" && export SENDER_EMAIL="SENDER_EMAIL" && export RECEIVER_EMAIL="RECEIVER_EMAIL" && /usr/bin/docker system prune -af --volumes > /root/logs/docker_prune.log 2>&1 && /root/arpansahu-one-scripts/docker_cleanup_mail.sh
```

# Integrating Jenkins

* Now Create a file named Jenkinsfile at the root of Git Repo and add following lines to file

```bash
pipeline {
    agent { label 'local' }
    environment {
        ENV_PROJECT_NAME = "arpansahu_one_scripts"
    }
    stages {
        stage('Initialize') {
            steps {
                script {
                    echo "Current workspace path is: ${env.WORKSPACE}"
                }
            }
        }
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
    }
    post {
        success {
            script {
                // Retrieve the latest commit message
                def commitMessage = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
                if (currentBuild.description == 'DEPLOYMENT_EXECUTED') {
                    sh """curl -s \
                    -X POST \
                    --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
                    https://api.mailjet.com/v3.1/send \
                    -H "Content-Type:application/json" \
                    -d '{
                        "Messages":[
                                {
                                        "From": {
                                                "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                                "Name": "ArpanSahuOne Jenkins Notification"
                                        },
                                        "To": [
                                                {
                                                        "Email": "$MY_EMAIL_ADDRESS",
                                                        "Name": "Development Team"
                                                }
                                        ],
                                        "Subject": "Jenkins Build Pipeline your project ${currentBuild.fullDisplayName} Ran Successfully",
                                        "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed",
                                        "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is now deployed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                                }
                        ]
                    }'"""
                }
                // Trigger the common_readme job for all repositories"
                build job: 'common_readme', parameters: [string(name: 'environment', value: 'prod')], wait: false
               
            }
        }
        failure {
            sh """curl -s \
            -X POST \
            --user $MAIL_JET_API_KEY:$MAIL_JET_API_SECRET \
            https://api.mailjet.com/v3.1/send \
            -H "Content-Type:application/json" \
            -d '{
                "Messages":[
                        {
                                "From": {
                                        "Email": "$MAIL_JET_EMAIL_ADDRESS",
                                        "Name": "ArpanSahuOne Jenkins Notification"
                                },
                                "To": [
                                        {
                                                "Email": "$MY_EMAIL_ADDRESS",
                                                "Name": "Developer Team"
                                        }
                                ],
                            "Subject": "Jenkins Build Pipeline your project ${currentBuild.fullDisplayName} Ran Failed",
                            "TextPart": "Hola Development Team, your project ${currentBuild.fullDisplayName} deployment failed",
                            "HTMLPart": "<h3>Hola Development Team, your project ${currentBuild.fullDisplayName} is not deployed, Build Failed </h3> <br> <p> Build Url: ${env.BUILD_URL}  </p>"
                        }
                ]
            }'"""
        }
    }
}
```

Note: agent {label 'local'} is used to specify which node will execute the jenkins job deployment. So local linux server is labelled with 'local' are the project with this label will be executed in local machine node.

* Configure a Jenkins project from jenkins ui located at https://jenkins.arpansahu.me

Make sure to use Pipeline project and name it whatever you want I have named it as per great_chat

![Jenkins Pipeline Configuration](https://github.com/arpansahu/arpansahu-one-scripts/raw/main/Jenkinsfile.png)

In this above picture you can see credentials right? you can add your github credentials and harbor credentials use harbor-credentials as id for harbor credentials.
from Manage Jenkins on home Page --> Manage Credentials

and add your GitHub credentials from there

* Add a .env file to you project using following command (This step is no more required stage('Dependencies'))

    ```bash
    sudo vi  /var/lib/jenkins/workspace/arpansahu_one_script/.env
    ```

    Your workspace name may be different.

    Add all the env variables as required and mentioned in the Readme File.

* Add Global Jenkins Variables from Dashboard --> Manage --> Jenkins
  Configure System
 
  * MAIL_JET_API_KEY
  * MAIL_JET_API_SECRET
  * MAIL_JET_EMAIL_ADDRESS
  * MY_EMAIL_ADDRESS

Now you are good to go.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Documentation

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Javascript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://www.javascript.com/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)
[![Github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://www.github.com/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
![Harbor](https://img.shields.io/badge/HARBOR-TEXT?style=for-the-badge&logo=harbor&logoColor=white&color=blue)(https://goharbor.io/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-326ce5.svg?&style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=Jenkins&logoColor=white)](https://www.jenkins.io/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/en/)
![MINIIO](https://img.shields.io/badge/MINIO-TEXT?style=for-the-badge&logo=minio&logoColor=white&color=%23C72E49)(https://min.io/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![Mail Jet](https://img.shields.io/badge/MAILJET-9933CC?style=for-the-badge&logo=minutemailer&logoColor=white)](https://mailjet.com/)



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

SECRET_KEY=

DEBUG=

ALLOWED_HOSTS=

MAIL_JET_API_KEY=

MAIL_JET_API_SECRET=

AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_STORAGE_BUCKET_NAME=

BUCKET_TYPE=

DOMAIN=

PROTOCOL=

DATABASE_URL=

REDIS_CLOUD_URL=

# SENTRY
SENTRY_ENVIRONMENT=

SENTRY_DSH_URL=

# deploy_kube.sh requirements

HARBOR_USERNAME=

HARBOR_PASSWORD=


