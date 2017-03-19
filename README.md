# Microwork Chatbot

This is a Facebook Messenger chatbot for the course IN4325 Information Retrieval.

## Project set up

The inital skeleton is based on [hartleybrody's bot](https://github.com/hartleybrody/fb-messenger-bot), with some modifications to make it work on Python 3 and Windows (most notably, replacing gunicorn with waitress). More information about it can be found in [this tutorial](https://blog.hartleybrody.com/fb-messenger-bot/).

### First run

To run the chatbot (on Windows) execute the following steps:

- Make sure you have installed Python 3 (I used 3.6) and [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). I also assume you have Git installed and know how it works.
- `pip install virtualenvwrapper-win` to install the virtualenv stuff we are going to use. For Unix it is probably enough to install `virtualenvwrapper`
- `mkvirtualenv chatbot` to enter our virtual environment. It doesn't matter how you call it, but it's useful to remember how you call it.
- `pip install -r requirements.txt` to locally install project dependencies in the virtual environment
- `heroku git:remote -a fathomless-cove-38602` to add the Heroku app to the local git to push the code to. I've already added you to the Heroku app and set it up so it works.

If you run a Unix machine I assume you know how to adapt the above instructions to your own machine.

### Useful for development

- Execute `workon chatbot` to re-enter the virtual environment if you left it for some reason (although I cannot imagine spending your time other than on this course naturally). 
- Execute `git push heroku master` to deploy the chatbot to Heroku. In order to push a branch different than master to Heroku, execute `git push heroku your-branch-name:master`.
- You can run the chatbot locally with `heroku local`, but that doesn't do much other than verify it's working.
- Go to [the Facebook page](https://www.facebook.com/Microwork-Chatbot-1849085282000551) and click 'Message' to chat with our bot. Make sure you are admin of the page and developer of the Facebook app, otherwise it will give you the silent treatment.

### Testing locally

To test the chatbot functionality without first deploying to heroku do the following:

- Add a new Environment variable to your machine, with name `PAGE_ACCESS_TOKEN` and as value the token which can be found in Heroku at Settings -> Config vars
- Run the server locally as described above using the `heroku local` command, this will start the server at localhost:5000
- Simulate the webhooks with a application like Postman, you can do POST request to localhost:5000/chatbot like this:

###### Headers

`Content-Type : application/json`

###### Body

```{
  "object": "page",
  "entry": [
    {
      "messaging": [
        {
          "sender": {
            "id": "YOUR_FACEBOOK_ID"
          },
          "message": {
            "seq": 7425,
            "mid": "mid.$cAAaRu-bCUn5hCLcJoFa13HGOx2wQ",
            "text": "YOUR TEXT"
          },
          "timestamp": 1489673240992,
          "recipient": {
            "id": "1849085282000551"
          }
        }
      ],
      "id": "1849085282000551",
      "time": 1489673241040
    }
  ]
}
```
