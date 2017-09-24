import urllib
from bs4 import BeautifulSoup
import numpy as np

action_dict = {
'doubled': [1, 1, 1, 2, 0, 0, 0, 0, 0],
'flied': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'fouled': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'grounded': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'homered': [1, 1, 1, 4, 0, 0, 0, 0, 0],
'lined': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'non-force': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'out': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'sacrificed': [0, 1, 0, 0, 0, 0, 0, 0, 1],
'singled': [1, 1, 1, 1, 0, 0, 0, 0, 0],
'struck': [1, 1, 0, 0, 0, 0, 0, 0, 0],
'tripled': [1, 1, 1, 3, 0, 0, 0, 0, 0],
'walked': [0, 1, 0, 0, 1, 0, 0, 0, 0]
}

reached_dict = {
'on error': [1, 1, 0, 0, 0, 0, 0, 0, 0],
"on fielder's choice": [1, 1, 0, 0, 0, 0, 0, 0, 0],
'on a sacrifice': [0, 1, 0, 0, 0, 0, 0, 0, 1]
}

hit_dict = {
'ground rule double': [1, 1, 1, 2, 0, 0, 0, 0, 0],
'sacrifice fly': [0, 1, 0, 0, 0, 0, 0, 1, 0]
}
was_dict = {
# IBB also counts as a BB
'intentionally walked': [0, 1, 0, 0, 1, 1, 0, 0, 0],
'hit by a pitch': [0, 1, 0, 0, 0, 0, 1, 0, 0],
'forced out': [1, 1, 0, 0, 0, 0, 0, 0, 0]
}	


action_dict_cat = {
'doubled': '2B',
'flied': 'out',
'fouled': 'out',
'grounded': 'out',
'homered': 'HR',
'lined': 'out',
'non-force': 'out',
'out': 'out',
'sacrificed': 'SH',
'singled': '1B',
'struck': 'out',
'tripled': '3B',
'walked': 'BB'
}

reached_dict_cat = {
'on error': 'out',
"on fielder's choice": 'out',
'on a sacrifice': 'SH'
}

hit_dict_cat = {
'ground rule double': '2B',
'sacrifice fly': 'SF'
}

was_dict_cat = {
# IBB also counts as a BB
'intentionally walked': 'IBB',
'hit by a pitch': 'HBP',
'forced out': 'out'
}	
		
		


import csv
def store_ids(filename, firstname, lastname, playerid):
	id_to_name = {}
	
	with open (filename, 'r') as f:
		reader = csv.DictReader(f)
		for row in reader:
			first, last, id = row[firstname], row[lastname], row[playerid]
			id_to_name[id] = (first, last)

	return id_to_name
	

	
def get_vs_urls(last_season):
	'''
	store info on a batter's vs stats
	'''
	exception = ["D'", "O'"] #maybe O' too?
	
	
	base_url = 'http://www.fangraphs.com/players.aspx'
	page = urllib.urlopen(base_url).read()
	soup = BeautifulSoup(page)
	urls = []
	for div in soup.find_all('div', {'class':'s_name'}):
		for a in div.find_all('a'):
			urls.append('https://www.fangraphs.com/' + a['href'])

	vs_urls = []	
	cnt = 0	
	for url in urls:
		print url
		if url[-2:] not in exception: #idk why D' doesn't work...
			page = urllib.urlopen(url).read()
			soup = BeautifulSoup(page)
			players = soup.find_all('div', {'class':'search'})[0]
			rows = players.table.find_all('tr')
			for row in rows:
				year_str = row.find_all('td')[1].string[-4:]
				if year_str.isdigit() and int(year_str) >= last_season:
					href = row.td.a['href']
					name = row.td.a.string
					vs_url = 'https://www.fangraphs.com/statsp.aspx?' + href[href.find('?')+1:]
					print href[href.find('?')+1:]
					vs_urls.append((name, vs_url))
			cnt += 1

	return vs_urls

'''
url = "https://www.fangraphs.com/players.aspx?letter=D'"
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page)
players = soup.find_all('div', {'class':'search'})
'''

#url = 'http://www.fangraphs.com/statsp.aspx?playerid=15676&position=1B&season=2017'
#url = 'http://www.fangraphs.com/statsp.aspx?playerid=8203&position=2B&season=2017'
#url = 'http://www.fangraphs.com/statsp.aspx?playerid=10155&position=OF&season=2017'
#url = 'http://www.fangraphs.com/statsp.aspx?playerid=1101&position=OF&season=2017'

