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

There is only one endpoint. favgetter.com/?domain=example.com

## Parameters

  - domain: the domain name (eg - facebook.com)
  - favicon: this is a full path url (eg - http://example.com/favicon.ico) to
    an alternative favicon. This is useful if you absolutely cannot get the script
    to find the right favicon. 

To refresh a domain: `curl http://localhost:5000/?domain=facebook.com&refresh=true`


# Getting started (development)

This is a really simple app to get started with.

  1. `git clone git@bitbucket.org:bkmk/favicon-getter.git`
  2. `venv .`
  3. `source venv/bin/activate`
  4. `pip install -r requirements.txt`
  5. `python favicon.py`

# Deploying to production

You should be able to deploy using many methods. Personally, I use a home-grown
'push-to-deploy' -- kind of like Heroku.

# Other favicon grabbers

  - (pyfav)[https://github.com/phillipsm/pyfav] (a simple Python library that helps you get a favicon for a supplied URL.)
  - (besticon)[https://github.com/mat/besticon] (A favicon service written in Go https://icons.better-idea.org)
