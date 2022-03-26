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

### Step 2. Install `heroku` CLI

I used the instructions provided by the Heroku resource here: https://devcenter.heroku.com/articles/git, and installed the [CLI](https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli) tool. Since I use Arch Linux, my installation was as simple as:

```
yay -S heroku-cli
```

Next thing I needed to do was login:

```
heroku login
```

### Step 3. Setup the app deployment

Since I created the app in the Heroku UI in Step 1, I needed to add it as an existing application and not create a new one. The command for this is:

```
heroku git:remote -a sanicbook
```

Next, I want to use the Python "buildpack", but because I have the repository nested I cannot use the default. Therefore, following these steps I ran:

```
heroku buildpacks:set https://github.com/timanovsky/subdir-heroku-buildpack 
heroku buildpacks:add heroku/python
heroku config:set PROJECT_PATH=application
```
