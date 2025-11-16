# Energy prices tracker

## Table of contents
1. [What-it-is?](#What-it-is?)
2. [Installation](#Installation)
3. [Used-technologies](#Used-technologies)

## What it is?
A small webapp to track different energy prices.\
Able to view some technical indicators to see the price changes.\
Used api: [commoditypriceapi](https://commoditypriceapi.com/)\
I use a free account, but have a lot of requests to spend, but please only use as much as you need.

## Installation
```bash
git clone https://github.com/somabencsik/energy-tracker.git
cd energy-tracker
docker compose build
docker compose up
```
Sometimes for the first time the backend fails to start, because database is not started yet, despite the `depends_on` statement.\
Please, restart the docker compose and it should be good to go!

## Used technologies
- Database: postgres
- Backend: Python-FastAPI
- Frontend: Python-dash
- Build&Run: docker, docker compose