'''
url = 'http://www.fangraphs.com/statsp.aspx?playerid=3174&position=OF&season=2017'
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page, 'lxml')
'''

def get_counts(soup):

	#unique_actions = []
	#unique_actions_full = []
	action_counts = np.zeros(9)

	for tr in soup.tbody.find_all('tr'):
		pitcher_name = tr.find_all('td')[1].a.string
		href = tr.find_all('td')[1].a['href']
		pitcher_id = href[href.find('=')+1:href.find('&')]
		
		full_action = tr.find_all('td')[6].string.split('.')[0]
		log = full_action.split(' ')
		action = log[2]
		
		#print action
		if action in action_dict:
			#print action_dict[action]
			action_counts += action_dict[action]
		elif action == 'was':
			for was_action in was_dict:
				if was_action in full_action:
					#print was_action, 'in', full_action
					action_counts += was_dict[was_action]
		elif action == 'hit':
			for hit_action in hit_dict:
				if hit_action in full_action:
					#print hit_action, 'in', full_action
					action_counts += hit_dict[hit_action]			
		elif action == 'reached':
			for reached_action in reached_dict:
				if reached_action in full_action:
					#print hit_action, 'in', full_action
					action_counts += reached_dict[reached_action]			
		else:
			#print action, 'is nowhere'
			print '@@@', full_action
		#unique_actions_full.append(log)

		#print pitcher_id, pitcher_name
	
	avg = action_counts[2] / action_counts[0]
	obp = (action_counts[2] + action_counts[4] + action_counts[6]) / (action_counts[0] + action_counts[4] + action_counts[6] + action_counts[7])
	slg = action_counts[3] / action_counts[0]

	print 'avg:', round(avg, 3)
	print 'obp:', round(obp, 3)
	print 'slg:', round(slg, 3)
	
	return action_counts
	

	
def get_counts_per_pitcher(soup):
	
	total_dict = {}


	for tr in soup.tbody.find_all('tr'):
		pitcher_name = tr.find_all('td')[1].a.string
		href = tr.find_all('td')[1].a['href']
		pitcher_id = href[href.find('=')+1:href.find('&')]
		
		id = (pitcher_name, pitcher_id) 
		if id not in total_dict:
			total_dict[id] = np.zeros(9)
		
		full_action = tr.find_all('td')[6].string.split('.')[0]
		log = full_action.split(' ')
		action = log[2]
		
		#print action
		if action in action_dict:
			#print action_dict[action]
			total_dict[id] += action_dict[action]
		elif action == 'was':
			for was_action in was_dict:
				if was_action in full_action:
					#print was_action, 'in', full_action
					total_dict[id] += was_dict[was_action]
		elif action == 'hit':
			for hit_action in hit_dict:
				if hit_action in full_action:
					#print hit_action, 'in', full_action
					total_dict[id] += hit_dict[hit_action]			
		elif action == 'reached':
			for reached_action in reached_dict:
				if reached_action in full_action:
					#print hit_action, 'in', full_action
					total_dict[id] += reached_dict[reached_action]			
		else:
			print '@@@', full_action


	slashlines = {}
	
	for id, action_counts in total_dict.items():
		avg = action_counts[2] / action_counts[0]
		obp = (action_counts[2] + action_counts[4] + action_counts[6]) / (action_counts[0] + action_counts[4] + action_counts[6] + action_counts[7])
		slg = action_counts[3] / action_counts[0]
		
		slashlines[id] = (avg, obp, slg)
			
			
			
	return slashlines
	

	
