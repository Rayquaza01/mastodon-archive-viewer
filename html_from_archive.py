#!/usr/bin/env python3
import json
from os import path
import html

with open("outbox.json", "r", encoding="utf-8") as outbox_file:
    outbox = json.loads(outbox_file.read())
with open("actor.json", "r", encoding="utf-8") as actor_file:
    actor = json.loads(actor_file.read())

ACTOR_ID = actor.get("id")

#map the outbox down to the actual objects
statuses = [status.get("object") for status in outbox.get("orderedItems")]

articles = []
#attachment urls may begin with "/media/" or something else we dont want
# start with an offset of 1 to avoid checking root for /media or something else wrong
PATH_OFFSET = 1

POST_TEMPLATE = '''<div class="m-post" id="{6}">
    <div class="m-post-header">
        <img src="avatar.png" class="m-pfp">
        <div class="m-user-block">
            <div class="m-display-name">{4}</div>
            <div class="m-user-name">@{5}</div>
        </div>
        {7}
        <a href="#{6}" class="m-permalink">{0}</a>
    </div>
    <details>
        <summary>{1}</summary>
        <div class="m-post-body">{2}</div>
        <div class="m-media">{3}</div>
    </details>
</div>'''

POST_TEMPLATE_NO_CW = '''<div class="m-post" id="{5}">
    <div class="m-post-header">
        <img src="avatar.png" class="m-pfp">
        <div class="m-user-block">
            <div class="m-display-name">{3}</div>
            <div class="m-user-name">@{4}</div>
        </div>
        {6}
        <a href="#{5}" class="m-permalink">{0}</a>
    </div>
    <div class="m-post-body">{1}</div>
    <div class="m-media">{2}</div>
</div>'''

REPLY_TEMPLATE = '''<a href="{0}" title="Parent Post">⬆️</a>'''

VIDEO_TEMPLATE = '''<video controls muted src="{0}" class="status__image" alt="{1}" title="{1}">There should be a video here.</video>'''
IMAGE_TEMPLATE = '''<img class="status__image" src="{0}" alt="{1}" title="{1}">'''

STYLESHEET = '''<style>
:root {
  --accent: #dc8add;

  --bg: #c0bfbc;
  --fg: black;

  --post-bg: #deddda;
  --post-drop-shadow: #deddda;

  --link: #1a5fb4;

  font-size: 16px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --accent: #613583;

    --bg: #3d3846;
    --fg: white;

    --post-bg: #241f31;
    --post-drop-shadow: black;

    --link: #99c1f1;

    font-size: 16px;
  }
}

html {
  scroll-behavior: smooth;
}

html, body {
  background-color: var(--bg);
}

body {
  font-family: Verdana;
  color: var(--fg);

  font-size: 1em;
}

a {
  color: var(--link);
  text-decoration: none;
}

.hashtag {
  color: var(--fg);
}

a:hover {
  text-decoration: underline;
}

#header {
  text-align: center;

  margin-bottom: 2%;
}

#header > img {
  border-radius: 50%;
  width: 10em;
}

#feed {
  margin: 0 10% 0;
}

.m-post {
  border-radius: .75em;
  background-color: var(--post-bg);
  padding: 1.5em;
  margin-bottom: 2em;

  text-wrap: wrap;

  box-shadow: .25em .25em .25em var(--post-drop-shadow);
}

.m-post:target {
  box-shadow: .5em .5em .5em var(--accent);
}

.m-media > * {
  max-width: 100%;
  max-height: 20vh;
}

.m-post-header {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.m-pfp {
  border-radius: 50%;
  height: 3em;
  margin-right: 1em;
}

.m-display-name {
  font-weight: bold;
}

.m-user-block {
  flex-grow: 1;
}

.m-permalink {
  color: var(--fg);
  margin-left: 1em;
}

.invisible {
  display: none;
}

.ellipsis:after {
  content: "..."
}

blockquote {
  border-left: .2em solid;
  padding-left: 1em;
  margin-left: 1em;
}
</style>
'''

