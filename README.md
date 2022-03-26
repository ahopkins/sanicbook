# Getting started

```
$ docker-compose build
```

```
$ docker-compose up
```


## How I released this project?

This project has been deployed using [Heroku](https://www.heroku.com). After signing up for an account, I followed these steps.

### Step 1. Create new app

Following the steps was pretty simple. Since I am deploying a single application, I chose an "app" and not a "pipeline." I then selected the GitHub deployment method amd followed the prompts to connect my repository `ahopkins/sanicbook`.

Heroky offered the option of "automatic deploys", which I elected to enable. Since the default branch of my application is `main`, I made sure that that was selected as my "deploy branch".