def get_counts_per_pitcher(db, tablename):
	total_dict = {}

	for tr in soup.tbody.find_all('tr'):
		pitcher_name = tr.find_all('td')[1].a.string
		href = tr.find_all('td')[1].a['href']
		pitcher_id = href[href.find('=')+1:href.find('&')]
		
		id = (pitcher_name, pitcher_id) 
		if id not in total_dict:
			total_dict[id] = np.zeros(9)
		
		full_action = tr.find_all('td')[6].string.split('.')[0]
		log = full_action.split(' ')
		action = log[2]
		
		#print action
		if action in action_dict:
			#print action_dict[action]
			total_dict[id] += action_dict[action]
		elif action == 'was':
			for was_action in was_dict:
				if was_action in full_action:
					#print was_action, 'in', full_action
					total_dict[id] += was_dict[was_action]
		elif action == 'hit':
			for hit_action in hit_dict:
				if hit_action in full_action:
					#print hit_action, 'in', full_action
					total_dict[id] += hit_dict[hit_action]			
		elif action == 'reached':
			for reached_action in reached_dict:
				if reached_action in full_action:
					#print hit_action, 'in', full_action
					total_dict[id] += reached_dict[reached_action]			
		else:
			print '@@@', full_action


	slashlines = {}
	
	for id, action_counts in total_dict.items():
		avg = action_counts[2] / action_counts[0]
		obp = (action_counts[2] + action_counts[4] + action_counts[6]) / (action_counts[0] + action_counts[4] + action_counts[6] + action_counts[7])
		slg = action_counts[3] / action_counts[0]
		
		slashlines[id] = (avg, obp, slg)
			
	return slashlines	
	
import sqlite3
from prettytable import PrettyTable

'''
url = 'http://www.fangraphs.com/statsp.aspx?playerid=3174&position=OF&season=2016'
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page, 'lxml')
create_table(db, 'Choo_16', soup, 3174, '2016')
compare_with_total(db, 'Choo_16')
''' #(76, 70)
'''
url = 'http://www.fangraphs.com/statsp.aspx?playerid=4949&position=OF&season=2016'
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page, 'lxml')
create_table(db, 'Stanton_16', soup, 4949, '2016')
compare_with_total(db, 'Stanton_16')
''' #(196, 182)
'''
url = 'http://www.fangraphs.com/statsp.aspx?playerid=5038&position=3B&season=2016'
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page, 'lxml')
create_table(db, 'Donaldson_16', soup, 5038, '2016')
compare_with_total(db, 'Donaldson_16')
''' #(316, 268)
''' 
url = 'http://www.fangraphs.com/statsp.aspx?playerid=4972&position=P&season=2016'
page = urllib.urlopen(url).read()
soup = BeautifulSoup(page, 'lxml')
create_table(db, 'Hamels_16', soup, 4972, '2016')
''' # checking if create_table would also work for pitchers


'''
import time
import urllib2
from bs4 import SoupStrainer
start = time.time()
url = "http://www.fangraphs.com/statsp.aspx?playerid=4972&position=P&season=2016"
page = urllib2.urlopen(url).read()
print time.time() - start
links = SoupStrainer("tbody")
soup = BeautifulSoup(page, "lxml", parse_only=links)
print time.time() - start
#create_table(db, 'Hamels_16', soup, 4972, '2016')
'''

'''
table = []
for row in response.css("tr.rgRow"):
	rowl = []
	for td in row.css('td::text'):
		rowl.append(str(td.extract()))
	table.append(rowl)

import csv
with open('Hamels_16.csv', 'wb') as f:
	writer = csv.writer(f)
	for rowl in table:
		writer.writerow(rowl)
'''
	
	
def drop_table(db, tablename):
	query = '''drop table ''' + tablename
	db.execute(query)


