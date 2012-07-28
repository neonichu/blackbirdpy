#!/usr/bin/env python

import blackbirdpy
import json
import sys
import urllib2

LINE_SEP = '********************'

# TODO: Should cross-check 'user_id' for all tweets

def format_tweet(dummy_tweet, actual_tweet):
	tweet_created_datetime = blackbirdpy.timestamp_string_to_datetime(actual_tweet['created_at'])
	tweet_easy_timestamp = blackbirdpy.easy_to_read_timestamp_string(tweet_created_datetime)

	html = blackbirdpy.TWEET_EMBED_HTML.format(
		id=actual_tweet['status_id'],
		tweetURL='https://twitter.com/NeoNacho/status/%s' % actual_tweet['status_id'],
		screenName=dummy_tweet['user']['screen_name'],
		realName=dummy_tweet['user']['name'],
		tweetText=actual_tweet['text'].decode('utf-8'),
		source=actual_tweet['created_via'], # TODO: Should be href to client
		profilePic=dummy_tweet['user']['profile_image_url'],
		profileBackgroundColor=dummy_tweet['user']['profile_background_color'],
		profileBackgroundImage=dummy_tweet['user']['profile_background_image_url'],
		profileTextColor=dummy_tweet['user']['profile_text_color'],
		profileLinkColor=dummy_tweet['user']['profile_link_color'],
		timeStamp=actual_tweet['created_at'],
		easyTimeStamp=tweet_easy_timestamp,
		utcOffset=dummy_tweet['user']['utc_offset'], # TODO: This should be from the actual tweet
		bbpBoxCss='',
	)
	
	return html

def tweet_for_id(tweet_id):
	api_url = 'http://api.twitter.com/1/statuses/show.json?include_entities=true&id=' + tweet_id
	api_handle = urllib2.urlopen(api_url)
	api_data = api_handle.read()
	api_handle.close()
	return json.loads(api_data)

def tweets_from_file(filename):
	current_status = {}
	first = True
	in_text = False
	tweets = []

	for line in open(filename, 'r'):
		if line.startswith('//'):
			continue

		if line[:-1] == LINE_SEP:
			if first:
				first = False
				continue

			in_text = False

			tweets.append(current_status)
			current_status = {}
			continue

		if first:
			continue

		if in_text:
			line = line[:-1]
			current_status['text'] += line
			continue

		if ': ' in line:
			key = line.split(':')[0]
			in_text = key == 'text'
			current_status[key] = ':'.join(line.split(':')[1:])[1:-1]

	return tweets


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'Please specify your *-tweets.txt file.'
		sys.exit(1)

	tweets = tweets_from_file(sys.argv[1])
	dummy_tweet = tweet_for_id(tweets[0]['status_id'])

	print """<!DOCTYPE html>
<html>
<head>
	<script src="styleTweets.js" type="text/javascript"></script>
	<link href="tweet.css" rel="stylesheet" type="text/css" />
	<meta charset="utf-8" />
	<title>All tweets by %s</title>
</head>
<body>
""" % dummy_tweet['user']['screen_name']

	for tweet in tweets:
		print format_tweet(dummy_tweet, tweet).encode('utf-8')

	print """</body>
</html>"""
