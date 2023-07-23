#!/usr/bin/env python3
import json
from os import path
import datetime

# SHORT DATE

SECOND_LENGTH = 1
MINUTE_LENGTH = 60
HOUR_LENGTH = MINUTE_LENGTH * 60
DAY_LENGTH = HOUR_LENGTH * 24
WEEK_LENGTH = DAY_LENGTH * 7
YEAR_LENGTH = DAY_LENGTH * 365

def ShortDate(date: str):
	now = datetime.datetime.now()
	then = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

	diff = int((now - then).total_seconds())

	if diff >= YEAR_LENGTH:
		return str(diff // YEAR_LENGTH) + "y"
	if diff >= WEEK_LENGTH:
		return str(diff // WEEK_LENGTH) + "w"
	if diff >= DAY_LENGTH:
		return str(diff // DAY_LENGTH) + "d"
	if diff >= HOUR_LENGTH:
		return str(diff // HOUR_LENGTH) + "h"
	if diff >= MINUTE_LENGTH:
		return str(diff // MINUTE_LENGTH) + "m"
	return str(diff) + "s"

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
		attachments = [attachment.get("url") for attachment in status.get("attachment")]
		images = ""
		for imageURL in attachments:
			# only runs the loop for the first media url in the archive
			if pathOffset == 1:
				while not path.exists(imageURL[pathOffset:]) and pathOffset < len(imageURL):
					pathOffset +=1

			if imageURL[-4:] == ".mp4" or imageURL[-5:] == ".webm":
				images += "<video controls muted src='{0}' class='status__image'>There should be a video here.</video>".format(imageURL[pathOffset:])
			else:
				images += "<img class='status__image' src='{0}'>".format(imageURL[pathOffset:])
		if summary:
			article = '''<div class="m-post">
	<div class="m-post-header">
		<img src="avatar.png" class="m-pfp">
		<div class="m-user-block">
			<div class="m-display-name">{4}</div>
			<div class="m-user-name">@{5}</div>
		</div>
		<span class="m-permalink" title={6}>{0}</span>
	</div>
	<details>
		<summary>{1}</summary>
		<div class="m-post-body">{2}</div>
		<div class="m-media">{3}</div>
	</details>
</div>'''.format(ShortDate(date), summary, htmlContent, images, actor.get("name"), actor.get("preferredUsername"), date)
		else:
			article = '''<div class="m-post">
	<div class="m-post-header">
		<img src="avatar.png" class="m-pfp">
		<div class="m-user-block">
			<div class="m-display-name">{3}</div>
			<div class="m-user-name">@{4}</div>
		</div>
		<span class="m-permalink" title={5}>{0}</span>
	</div>
	<div class="m-post-body">{1}</div>
	<div class="m-media">{2}</div>
</div>'''.format(ShortDate(date), htmlContent, images, actor.get("name"), actor.get("preferredUsername"), date)
		articles.append(article)

outfile = open("processed_archive.html", "w")
styleSheet = '''<style>
#feed {
  margin: 0 30% 0;
}

.m-media > * {
  width: 100%;
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
</style>
'''
outfile.write("<!DOCTYPE html><html>\
	<head>\
	<title>Mastodon Archive</title>\
	<meta charset='UTF-8'>\
	<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
outfile.write(styleSheet)
outfile.write("</head><body>\
	<section id='header'>\
		<img src='avatar.png'>\
		<div id=preferred-name>{0}</div>\
		<a id=user-name>{1}</a>\
		<div id='actor-summary'>{2}</div>\
	</section><div id='feed'>".format(actor.get("preferredUsername"), actor.get("name"), actor.get("summary")))
for article in articles:
	outfile.write(article)
outfile.write("</div></body></html>")
outfile.close()