def create_table(db, tablename, soup, batter_id, year, for_pitcher=False):
	cursor = db.cursor()
	if for_pitcher:
		cursor.executescript('create table ' + tablename + ' (id number, date string, pname text, bname text, cat text, AB number, PA number, H number, SLGC number, BB number, IBB number, HBP number, SF number, SH number)')
	else:
		cursor.executescript('create table ' + tablename + ' (id number, date string, bname text, pname text, cat text, AB number, PA number, H number, SLGC number, BB number, IBB number, HBP number, SF number, SH number)')

	batter_name = str(soup.strong.string) # string to remove unicode sign
	id = 0
	
	cnt = 0
	
	for tr in soup.tbody.find_all('tr'):
		cnt += 1
		if cnt % 100 == 0:
			print 'working on row', cnt
		
		pitcher_name = str(tr.find_all('td')[1].a.string)
		href = tr.find_all('td')[1].a['href']
		pitcher_id = href[href.find('=')+1:href.find('&')]	
		
		md = tr.find('td').a.string.split('/')
		month, date = md[0], md[1]
		if len(month) == 1:
			month = '0' + month
		if len(date) == 1:
			date = '0' + date
		date_str = str(year + '-' + month + '-' + date)
		
		full_action = tr.find_all('td')[6].string
		log = full_action.split(' ')
		print log
		action = log[2]
		
		stat_row = ()
		
		include = True
		cat = ''
		
		if action in action_dict:
			stat_row = action_dict[action]
			cat = action_dict_cat[action]
		elif action == 'was':
			for was_action in was_dict:
				if was_action in full_action:
					stat_row = was_dict[was_action]
					cat = was_dict_cat[was_action]
				else:
					stat_row = [0] * 9
					include = False   # need to ignore 'was caught stealing'
		elif action == 'hit':
			for hit_action in hit_dict:
				if hit_action in full_action:
					stat_row = hit_dict[hit_action]	
					cat = hit_dict_cat[hit_action]
		elif action == 'reached':
			for reached_action in reached_dict:
				if reached_action in full_action:
					stat_row = reached_dict[reached_action]	
					cat = reached_dict_cat[reached_action]
		else:
			print '@@@', full_action
			stat_row = [0] * 9
			include = False
		
		#print pitcher_name
		#print full_action
		
		if include and len(stat_row) == 9: # Stanton_16 showed a stat_row that is empty.. need to check why
			id += 1
			stat_row = tuple(stat_row)
			total_row = str((id, date_str, batter_name + '_' + str(batter_id), pitcher_name + '_' + str(pitcher_id), cat) + stat_row)
			#print total_row
			statement = 'INSERT INTO ' + tablename + ' values ' + total_row
			#print '|' + statement + '|' 
			cursor.executescript(statement)
			
from os import listdir
def create_tables(db, dirname):
	files = [f for f in listdir(dirname)]
	
	for file in files:
		tablename = file[:-4]
		
		print 'will create table', tablename
		create_table_from_csv(db, tablename, dirname+'/'+file)

			
def create_table_from_csv(db, tablename, csvfile):
	cursor = db.cursor()
	#print "create table " + tablename + " (id number, date string, playername text, vsname text, cat text, AB number, PA number, H number, SLGC number, BB number, IBB number, HBP number, SF number, SH number)"
	query = ''.join(["create table ", tablename, " (id number, date string, playername text, vsname text, cat text, AB number, PA number, H number, SLGC number, BB number, IBB number, HBP number, SF number, SH number)"])
	
	#print query
	cursor.executescript(query)

	id = 0
	cnt = 0
	
	with open(csvfile, 'rb') as f:
		reader = csv.DictReader(f)
		
		for row in reader:
			cnt += 1
			if cnt % 100 == 0:
				print 'working on row', cnt
			playername, playerid, vsname, vsid, date_str, full_action = row['playername'].replace('.', '').replace("'", ''), row['playerid'].replace('&', ''), \
																		row['vsname'].replace('.', '').replace("'", ''), row['vsid'].replace('&', ''), \
																		row['date'], row['Play']
			vsname = '_'.join(vsname.split(' '))

			log = full_action.split(' ')
			#print log
			action = log[2]
			
			stat_row = ()
			
			include = True
			cat = ''
			
			if action in action_dict:
				stat_row = action_dict[action]
				cat = action_dict_cat[action]
			elif action == 'was':
				for was_action in was_dict:
					if was_action in full_action:
						stat_row = was_dict[was_action]
						cat = was_dict_cat[was_action]
					else:
						stat_row = [0] * 9
						include = False   # need to ignore 'was caught stealing'
			elif action == 'hit':
				for hit_action in hit_dict:
					if hit_action in full_action:
						stat_row = hit_dict[hit_action]	
						cat = hit_dict_cat[hit_action]
			elif action == 'reached':
				for reached_action in reached_dict:
					if reached_action in full_action:
						stat_row = reached_dict[reached_action]	
						cat = reached_dict_cat[reached_action]
			else:
				#print '@@@', full_action
				stat_row = [0] * 9
				include = False
			
			#print pitcher_name
			#print full_action
			
			if include and len(stat_row) == 9: # Stanton_16 showed a stat_row that is empty.. need to check why
				id += 1
				stat_row = tuple(stat_row)
				total_row = str((id, date_str, playername + '_' + playerid, vsname + '_' + vsid, cat) + stat_row)
				#print total_row
				statement = 'INSERT INTO ' + tablename + ' values ' + total_row
				#print '|' + statement + '|' 
				cursor.executescript(statement)

			
			
