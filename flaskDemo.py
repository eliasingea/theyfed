from riotwatcher import RiotWatcher
from flask import Flask, flash, request, render_template, send_from_directory
import time
import collections
from math import ceil
app = Flask(__name__)
app.debug=True
api = RiotWatcher('caa58d75-ee1d-46b9-b3a8-6f540a5d016d')


@app.route('/', methods=['GET','POST'])
def printGame():
	if request.method=='POST':
		
		summoner1 = request.form.get('summoner1')
		summoner2 = request.form.get('summoner2')
		error = False
		if not summoner1 or not summoner2:
			error = True
			return render_template('getIds.html', error = error)
		summ1 = api.get_summoner(name=summoner1)
		summ2 = api.get_summoner(name=summoner2)
		id1 = summ1['id']
		id2 = summ2['id']
		gameId1 = []
		gameId2 = []
		matchList1 = api.get_match_list(id1, ranked_queues="RANKED_SOLO_5x5")
		for matches in matchList1['matches']:
			matchId1 = matches['matchId']
			gameId1.append(matchId1)

		matchList2 = api.get_match_list(id2, ranked_queues="RANKED_SOLO_5x5")
		for matches in matchList2['matches']: 
			matchId2 = matches['matchId']
			gameId2.append(matchId2)
		games = []
		for game in gameId1:
			for game2 in gameId2:
				if game == game2: 
					games.append(game)
		if not games:
			print "we didn't find anything"
			return render_template('results2.html', summoner2=summoner2)
		firstGame = games[0]
		
		# begin = 0
		# end = 15
		# matchIds = getMatchHistory(api, id1, begin, end)
		# for m in matchIds:
		# 	print 'these are the matchIds for the first summoner %d' %m
		# player = getPlayerIds(api, matchIds)
		# compared = comparison(api, id2, matchIds, player)
		# i = 0
		# while compared is False:
		# 	if i == 7:
		# 		print 'we didnt find anything'
		# 		return render_template('results2.html', summoner2=summoner2)
		# 	begin += 15
		# 	end += 15
		# 	#timeOut(api)
		# 	matchId= getMatchHistory(api, id1, begin, end)
		# 	player = getPlayerIds(api, matchId)
		# 	compared = comparison(api, id2, matchId, player)
		# 	i+=1
		# 	print i
		stats, items, champId, summonerName, matchUrl = getStats(api, id1, id2, firstGame, summoner2)
		champName, champStrip = getChampion(api, champId)
		print champId
		return render_template('results.html', stats = stats, items = items, summoner2=summoner2, firstGame=firstGame, id2=id2, champName=champName, champId=champId, champStrip=champStrip)
	return render_template('getIds.html')

def timeOut(RiotWatcher):
	if api.can_make_request() is False:
		time.sleep(10)

def comparison(RiotWatcher, id2, matchIds, player):
	if id2 in player:
	 	print 'you have played with them'
	 	game = player[id2]
	 	
	 	return True, game
	else: 
	 	print 'nope'
	 	return False
def getMatchHistory(RiotWatcher, id1, begin, end):
	matchIds = []
	myHistory = api.get_match_history(id1, begin_index=begin, end_index=end)
	for rankedHistory in myHistory['matches']:
		matchId = rankedHistory['matchId']
		matchIds.append(matchId)
		print matchId

	return matchIds
def getPlayerIds(api, matchIds):
	player = {}
	for match in matchIds: 
		print match
		# if api.can_make_request() is False: 
		#  	time.sleep(5)
		#timeOut(api)
		match1 = api.get_match(match)
	   	for matches in match1['participantIdentities']:
		 	players = matches['player']
		 	playerIds = players['summonerId']
		 	print 'these are the player ids %d' %playerIds
		 	player[playerIds] = match
	return player

def getStats(RiotWatcher, id1, id2, firstGame, summoner2):
	#timeOut(api)
	
	print 'we are about to get the stats for %d' %id2
	summoners = []
	summNames = []
	participants = []
	stats = {}
	items = {}
	match = api.get_match(firstGame)
	participantIdentities = match['participantIdentities']
	for p in participantIdentities:
		player = p['player']
		summonerIds = player['summonerId']
		summoners.append(summonerIds)
		if id2 in summoners:
			participantId = p['participantId']
			participants.append(participantId)
			summonerName = player['summonerName']
			matchUrl = player['matchHistoryUri']
			summNames.append(summonerName)
			print summNames
			
			
	participantStats = match['participants']
	for par in participantStats:
		if participants[0] == par['participantId']:

			champId = par['championId']
			kills = par['stats']['kills']
			deaths = par['stats']['deaths']
			assists = par['stats']['assists']
			championLevel = par['stats']['champLevel']
			winner = par['stats']['winner']
			key = 'stats'
		#stats.setdefault('stats', {})
			stats['kills'] = kills
			stats['deaths'] = deaths
			stats['assists'] = assists
			stats['winner'] = winner
			stats['champLevel'] = championLevel
			kda = (kills + assists) / float(deaths)
			kda = ceil(kda * 100) / 100.0
			stats['KDA'] = kda 
			
			items['item0'] = par['stats']['item0']
			items['item1'] = par['stats']['item1']
			items['item2'] = par['stats']['item2']
			items['item3'] = par['stats']['item3']
			items['item4'] = par['stats']['item4']
			items['item5'] = par['stats']['item5']
			items['item6'] = par['stats']['item6']
		
			print stats
			print items
			print champId
			summonerName = summoner2
			print summonerName
			print matchUrl
			return stats, items, champId, summonerName, matchUrl

def getChampion(RiotWatcher, champId):
	champ = api.static_get_champion(champId)
	champName = champ['name']
	champStrip = champName.replace(" ", "")
	print champName
	print champStrip
	if '.' in champStrip:
		champStrip = champStrip.replace(".", "")
	return champName, champStrip
if __name__ == '__main__':
	app.run()
