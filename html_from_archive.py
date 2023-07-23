#!/usr/bin/env python3
import json
from os import path
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
			article = "<img src='profile.png'>\
			<article class='status'>\
			<div class='status__date'><span>{0}</span></div>\
			<details><summary class='status__summary'>{1}</summary>\
			<div class='status__content'>{2}</div>\
			<div class='status__media'>{3}</div>\
			</details>\
			</article>".format(date, summary, htmlContent, images)
		else:
			article = "<article class='status'>\
			<div class='status__date'><span >{0}</span></div>\
			<div class='status__content'>{1}</div>\
			<div class='status__media'>{2}</div>\
			</article>".format(date, htmlContent, images)
		articles.append(article)

outfile = open("processed_archive.html", "w")
styleSheet = "<style>\
.status { width: 54ch; position: relative; min-height: 128px; margin:auto auto 4em auto; border: 1px solid #999; border-radius: 16px; padding:8px; background: rgba(0,0,0,0.75);}\
.status::before{ content: url('avatar.png'); position: absolute; right: 100%; }\
.status__summary { width: 100%; background: #333 }\
.status__summary::after {content: '[Click to Open]';display: block;}\
.status__date { text-align: right; }\
.status__content { }\
.status__media { width:100%; }\
.status__image { max-width: 100%; width:100%; min-width:100%; }\
#header {background: rgba(0,0,0,0.75);text-align: center;padding-bottom: 16px;}\
body { margin:0;background:#333; background-image: url('header.png'); background-size: cover; background-attachment: fixed; color: #fff1e8; line-height: 1.4;}\
* {box-sizing: border-box;}\
a { color: rgb(150,255,140) }\
</style>"
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
	</section>".format(actor.get("preferredUsername"), actor.get("name"), actor.get("summary")))
for article in articles:
	outfile.write(article)
outfile.write("</body></html>")
outfile.close()