def compare_with_total(db, tablename):
	query = 'SELECT DISTINCT vsname, id FROM ' + tablename
	print query 
	cursor = db.cursor()
	cursor.execute(query)
	pitchers = cursor.fetchall()
	
	base_query = '''select sum(H) * 1.0 / sum(AB) as avg, sum(H) as H, sum(AB) as AB from x
				where  not ( date = (select max(date) from x)
					and id = (select max(id) from x where date = (select max(date) from x) ) )
				order by date'''	

	base_query_neg = '''select H from x
				where ( date = (select max(date) from x)
					and id = (select max(id) from x where date = (select max(date) from x) ) )
				order by date'''	
	
	
	total_query = "select sum(H) * 1.0 / sum(AB) as avg, sum(H) as H, sum(AB) as AB from " + tablename
	cursor.execute(total_query)
	total_result = cursor.fetchall()
	
	total_avg = total_result[0][0]
	
	total_score = 0
	vs_score = 0
	
	
	cnt = 0
	for pitcher_tup in pitchers:
		cnt += 1
		
		pitcher_name = pitcher_tup[0]
		#print cnt, pitcher_name
		addition = '''with x as (select * from ''' + tablename + ''' where vsname = "''' + str(pitcher_name) + '''")'''
		
		query = addition + '\n' + base_query
		
		cursor.execute(query)
		result = cursor.fetchall()
		vs_avg = result[0][0]
		
		neg_query = addition + '\n' + base_query_neg
		cursor.execute(neg_query)
		hit = cursor.fetchall()[0][0]
		
		#print 'results', total_avg, vs_avg, hit
		
		if vs_avg != None:
			if hit:
				if total_avg >= vs_avg:
					total_score += 1
					#print 'total won'
				else:
					vs_score += 1
					#print 'vs won'
			else:
				if total_avg >= vs_avg:
					vs_score += 1
					#print 'vs won'
				else:
					total_score += 1
					#print 'total won'			

	return total_score, vs_score			
			


'''
SQL functions
'''			
def print_select(db, statement, verbose=True):
	cursor = db.cursor()
	cursor.execute(statement)
	
	if cursor.description != None:
	
		names = [desc[0] for desc in cursor.description]
		rows = cursor.fetchall()
		
		x = PrettyTable(names)
		for row in rows:
			x.add_row(row)
		if verbose:
			print x
	
		return rows
	else:
		return []

	
	
	
	
def table(db, tablename, limit=0):
	query = "select * from " + tablename
	if limit != 0:
		query += ' limit ' + str(limit)
    
	print_select(db, query)
	return 'success'


	
'''
code for similarity indices
'''

from sklearn.metrics.pairwise import cosine_similarity as cos_sim
from sklearn.metrics.pairwise import euclidean_distances as euclid
import numpy as np
import math 

def batters_for_pitcher(db, ptable, year_str):
	'''
	return a list of all batters who faced a single pitcher
	'''
	query = "SELECT DISTINCT vsname FROM " + ptable
	cursor = db.cursor()
	cursor.execute(query)
	blist = cursor.fetchall()
	
	filelist = []
	for btup in blist:
		bname = btup[0]
		splitted = bname.split('_')

		
		if len(splitted) == 3:
			filename = '_'.join([splitted[0], splitted[1], year_str, splitted[2]]).replace('.', '') + '.csv'
		else:
			filename = '_'.join([splitted[0], splitted[1], splitted[2], year_str, splitted[3]]).replace('.', '') + '.csv'

		filelist.append(filename)
	return filelist
	

def get_sim(rows):
	newrows = []
	for row in rows:
		newrows.append(row[0])
	
	newrows = map(lambda x: int(x)**2, newrows)
	
	return 1 - math.sqrt(sum(newrows)) / math.sqrt(len(newrows))


BASE_QUERY = '''
with vs as (
select xpname, xvsname, ypname, yvsname, xAVG, yAVG
    from (select playername as xpname, vsname as xvsname, sum(H) as xH, sum(AB) as xAB,
		sum(H) * 1.0 / sum(AB) as xAVG
            from XBATTER
            group by vsname ) as x
    join (select playername as ypname, vsname as yvsname, sum(H) as yH, sum(AB) as yAB,
		sum(H) * 1.0 / sum(AB) as yAVG
            from YBATTER
            group by vsname ) as y
        on x.xvsname = y.yvsname 
)

select vs.xAVG - vs.yAVG as diff
	from vs
	where vs.xAVG is not null
		and vs.yAVG is not null
'''



