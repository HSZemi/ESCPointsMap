#! /usr/bin/env python3

import sqlite3
import os
import csv
import json

def chart_from_result(result):
	chart = {}
	for row in result:
		country_from = row[0]
		country_to = row[1]
		if(country_from not in chart):
			chart[country_from] = {}
			
		chart[country_from][country_to] = row[2]

	#fix the problem with Serbia and Montenegro
	
	if('Serbia and Montenegro' in chart):
		for country in chart['Serbia and Montenegro']:
			if(country not in chart['Serbia']):
				chart['Serbia'][country] = 0
			if(country not in chart['Montenegro']):
				chart['Montenegro'][country] = 0
				
			chart['Serbia'][country] += chart['Serbia and Montenegro'][country]
			chart['Montenegro'][country] += chart['Serbia and Montenegro'][country]
		del chart['Serbia and Montenegro']

	for country in chart:
		if('Serbia and Montenegro' in chart[country]):
			if('Serbia' not in chart[country]):
				chart[country]['Serbia'] = 0
			if('Montenegro' not in chart[country]):
				chart[country]['Montenegro'] = 0
			
			chart[country]['Serbia'] += chart[country]['Serbia and Montenegro']
			chart[country]['Montenegro'] += chart[country]['Serbia and Montenegro']
			del chart[country]['Serbia and Montenegro']
	return chart

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
chart = chart_from_result(result)

with open("data_all.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year < 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "semifinal" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year > 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050.json", "w") as file:
	print(json.dumps(chart), file=file)
	
# all - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event IN (SELECT ID FROM events WHERE type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_all_final.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year < 2009 AND type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote_final.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE event in (SELECT ID FROM events WHERE year >= 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050_final.json", "w") as file:
	print(json.dumps(chart), file=file)

conn.close()