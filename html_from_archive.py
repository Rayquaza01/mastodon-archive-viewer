#!/usr/bin/env python3
import json
from os import path
import datetime
import html

with open("outbox.json", "r") as outbox_file:
	outbox = json.loads(outbox_file.read())
with open("actor.json", "r") as actor_file:
	actor = json.loads(actor_file.read())
#map the outbox down to the actual objects
statuses = [status.get("object") for status in outbox.get("orderedItems")]

articles = []
#attachment urls may begin with "/media/" or something else we dont want
# start with an offset of 1 to avoid checking root for /media or something else wrong
pathOffset = 1

for status in statuses:
	#need to ignore objects that arent status dicts
	if type(status) == type({}):
		date = status.get("published")
		summary = status.get("summary")
		htmlContent = status.get("content")
		attachments = status.get("attachment")
		images = ""
		for attachment in attachments:
			imageURL = attachment.get("url")
			altText = attachment.get("name")
			if altText is None:
				altText = ""
			altText = html.escape(altText, True)
			# only runs the loop for the first media url in the archive
			if pathOffset == 1:
				while not path.exists(imageURL[pathOffset:]) and pathOffset < len(imageURL):
					pathOffset +=1

			if imageURL[-4:] == ".mp4" or imageURL[-5:] == ".webm":
				images += "<video controls muted src='{0}' class='status__image' alt='{1}' title='{1}'>There should be a video here.</video>".format(imageURL[pathOffset:], altText)
			else:
				images += "<img class='status__image' src='{0}' alt='{1}' title='{1}'>".format(imageURL[pathOffset:], altText)
		if summary:
			article = '''<div class="m-post">
	<div class="m-post-header">
		<img src="avatar.png" class="m-pfp">
		<div class="m-user-block">
			<div class="m-display-name">{4}</div>
			<div class="m-user-name">@{5}</div>
		</div>
		<span class="m-permalink">{0}</span>
	</div>
	<details>
		<summary>{1}</summary>
		<div class="m-post-body">{2}</div>
		<div class="m-media">{3}</div>
	</details>
</div>'''.format(date, summary, htmlContent, images, actor.get("name"), actor.get("preferredUsername"))
		else:
			article = '''<div class="m-post">
	<div class="m-post-header">
		<img src="avatar.png" class="m-pfp">
		<div class="m-user-block">
			<div class="m-display-name">{3}</div>
			<div class="m-user-name">@{4}</div>
		</div>
		<span class="m-permalink">{0}</span>
	</div>
	<div class="m-post-body">{1}</div>
	<div class="m-media">{2}</div>
</div>'''.format(date, htmlContent, images, actor.get("name"), actor.get("preferredUsername"),)
		articles.append(article)

outfile = open("processed_archive.html", "w")
styleSheet = '''<style>
body {
  font-family: Verdana;
  background-color: #282C37;
  color: white;
}

a {
  color: #8c8dff;
  text-decoration: none;
}

.hashtag {
  color: white;
}

a:hover {
  text-decoration: underline;
}

#header {
  text-align: center;
}

#header > img {
  border-radius: 50%;
  width: 150px;
}

#feed {
  margin: 0 10% 0;
}

.m-post {
  border: 1px solid;
  border-radius: 25px;
  padding: 10px;
  margin-bottom: 10px;

  text-wrap: wrap;
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
  height: 50px;
  margin-right: 10px;
}

.m-display-name {
  font-weight: bold;
}

.m-user-block {
  flex-grow: 1;
}

.invisible {
  display: none;
}

.ellipsis:after {
  content: "..."
}
</style>
'''
outfile.write('''<!DOCTYPE html>
<html>
  <head>
    <title>Mastodon Archive</title>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
</head>''')
outfile.write(styleSheet)
outfile.write("</head><body>\
	<section id='header'>\
		<img src='avatar.png'>\
		<div class='m-display-name'>{0}</div>\
		<div>@{1}</div>\
		<div id='actor-summary'>{2}</div>\
	</section><div id='feed'>".format(actor.get("name"), actor.get("preferredUsername"), actor.get("summary")))
for article in articles:
	outfile.write(article)
outfile.write(''' </div>
<script>
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
</script>
</body>
</html>''')
outfile.close()
