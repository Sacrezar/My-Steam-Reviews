# My Steam Reviews (MSR)

My Steam reviews is a tool that aims to provide a global insight about your steam reviews.

As of now, it returns 10 randoms games that are not yet evaluated. 

## Table of Contents
- [My Steam Reviews (MSR)](#my-steam-reviews-msr)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [How to Use](#how-to-use)
    - [Example](#example)
  - [FAQ](#faq)
    - [Why not use the Steam API to retrieve reviews?](#why-not-use-the-steam-api-to-retrieve-reviews)

## Requirements

**Python 3.8.x**

You'll need a Steam API Key, you can get it [there](https://steamcommunity.com/dev/apikey)
<div align="center">
  <img src="/assets/apikey_steam.png"/>
</div>

You'll need to know either your vanity URL or your account ID. You can find one of them in the URL of your account id:

```bash
#Vanity URL
https://steamcommunity.com/id/<vanityURL>
#Account ID
https://steamcommunity.com/profiles/<accountID>
```

**Note:** Your account ID is only numbers and your vanityURL is what you chose when you created it.

## How to Use

I recommend to use a venv but it is not an obligation, here are the following command to do:
```bash
cd My-Steam-Reviews
py -m venv env
.\env\Scripts\Activate.ps1
```
Don't forget to install requirements.
```bash
py -m pip install -r requirements.txt --user
```
After that, you just have to launch the script:
```bash
py main.py
```
The first time, It will ask you some information and then fetch. 
### Example
<div align="center">
  <img src="/assets/fetching_eg.png"/>
</div>

## FAQ
### Why not use the Steam API to retrieve reviews?
As far as I know, it is not possible to use the Steam API that way.
