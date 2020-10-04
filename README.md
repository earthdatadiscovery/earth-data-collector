# EARTH DATA COLLECTOR

## PROJECT

This repository is part of a project created by the `Earth Data Discovery Team` for the 2020 Space Apps Challenge

## GOAL

The goal of this repository is to fetch data from the [CMR Earth Data](https://cmr.earthdata.nasa.gov) and index it into a [MeiliSearch](https://github.com/meilisearch/MeiliSearch) search Engine.

This is a necesary step to create an accessible and open interface for finding Earth Science datasets.

## HOW TO USE IT

### Preparing your environment

#### Clone the repository and install dependencies. You need `python 3` and `pip`

```bash
git clone https://github.com/earthdatadiscovery/earth-data-collector.git
cd earth-data-collector
pip install -r requirements.txt
```

#### RUN A MEILISEARCH INSTANCE

Here we use a docker image, but there are other ways to [install here](https://docs.meilisearch.com/guides/introduction/quick_start_guide.html#getting-started)

```bash
docker run -it -p 7700:7700 --name MeiliEarthData getmeili/meilisearch:latest ./meilisearch
```

#### ADD YOUR MEILISEARCH SETTINGS

You need to set up your MeiliSearch URL (and eventually the API Key if you want to use one) in `services/meilisearch/meilisearch.py`

#### RUN IT! GO GO GO!

```bash
python collector.py
```
