# Albatross
Analysis of Lenses & Bodies for Applied Targeted Recommendations, Original Content, and Style-based Scoring

<img src="src/static/images/albatross.webp" height="300" />

## URL

https://albatross.internal-services.mpb.com
(May be slow to initially load, as the instance is shut down when not in use and started up when called)

## Overview


Albatross is a single-page web application designed to help photographers understand their shooting patterns, analyse EXIF data across multiple images, and receive personalised gear recommendations.

Built with Flask, Jinja2, and SQLite, Albatross keeps image files local, processes only EXIF metadata, and uses a local LLM to suggest gear upgrades tailored to a user's photographic habits.

## API Contract
The full API specification is available in `/static/openapi.yaml`, or can be rendered as a swagger page at `/swagger`


 ## Setup

You can set up Albatross locally by following these steps:
  * Clone the repository
  * Run `mpb setup`
  * Check the tests pass, by running `mpb test`
  * In Pycharm, run the saved `run-albatross-locally` run configuration
  * Open your browser and navigate to `http://127.0.1:8080/`


 ## Features  

 * Analyze multiple images at once without uploading actual image data  
 * Classify photographers by shooting style (“The Stargazer”, “The Naturalist”, etc.)  
 * Break down camera & lens usage with detailed visuals and stats  
 * Get AI-powered gear upgrade suggestions at 3 budget levels  
 * Visualize focal ranges, exposure metrics, and EXIF-based behavior  
 * Persist full analysis for future reference (future login support)  
 * Generate shareable classification cards for social media  

## Deployment

Albatross is deployed to Google Cloud Platform’s Cloud Run as a Cloud Run Service.

This means that the service is automatically scaled up or down depending on incoming traffic, and even scales to zero when there have been no requests for a while to optimise costs.

Albatross uses a Jenkins pipeline for CI/CD that essentially builds the docker image and publishes it in Google’s Artifact Registry , which Cloud Run detects and deploys a new version.

The configuration for making Albatross deployable via cloud run lives here in the devops terraform config and are fairly easy to copy if you wanted to apply them to your own project (find and replace ‘albatross’ with your own project name)

## How It Works

### 1. Index View (Frontend)
* User selects JPG images via a file input.
* Images are processed entirely in-browser to extract EXIF data.
* Extracted metadata is compiled into a JSON payload.
* Payload is sent to the Flask backend via a POST request.

### 2. Backend (Flask Server)
* Receives and processes EXIF data.
* Performs the following:
* Builds a list of cameras/lenses used (Camera, Lens models)
* Creates a unified model per image (ImageExif)
* Analyzes overall shooting behavior (Metrics)
* Classifies photographer type (PhotographerClassification)
* Queries a local LLM for gear recommendations (Recommendations)
* Persists all outputs to SQLite under a session ID.
* Renders a detailed HTML report with Jinja templates.

### 3. Results View (Frontend)
Displays:
* Photographer classification and detailed score
* Breakdown of camera/lens usage
* Charts (bar, line, radar) of focal range and exposure
* Gear upgrade suggestions + links to MPB
* Content + challenges tailored to the user’s shooting type

## Flow Diagram
```mermaid
---
config:
  layout: elk
  look: classic
---
flowchart TD
 subgraph Browser["Browser"]
        A1["User selects JPG images"]
        A2["Extract EXIF data in browser"]
        A3["Send EXIF JSON to Flask endpoint"]
        A4["Results page rendered"]
  end
 subgraph subGraph1["Flask Server"]
        B1["Receive EXIF payload"]
        B2["Build Camera & Lens list"]
        B3["Create ImageExif models"]
        B4["Generate collective Metrics"]
        B5["Classify photographer"]
        B6["Generate gear recommendations - LLM"]
        B7["Persist all data with session ID"]
        B8["Render Jinja templates"]
  end
 subgraph Database["Database"]
        D1["Camera"]
        D2["Lens"]
        D3["ImageExif"]
        D4["Metrics"]
        D5["PhotographerClassification"]
        D6["Recommendations"]
  end
    A1 --> A2
    A2 --> A3
    A3 --> B1
    B1 --> B2 & B3 & B4 & B5 & B6
    B2 --> D1 & D2 & B7
    B3 --> D3 & B7
    B4 --> D4 & B7
    B5 --> D5 & B7
    B6 --> D6 & B7
    B7 --> B8
    B8 --> A4
    style Browser fill:#f9f,stroke:#333,stroke-width:1px
    style Database fill:#bfb,stroke:#333,stroke-width:1px
    style subGraph1 fill:#FFE0B2,color:#FFFFFF,stroke:#FFFFFF

  ```

## Environment variable configuration
All environment variables are defined with sensible defaults, so the application should be runnable without any external configuration. However, if you want to change them from the defaults:

| Name                                  | Type     | Default Value    | Purpose                                                                  | Value for tests, if different |
|---------------------------------------|----------|------------------|--------------------------------------------------------------------------| ----------------------------- |
| LLM_ENABLED**                         | Boolean* | true             | Enable or disable LLM queries                                            | false                         |
| LLM_PRODUCT                           | String   | gemini           | Define which LLM product we are targeting                                |                               |
| LLM_MODEL                             | String   | gemini-2.0-flash | Define which LLM model to use                                            |                               |
| DB_ENABLED                            | Boolean* | true             | Whether to persist results to the database                               | false                         |
| SEARCH_PROXY_URL                      | Boolean* | true             | The url for the proxied search service                                   |                               |
| LLM_RECOMMENDATION_OPTIONS_PER_BUDGET | Integer  | 3                | For each recommendation table, for each budget, how many rows to request |                               |

`*` Note that boolean types are passed as strings, with values equal to 'true' being `true` and all other values being `false`.

`**` Useful for running locally without incurring costs when we don't need to load recommendations.


## Tech Stack
* Frontend: Vanilla JS + in-browser EXIF parsing
*	Backend: Python, Flask, Jinja2
*	Data: SQLite + SQLAlchemy ORM
*	AI: Local LLM instance (future: SLM trained on MPB data)
*	Charts: Chart.js

## Future Roadmap
* User login & session history
* Custom-trained small language model (SLM) from MPB inventory
