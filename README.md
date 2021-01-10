# About this project

I often build dashboards and consoles that link to outside websites, 
and it is a nice UX perk to see the site's favicon next to the link.
As it turns out, not all websites publish their favicon at 
example.com/favicon.ico, which results in 404 and broken images.
I made this little api and script to automatically hunt-down that
favicon, and as a last resort, generate one.

# Features

  - All favicons are stored/cached locally, so you only pay the download
penalty once. You can warm-up your cache with a list of domains and a shell
script to curl those domains to the favicon API

  - Icon generated if there really is no favicon to be found for that domain

# API Endpoints

There is only one endpoint. `http://localhost:8000/?url=example.com`

## Parameters

  - url: the url of the web page you want the favicon from


# Getting started (development)

This is a really simple app to get started with.

  1. `git clone git@bitbucket.org:bkmk/favicon-getter.git`
  1. `cp docker-compose.sample.yml docker-compose.yml`
  1. `cp Makefile.sample Makefile`
  1. `cp env.sample env env.prod` (one for local and prod if that is your thing)
  1. edit HOST in Makefile of your live endpoint
  1. check the `docker-compose.yml` settings (I have some traefik stuff in there) 


Personally, I like JetBrain's PyCharm Professional to work in a
full debugged environment. 

# Deploying to production

I use `docker-compose`. See the samples.

# Other favicon grabbers

  - [pyfav](https://github.com/phillipsm/pyfav): a simple Python library that helps you get a favicon for a supplied URL.
  - [besticon](https://github.com/mat/besticon): A favicon service written in Go https://icons.better-idea.org
  - [favicongrabber.com](https://github.com/antongunov/favicongrabber.com): A NodeJS app to grab favicons.