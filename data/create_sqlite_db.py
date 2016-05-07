#! /usr/bin/env python3

import sqlite3
import os
import csv
import json

def charts_from_result(result):
	chart_from = {}
	chart_to = {}
	for row in result:
		country_from = row[0]
		country_to = row[1]
		if(country_from not in chart_from):
			chart_from[country_from] = {}
		if(country_to not in chart_to):
			chart_to[country_to] = {}
			
		chart_from[country_from][country_to] = row[2]
		chart_to[country_to][country_from] = row[2]

	#fix the problem with Serbia and Montenegro
	if('Serbia and Montenegro' in chart_to):
		for country in chart_to['Serbia and Montenegro']:
			if(country not in chart_to['Serbia']):
				chart_to['Serbia'][country] = 0
			if(country not in chart_to['Montenegro']):
				chart_to['Montenegro'][country] = 0
				
			chart_to['Serbia'][country] += chart_to['Serbia and Montenegro'][country]
			chart_to['Montenegro'][country] += chart_to['Serbia and Montenegro'][country]
		del chart_to['Serbia and Montenegro']
	
	if('Serbia and Montenegro' in chart_from):
		for country in chart_from['Serbia and Montenegro']:
			if(country not in chart_from['Serbia']):
				chart_from['Serbia'][country] = 0
			if(country not in chart_from['Montenegro']):
				chart_from['Montenegro'][country] = 0
				
			chart_from['Serbia'][country] += chart_from['Serbia and Montenegro'][country]
			chart_from['Montenegro'][country] += chart_from['Serbia and Montenegro'][country]
		del chart_from['Serbia and Montenegro']

	for country in chart_to:
		if('Serbia and Montenegro' in chart_to[country]):
			if('Serbia' not in chart_to[country]):
				chart_to[country]['Serbia'] = 0
			if('Montenegro' not in chart_to[country]):
				chart_to[country]['Montenegro'] = 0
			
			chart_to[country]['Serbia'] += chart_to[country]['Serbia and Montenegro']
			chart_to[country]['Montenegro'] += chart_to[country]['Serbia and Montenegro']
			del chart_to[country]['Serbia and Montenegro']
			
	for country in chart_from:
		if('Serbia and Montenegro' in chart_from[country]):
			if('Serbia' not in chart_from[country]):
				chart_from[country]['Serbia'] = 0
			if('Montenegro' not in chart_from[country]):
				chart_from[country]['Montenegro'] = 0
			
			chart_from[country]['Serbia'] += chart_from[country]['Serbia and Montenegro']
			chart_from[country]['Montenegro'] += chart_from[country]['Serbia and Montenegro']
			del chart_from[country]['Serbia and Montenegro']
	return (chart_from, chart_to)

#conn = sqlite3.connect('esc.db')
conn = sqlite3.connect(':memory:')

cursor = conn.cursor()
cursor.execute('CREATE TABLE events (ID INTEGER PRIMARY KEY, year INTEGER, name STRING, type TEXT)')
cursor.execute('CREATE TABLE points (ID INTEGER PRIMARY KEY, event INTEGER, "from" TEXT, "to" TEXT, points INTEGER, FOREIGN KEY(event) REFERENCES events(ID))')

for f in os.listdir(os.getcwd()):
	if(f.endswith('.csv')):
		items = f[:-4].split('-')
		year = int(items[0])
		eventtype = items[1]
		eventname = f[:-4]
		cur = conn.cursor()
		cur.execute('INSERT INTO events(year, name, type) VALUES(?,?,?)', (year, eventname, eventtype))
		event_id = cur.lastrowid
		with open(f) as csvfile:
			reader = csv.DictReader(csvfile, delimiter="\t")
			#insert event
			# get event id
			for row in reader:
				for country_from in row:
					if(country_from not in ['To', 'Total Score'] and row[country_from] not in ['','–']):
						cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, country_from, row['To'], int(row[country_from])))

conn.commit()

# all
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points GROUP BY "to", "from"')
chart_from, chart_to = charts_from_result(result)

with open("data_all_from.json", "w") as file_from, open("data_all_to.json", "w") as file_to:
	print(json.dumps(chart_from), file=file_from)
	print(json.dumps(chart_to), file=file_to)

#televoting
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year < 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "semifinal" ) GROUP BY "to", "from"')
chart_from, chart_to = charts_from_result(result)

with open("data_televote_from.json", "w") as file_from, open("data_televote_to.json", "w") as file_to:
	print(json.dumps(chart_from), file=file_from)
	print(json.dumps(chart_to), file=file_to)
	
#50/50 Televoting / Jury
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year > 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "final" ) GROUP BY "to", "from"')
chart_from, chart_to = charts_from_result(result)

with open("data_5050_from.json", "w") as file_from, open("data_5050_to.json", "w") as file_to:
	print(json.dumps(chart_from), file=file_from)
	print(json.dumps(chart_to), file=file_to)

conn.close()