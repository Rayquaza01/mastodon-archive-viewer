# Mastodon Archive Viewer
A python script to take a mastodon archive and convert it into a human-readable webpage for viewing.

# Features:
* Organizes your old posts into a conveniently readable timeline
* Includes media attachments in posts
* Include polls in posts
* Exclude DMs from archive page
* Preserves content warnings/summaries
* Permalink to posts
* Permalink to parent post for replys

# Usage
<b>With Python:</b>
* To make a webpage to view your archive, just place the `html_from_archive.py` script in the root of the archive (the folder that has `outbox.json` and `media_attachments` in it) and run it using python3
* * From the command line: `python3 html_from_archive.py`
* * You can also set it as executable and run it directly or, on Windows, right click and open it with python 3.
* Open the resulting `processed_archive.html` file in your web browser.
