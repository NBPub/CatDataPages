# <img src="/static/navbar.png" title="Cat"> CatDataPages <img src="/static/revcat.png" title="caT">
Source code for a Flask website populated with data from the CatAPI, hosted on Render.

>## **[Cat-Data-Pages.onrender.com](https://cat-data-pages.onrender.com/)**

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Jinja](https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=purple)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=purple)


## Contents
- [Motivation](motivation)
- [Features](#features)
  - [Cat Breed Information](#cat-breed-information)
  - [API](#json-api)
  - [Data Demonstration](#data-demonstration)
- [Deployment](#deployment)
  - [Render](#render)
  - [Local](#local-installation)
- [Updates](#updates)

## Motivation
Make an interesting, fun page using data on cat breeds provided from [The Cat API](https://thecatapi.com/). Include details on data processing for demonstration/education.

## Features

### Cat Breed Information
   * [List index](https://cat-data-pages.onrender.com/cats/) of [data pages](https://cat-data-pages.onrender.com/random/cat/) for each breed
   * Side-by-side [comparison page](https://cat-data-pages.onrender.com/compare)
   * Choropleth  [map](https://cat-data-pages.onrender.com/graphs/map) of cat breed origins
### JSON API
   * Detailed descriptions with [examples](https://cat-data-pages.onrender.com/explore/api_info/)

| | Description | Scheme | 
| :----: | --- | --- |
| **Random Cat Image** | random cat image, updated every 10 minutes | [api/image](https://cat-data-pages.onrender.com/api/image) |
| **Breed Names** | list of cat breeds, helpful for data requests | [api/names](https://cat-data-pages.onrender.com/api/names) |
| **Cat Breed Data** | `type` *info* / *stats* / *graph* <br>for a specified or random `cat`| **api/\<cat\>/\<type\>**<br>[info](https://cat-data-pages.onrender.com/api/random/info), [stats](https://cat-data-pages.onrender.com/api/random/stats), [graphs](https://cat-data-pages.onrender.com/api/random/graph) |

### Data Demonstration
  * [Pages](https://cat-data-pages.onrender.com/data/story) detailing how the CatAPI data was processed and presented
    * Pandas, Matplotlib, and Plotly code demonstration and discussion
  * [Pages](https://cat-data-pages.onrender.com/explore/data) analyzing the overall data distributions
 
## Deployment
The current version of this project was built with Python 3.10, and the packages listed in [requirements.txt](requirements.txt). 

`pip install -r requirements.txt`

### Render
Cat-Data-Pages can be run in earlier Python versions using the more general [requirements for render](requirements_render.txt), which does not list specific package versions.

`pip install -r render_requirements.txt`

This was utilized to avoid build errors in Render.
```shell
# settings
Name = Cat-Data-Pages
Branch = main
Build Command = pip install --upgrade pip setuptools wheel && pip install -r requirements_render.txt
Start Command = gunicorn -w 2 --threads 4 app:app

# environment
PYTHON_VERSION = 3.10.9
TZ = America/Los_Angeles
```
*[gthread](https://docs.gunicorn.org/en/latest/design.html#gthread-workers) worker type used instead of [sync](https://docs.gunicorn.org/en/latest/design.html#sync-workers) due to threads > 1*

### Local Installation
This project can be deployed locally using the default Flask Werkzeug server. 
Download the source [code](https://github.com/NBPub/CatDataPages/archive/refs/heads/main.zip) to a directory and see the Flask [documentation](https://flask.palletsprojects.com/) 
help setting up a virtual environment, installing requirements, and options for running the application.

Run in debug mode:
```shell
cd your-directory
# activate virtual environment
flask --debug run
```

## Updates
This project was recently updated (Dec 2021 --> Dec 2022) as I moved it to [Render](https://render.com/) from [Heroku](https://www.heroku.com/).

 * Documentation on Github
   * will leave sparse and provide links to project and/or screenshots
 * Improved formatting for some pages, mainly widened margins
   * source code links in data story pages, version list in homepage footer
 * Bugfixes for saving graphs (create folder if not exists), and generating map
 * Changed method of saving random cat image
   * from txt file with link --> JSON file with dictionary --> storing dictionary in memory
   * cleaned up code a little, changed to class
   * added try / except block in case of empty return from *thecatapi*
 * **Simple API and description page**
   * Returns URL, time remaining for random cat image
   * Returns list of cat names to facilitate other requests
   * Returns graphs/information/stats for a particular or random cat
 * Gunicorn deployment on Render, associated requirements file
   * optimizing # workers / threads . . .