def get_sim_list(db, filelist, base_batter):
	# base_batter is a filename already in filelist
	
	# first, create table if it doesn't exist in the db already
	
	rows = print_select(db, '''select name from sqlite_master''', verbose=False)
	tables = map(lambda x: x[0], rows)
	
	for file in filelist:
		tablename = file[:-4].replace("'", "") # O'Malley -> OMalley
		tablename = tablename.replace(".", "") # Almora
		
		if tablename not in tables:
			print file, tablename
			create_table_from_csv(db, tablename, 'data/'+file)
	
	print base_batter
	# remove base_batter
	#filelist.remove(base_batter) -> why do we get an error?
	# convert from filename to tablename
	base_batter = base_batter[:-4]	
	
	
	results = []
	
	# then, run the extension of the BASE_QUERY
	for file in filelist:
		tablename = file[:-4].replace("'", "")

		query = BASE_QUERY.replace('XBATTER', base_batter)
		query = query.replace('YBATTER', tablename)
		#print query
		
		rows = print_select(db, query, verbose=False)
		
		if len(rows) > 10:
			#print base_batter, tablename, get_sim(rows), len(rows)
			results.append((get_sim(rows), base_batter, tablename))
		#else: 
		#	print base_batter, tablename, '<10 rows returned'
	
	return results
	
VS_QUERY = '''
select playername, vsname, sum(AB) as AB,
		sum(H) * 1.0 / sum(AB) as AVG
            from PITCHER
	where vsname = 'BATTER'      
group by vsname
'''	

	
def estimate_vs(db, results, pitcher, N):
	results.sort()
	results.reverse()
	
	top_res = results[1:N+1]  # excluding oneself
	
	
	total_avg = 0
	
	valid_cnt = 0
	
	for res_tup in top_res:
		query = VS_QUERY.replace('PITCHER', pitcher)
		query = query.replace('BATTER', res_tup[-1].replace('2016_', ''))
		#print query
		
		rows = print_select(db, query, verbose=False)
		#print rows[0], res_tup[0], rows[0][-1]*res_tup[0]
		
		#print rows
		# sometimes pitcher vs. other batter may produce None AVG
		ab, avg = rows[0][-2], rows[0][-1] 
		
		#print pitcher, res_tup[-1].replace('2016_', ''), ab, avg
		
		if ab >= 3:
			total_avg += avg*res_tup[0]
			valid_cnt += 1
	print 'estimate:', total_avg / valid_cnt, 'with', valid_cnt, 'batters'
	
	
	return avg / valid_cnt
	#sim_sum = sum(map(lambda x: x[0], top_res))
	#sim_sum_abs = sum(map(lambda x: abs(x[0]), top_res))
	#print sim_sum, sim_sum_abs
	
def get_vs_final(db, ptable, bfile, year_str, N):
	filelist = batters_for_pitcher(db, ptable, year_str)
	results = get_sim_list(db, filelist, bfile)
	if len(results) < N:
		print N, 'is more than results'
		return -1, -1
	
	estimate = estimate_vs(db, results, ptable, N)
	
	query = VS_QUERY.replace('PITCHER', ptable)
	query = query.replace('BATTER', bfile[:-4].replace('2016_', ''))	
	rows = print_select(db, query, verbose=False)
	actual = rows[0][-1]
	print 'actual:', actual

	return actual, estimate
	
def get_vs_final_for_all(db, ptable, year_str, N):
	'''
	for all batters who faced ptable,
	returns the actual vs_avg and the estimated vs_avg using at most N similarities
	'''
	bfilelist = batters_for_pitcher(db, ptable, year_str)
	actuals = []
	estimates = []
	for bfile in bfilelist:
		actual, estimate = get_vs_final(db, ptable, bfile, year_str, N)
		if actual != -1:
			actuals.append(actual)
			estimates.append(estimate)

	return actuals, estimates
	
	
	
def get_url_dict(vs_urls):
	url_dict = {}
	
	for url_tup in vs_urls:
		name, url = url_tup[0], url_tup[1]
		splitted = name.split(' ')
		newname = splitted[0][0] + ' ' + splitted[1]
		
		id = url[url.find("id=")+3:url.find("id=")+7]
		
		sql_id = newname + '_' + id
		
		url_dict[sql_id] = url
	return url_dict
	


	
print 'success'