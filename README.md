# Salar in Motion

Open monitoring of the Salar del Hombre Muerto (Argentine Puna) with the NISAR radar mission.

Project by **Team Satellite Miner** for the *Dancing with the SARs* challenge of the NASA Space Apps Challenge 2026.

> Status: hackathon prototype. Results are preliminary and have not been validated in the field.

**Interactive application:** https://satelliteminer.github.io/salar-in-motion/

## What it is

An open tool that shows where and how much the surface of the salt flat changed between June and October 2026, as seen by the NISAR L-band radar. It describes changes in the radar signal; it does not attribute causes or assign responsibilities.

It looks at two kinds of surface:

- **Lagoons and wetlands**, which change with the seasons.
- **Evaporation ponds**, which change with industrial operation.

## Preliminary results

All figures compare each date with 10 June 2026 (orbit 118 ascending, frame 165).

- **43 change zones** between 10 June and 20 October 2026, each of at least 0.1 km² with more than 3 dB of change: 25 where the signal increased (21.7 km² in total) and 18 where it decreased (6.8 km²).
- The largest zones correspond to lagoons, a delta and vegetated fluvial plains. The central salt crust barely changes.
- **Persistent change** (same direction, more than 1.5 dB, in at least 3 of the 4 later dates): 12.8 km² where the signal increased and 18.4 km² where it decreased.
- **Evaporation pond sector** (east-southeast of the salar centre): no change through 4 July; from 21 August onward about 2 km² show a signal more than 2 dB lower, and it stays that way in September and October. Sentinel-2 images of 8 June and 26 October show that the ponds already existed in June: their surface state changed, not their number. NISAR has a data gap between 27 July and 10 August, so the exact date of the change is unknown.
- **Los Patos wetland:** almost no persistent change (0.3 km²). **Wetland in the southwest sector:** 2.4 km² with a persistent decrease nearby; radar alone cannot tell the cause.
- The area that changes goes up and down between dates, which shows that part of the change is seasonal.

| Date | Signal increased > 3 dB (km²) | Signal decreased > 3 dB (km²) |
|---|---|---|
| 4 Jul 2026 | 24.8 | 1.9 |
| 21 Aug 2026 | 4.5 | 16.4 |
| 26 Sep 2026 | 17.9 | 13.6 |
| 20 Oct 2026 | 29.3 | 10.5 |

## Data

| Source | Product | Use |
|---|---|---|
| NISAR (NASA/JPL – ISRO) | L2 GCOV, L-band, orbit 118 ascending, frame 165 | Change maps |
| Sentinel-2 (ESA, Copernicus) | L2A true colour | Optical checks |

NISAR dates used: 10 June, 4 July, 21 August, 26 September and 20 October 2026.

The data are not stored in this repository. They are downloaded from the ASF DAAC with a free [NASA Earthdata Login](https://urs.earthdata.nasa.gov) account.

## How to run it

1. Open `nisar_hombre_muerto_auto.ipynb` in Google Colab or Jupyter.
2. Run all cells. The first one installs the libraries.
3. Enter your Earthdata user name and password when asked. The password is not saved in the notebook.
4. Wait for the downloads (large files; each scene is downloaded, cropped and deleted, one at a time).
5. At the end the notebook packs the results in a ZIP file.

Requirements: Python 3.10 or later and the libraries in `requirements.txt`.

The dates are fixed in the `FECHAS_FIJAS` parameter so that results can be reproduced. Without it, every new NISAR pass would change the selected dates.

## Method

1. Search and download of GCOV scenes of one orbit and frame, chosen because it covers the whole study box.
2. Crop of the study area: longitude -67.35 to -66.75, latitude -25.70 to -25.15 (about 60 by 63 km at 20 m pixels).
3. Speckle filter with a 5 × 5 pixel window.
4. HH backscatter difference, in dB, of each date against the first one.
5. Change zones: more than 3 dB of change and at least 0.1 km².
6. Evaporation pond box (longitude -66.898 to -66.868, latitude -25.437 to -25.417): area with more than 2 dB of change, measured separately for each date.
7. Persistent change: same direction and more than 1.5 dB in at least 3 of the 4 later dates.
8. Main zones checked against Sentinel-2 optical images of nearby dates.
9. Surfaces grouped with k-means clustering on HH and HV (not validated).

## Limits

- Five dates, from winter to spring, cannot separate a trend from the seasonal cycle.
- A change in radar signal does not say by itself what changed: it needs optical or field confirmation.
- Thresholds (3 dB, 2 dB, 1.5 dB and 0.1 km²) are not validated in the field.
- NISAR has a data gap from 27 July to 10 August 2026.
- Radar observes the surface: it does not measure groundwater or water quality.
- The tool does not assess environmental impacts.

## Interactive application

The `docs/` folder holds the web application: a map of the signal change for each date, the 43 change zones, the persistent-change layer, a provisional "very dark surface" layer for each date and a chart of the change per date. Open `docs/index.html` in a browser; it needs no server. Published with GitHub Pages, it gets a public address.

The layers in `docs/data/` are generated from the notebook results with:

```
python build_app_layers.py <folder with the unzipped notebook results> docs
```

The script reads the dates and areas from the notebook CSV files, so the application always matches the run.

## Repository contents

| File | What it is |
|---|---|
| `nisar_hombre_muerto_auto.ipynb` | Main notebook: download, crop, change maps, zones, persistent change, pond sector |
| `build_app_layers.py` | Turns the notebook results into the application layers |
| `docs/` | Interactive application (HTML, Leaflet, data layers) |
| `requirements.txt` | Python libraries |
| `LICENSE` | MIT licence |

## Use of AI

A large language model (Claude, by Anthropic) was used as an assistant to write and review most of the data-processing code in the notebook, the application code, the documentation and the translations. The team reviewed the code and is responsible for all content. The choice of challenge, study area, framing, method decisions and interpretation of results are the team's own.

The processing also uses k-means clustering (scikit-learn), a classical machine-learning method, to group surfaces; those groups are not validated. No other AI or machine-learning model is used in the processing, and the project contains no AI-generated images, video or audio.

## Timing

A first run of the data access and processing was done between 10 and 12 November 2026. During the hackathon weekend we re-ran the full processing, added the per-date and persistent-change layers, and built the interactive application, the English materials and this repository.

## Data attribution

- NISAR: NASA/JPL – ISRO, distributed by the Alaska Satellite Facility DAAC.
- Sentinel-2: contains modified Copernicus Sentinel data (2026).
- Base maps in the application: Esri, Maxar, Earthstar Geographics; © OpenStreetMap contributors.
- Leaflet (BSD-2-Clause licence).

This work is not endorsed by NASA.

## Licence

The code is released under the MIT licence. See `LICENSE`.

## Team

Team Satellite Miner (Matías Perco and Franco Agustín Baez), NASA Space Apps Challenge 2026, Universal Event.
