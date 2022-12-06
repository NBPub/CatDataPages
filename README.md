# CatDataPages
Source code for a Flask website populated with data from the CatAPI.

*add image(s)*

## Motivation
Make an interesting, fun page using data on cat breeds provided from [The Cat API](https://thecatapi.com/). Include details on data processing for demonstration/education.

Visit the page for more information. *add links when available*


## Background
This project was recently updated (12-2022), as I need to move to a Heroku alternative. Dependencies were updated, and minor changes to code were added.

### Updates

 * Documentation on Github
   * will leave sparse and provide links to project and/or screenshots
 * Improved formatting for some pages, mainly margins
 * Bugfixes for saving graphs (create folder if not exists), and generating map
 * Changed method of saving random cat image
   * from txt file with link --> JSON file with dictionary --> storing dictionary in memory
   * cleaned up code a little, changed to class
 * Simple API and description page
   * Returns URL, time remaining for random cat image
   * Returns list of cat names to facilitate other requests
   * Returns graphs/information/stats for a particular or random cat
  * Docker build for deployment