DATE_SCRIPT = '''<script>
const SECOND_LENGTH = 1000;
const MINUTE_LENGTH = 60 * 1000;
const HOUR_LENGTH = 60 * MINUTE_LENGTH;
const DAY_LENGTH = 24 * HOUR_LENGTH;
const WEEK_LENGTH = 7 * DAY_LENGTH;
const YEAR_LENGTH = 365 * DAY_LENGTH;

function ShortDate(date) {
  const now = new Date();
  const then = new Date(date);

  const diff = now.getTime() - then.getTime();

  if (diff >= YEAR_LENGTH) {
    return Math.floor(diff / YEAR_LENGTH).toString() + "y"
  }

  if (diff >= WEEK_LENGTH) {
    return Math.floor(diff / WEEK_LENGTH).toString() + "w";
  }

  if (diff >= DAY_LENGTH) {
    return Math.floor(diff / DAY_LENGTH).toString() + "d";
  }

  if (diff >= HOUR_LENGTH) {
    return Math.floor(diff / HOUR_LENGTH).toString() + "h";
  }

  if (diff >= MINUTE_LENGTH) {
    return Math.floor(diff / MINUTE_LENGTH).toString() + "m";
  }

  if (diff >= SECOND_LENGTH) {
    return Math.floor(diff / SECOND_LENGTH).toString() + "s";
  }

  return date;
}

[...document.querySelectorAll(".m-permalink")].forEach(item => {
  item.title = item.innerText;
  item.innerText = ShortDate(item.innerText);
})
</script>'''

HEADER = '''<section id="header">
    <img src="avatar.png">
    <div class="m-display-name">{0}</div>
    <div>@{1}</div>
    <div id="actor-summary">{2}</div>
</section>'''

for status in statuses:
    #need to ignore objects that arent status dicts
    if not isinstance(status, dict):
        continue

    # skip DMs!
    if status.get("directMessage"):
        continue

    date = status.get("published")
    summary = status.get("summary")
    htmlContent = status.get("content")
    attachments = status.get("attachment")
    in_reply_to = status.get("inReplyTo")

    REPLY = ""
    if in_reply_to is not None:
        if in_reply_to.startswith(ACTOR_ID):
            parent_id = in_reply_to.rsplit("/", maxsplit=1)[-1]
            REPLY = REPLY_TEMPLATE.format("#" + parent_id)
        else:
            REPLY = REPLY_TEMPLATE.format(in_reply_to)

    statusID = status.get("id").rsplit("/", maxsplit=1)[-1]

    IMAGES = ""

    for attachment in attachments:
        imageURL = attachment.get("url")
        ALT_TEXT = attachment.get("name")
        if ALT_TEXT is None:
            ALT_TEXT = ""
        ALT_TEXT = html.escape(ALT_TEXT, True)
        # only runs the loop for the first media url in the archive
        if PATH_OFFSET == 1:
            while not path.exists(imageURL[PATH_OFFSET:]) and PATH_OFFSET < len(imageURL):
                PATH_OFFSET +=1

        if imageURL[-4:] == ".mp4" or imageURL[-5:] == ".webm":
            IMAGES += VIDEO_TEMPLATE.format(imageURL[PATH_OFFSET:], ALT_TEXT)
        else:
            IMAGES += IMAGE_TEMPLATE.format(imageURL[PATH_OFFSET:], ALT_TEXT)
    if summary:
        article = POST_TEMPLATE.format(
                date,
                summary,
                htmlContent,
                IMAGES,
                actor.get("name"),
                actor.get("preferredUsername"),
                statusID,
                REPLY
        )
    else:
        article = POST_TEMPLATE_NO_CW.format(
                date,
                htmlContent,
                IMAGES,
                actor.get("name"),
                actor.get("preferredUsername"),
                statusID,
                REPLY
        )
    articles.append(article)

with open("processed_archive.html", "w", encoding="utf-8") as outfile:
    # CREATING OUTPUT FILE

    # write head for document
    outfile.write(f'''<!DOCTYPE html>
<html>
    <head>
        <title>Mastodon Archive</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {STYLESHEET}
    </head>
    <body>
        <section id="header">
            <img src="avatar.png">
            <div class="m-display-name">{actor.get("name")}</div>
            <div>@{actor.get("preferredUsername")}</div>
            <div id="actor-summary">{actor.get("summary")}</div>
        </section>
        <div id="feed">
            {"\n".join(articles)}
        </div>
        {DATE_SCRIPT}
    </body>
</html>
''')
