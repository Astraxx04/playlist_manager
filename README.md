
# Playlist Manager

A simple CRUD API implemented using Django and the Django Rest Framework which supports song and playlist management feature.


## API Endpoints specifications

- Create new song: This endpoint is used to add a new song entry in the songs table.
- List available songs: This endpoint is used to list all the available songs in the app.
- Create new playlist: This endpoint is used to add a new playlist entry in the playlists table.
- List available playlists: This endpoint is used to list all the available playlists in the app.
- Edit playlist metadata: This endpoint is used to change the name of an existing playlist.
- Delete playlist: This endpoint is used to delete an existing playlist.
- List playlist songs: This endpoint is used to list all the songs associated with a playlist.
- Move playlist song: This endpoint is used to move a song up and down in a playlist i.e., reposition it.
- Remove playlist song: This endpoint is used to remove a song from a playlist.


## Run Locally

Clone the project:

```bash
git clone https://github.com/Astraxx04/playlist_manager.git
```

Go to the project directory:

```bash
cd playlist_manager
```

Create and activate a virtual environment:

```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows, use `myenv\Scripts\activate`
```

Install project dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

Run Django migrations:

```bash
python manage.py migrate
```

Start the Django development server:

```bash
python manage.py runserver
```

## Deployed Endpoint

[https://astraxx.pythonanywhere.com](https://astraxx.pythonanywhere.com)