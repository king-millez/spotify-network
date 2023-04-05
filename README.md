# spotify-network

![THE MASS](/.github/img/the%20mass.png)

_This probably break's Spotify's ToS or something. It does not use an official API application and uses your **personal** account to do API requests. **USE AT YOUR OWN RISK**._

---

`spotify-network` is an OSINT tool which gets a Spotify account's following, then their following, then their following, etc (to as many degrees of separation as you want) to create a pretty graph that you can show your friends.

**See the results here: https://twitter.com/King_Millez/status/1643435598852820993**

![2D Mass](/.github/img/image-4.png)

Included is a script which imports the network data into Blender so you can create even prettier 3D visualisations of your stalking endeavours.

## Setup

1. Install dependencies

   ```sh
   pip install -r requirements.txt
   ```

2. Set necessary variables

   In `network.ipynb`, you need to set the `STARTING_PROFILE_ID` constant to a Spotify account ID.

   You get the ID by splitting the account URL after the final slash. For `https://open.spotify.com/user/1239621992`, the ID is `1239621992`.

   ```py
   STARTING_PROFILE_ID = "1239621992"
   ```

3. Set `MAX_DEPTH`. By default it's set to 3, but this may be too much or too little for whatever it is you've trying to do. Keep in mind that this number increases the running time and amount of requests exponentially, and also makes the visualisations _much_ slower
4. Get your Spotify bearer token

   1. In your browser, got to https://open.spotify.com while logged in and hit F12.Then click the `Network` tab
   2. Change the intercept mode to only XHR requests
   3. You should see requests populating the intercept list. Click on a few until you find one which contains `authorization` in the _request_ headers, not the response headers

      ![Example of a Spotify bearer token in the request headers](/.github/img/bearer.png)

   4. Copy the value to your clipboard.

## Usage

1. Once you have your bearer token, click _Run All_ in the Jupyter Notebook
2. You should see a prompt to enter your account token. Abide by the divine request
3. Once you've done this, sit back and relax while the application creates a cool network for your Spotify account
4. Network data will be exported to `{Provided Account ID}.csv`, and the visualisation can be viewed in a browser by opening `{Provided Account ID}.html`

## Importing to Blender

1. Once you've exported the network CSV file, open Blender >= 2.8
2. Click on the `Scripting` tab
3. Click Window > Toggle System Console if you don't have it open yet
4. In `blender.py` (in this repository), change `csv_file_path` to the _absolute_ path of the network CSV file, e.g:

   ```py
   csv_file_path = "C:\\Users\\User\\Desktop\\whatever\\123123123.csv"
   ```

5. Change your Blender render engine to Cycles instead of Eevee (read [this](https://www.katsbits.com/codex/render-engine/)).
6. Delete all objects in your scene. Add some lights if you want. You are the creative.
7. Click play button to run the script. Watch the progress in the System Console.
8. When it's done, do some crazy 3D stuff with your visualisation :)
