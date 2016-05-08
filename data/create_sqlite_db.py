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
	return chart

conn = sqlite3.connect('esc.db')
#conn = sqlite3.connect(':memory:')

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
					print(f, country_from)
					print(row)
					if(country_from not in ['Participant', 'Points', 'Place']):
						points = 0
						if(row[country_from] not in ['','–']):
							points = int(row[country_from])
						
						#fix the problem with Serbia and Montenegro
						if('Serbia and Montenegro' not in (country_from, row['Participant'])):
							cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, country_from, row['Participant'], points))
						if(country_from == 'Serbia and Montenegro'):
							cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, 'Serbia', row['Participant'], points))
							cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, 'Montenegro', row['Participant'], points))
						elif(row['Participant'] == 'Serbia and Montenegro'):
							cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, country_from, 'Serbia', points))
							cur.execute('INSERT INTO points(event, "from", "to", points) VALUES (?,?,?,?)', (event_id, country_from, 'Montenegro', points))


conn.commit()

#SUM
# all
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_all.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 AND event in (SELECT ID FROM events WHERE year < 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "semifinal" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 AND event in (SELECT ID FROM events WHERE year > 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050.json", "w") as file:
	print(json.dumps(chart), file=file)
	
# all - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 AND event IN (SELECT ID FROM events WHERE type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_all_final.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 AND event in (SELECT ID FROM events WHERE year < 2009 AND type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote_final.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury - final only
result = cursor.execute('SELECT "from", "to", sum(points) AS sum FROM points WHERE points.points > 0 AND event in (SELECT ID FROM events WHERE year >= 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050_final.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#AVG
# all
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_all_avg.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points WHERE event in (SELECT ID FROM events WHERE year < 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "semifinal" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote_avg.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points WHERE event in (SELECT ID FROM events WHERE year > 2009 UNION SELECT ID FROM events WHERE year = 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050_avg.json", "w") as file:
	print(json.dumps(chart), file=file)
	
# all - final only
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points WHERE event IN (SELECT ID FROM events WHERE type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_all_final_avg.json", "w") as file:
	print(json.dumps(chart), file=file)

#televoting - final only
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points WHERE event in (SELECT ID FROM events WHERE year < 2009 AND type = "final") GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_televote_final_avg.json", "w") as file:
	print(json.dumps(chart), file=file)
	
#50/50 Televoting / Jury - final only
result = cursor.execute('SELECT "from", "to", avg(points) AS avg FROM points WHERE event in (SELECT ID FROM events WHERE year >= 2009 AND type = "final" ) GROUP BY "to", "from"')
chart = chart_from_result(result)

with open("data_5050_final_avg.json", "w") as file:
	print(json.dumps(chart), file=file)

conn.close()