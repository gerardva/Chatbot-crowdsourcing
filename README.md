# FaceWork Microwork Chatbot

This is the Facebook Messenger chatbot for microwork made by group 6 for the course IN4325 Information Retrieval.

## Using the chatbot

Go to [the Facebook page](https://www.facebook.com/Microwork-Chatbot-1849085282000551) and click 'Message' to chat with our bot. You need to be added as developer or tester of the Facebook app, otherwise it will give you the silent treatment. If you post your Facebook account name on our slack channel, we will add you as soon as possible.

## Project structure

The project directories and files are structured in the following tree:

- `api`
    - `apiserver.py` webserver that contains logic for the requester and worker API
    - `database.py` initializes database configuration
    - `model.py` datamodel used by both API's
    - `tests` integration tests for both API's
- `chatbot`
    - `api_helper` helper methods to call the worker API
    - `chatbot.py` entry point of chatbot, uses messaging and logger functionality
    - `facebook_helper` helper methods to call facebook API
    - `local_test.py` tests communication with facebook API independently of the code in `api`
    - `logger.py` wraps heroku logging functionality
    - `messaging.py` logic to handle the chatbot interaction flow by reading user messages and replying according to current chatbot state
- `pipelines`
    - `pipeline_1.py` pipeline for Albert Heijn Twitter WebCare evaluation task (Type 1: global content)
    - `pipeline_2.py` pipeline for Albert Heijn ground plan evaluation task (Type 2: local content)
    - `pipeline_3.py` pipeline for Albert Heijn store stocking evaluation task (Type 3: content generation)
    - `reviewPipeline.py` pipeline for generation of review tasks

## Project set up

The following paragraph describe how to set up the project to run and test it locally.

### First run

To run the chatbot (on Windows) execute the following steps:

- Make sure you have installed Python 3 (I used 3.6) and [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). I also assume you have Git installed and know how it works.
- `pip install virtualenvwrapper-win` to install the virtualenv stuff we are going to use. For Unix you need to install `virtualenvwrapper`
- `mkvirtualenv chatbot` to enter our virtual environment. It doesn't matter how you call it, but it's useful to remember how you call it.
- `pip install -r requirements.txt` to locally install project dependencies in the virtual environment
- `heroku git:remote -a fathomless-cove-38602` to add the Heroku app to the local git to push the code to. I've already added you to the Heroku app and set it up so it works.

If you run a Unix machine I assume you know how to adapt the above instructions to your own machine.

### Useful for development

- Execute `workon chatbot` to re-enter the virtual environment if you left it for some reason (although I cannot imagine spending your time other than on this course naturally).
- Execute `git push heroku master` to deploy the chatbot to Heroku. In order to push a branch different than master to Heroku, execute `git push heroku your-branch-name:master`.
- You can run the chatbot locally with `heroku local`. This will allow you to run the application locally, with the heroku database. If you have MySQL installed you can also run the app with your local database. In order to do this you need to enter your database settings in `api/config/settings.json`, and run the server app with `python ./setup.py`.

### Testing locally

- Once you have the app running locally you can run the API tests using `python -m unittest discover`.

To test the communication between the chatbot and facebook do the following:

- Add a new Environment variable to your machine, with name `PAGE_ACCESS_TOKEN` and as value the token which can be found in Heroku at Settings -> Config vars
- Run the server locally as described above using the `heroku local` command, this will start the server at localhost:5000
- Start the chatbot/local_test.py script and follow the instructions
