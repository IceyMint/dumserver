from functions import addToScheduler
from functions import getFreeKey
from copy import deepcopy
import time

'''
Command function template:

def commandname(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	print("I'm in!")
'''

def sendCommandError(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	mud.send_message(id, 'Unknown command!')

def help(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	mud.send_message(id, 'Commands:')
	mud.send_message(id, '  say <message>	- Says something out loud, '  + "e.g. 'say Hello'")
	mud.send_message(id, '  look			 - Examines the ' + "surroundings, e.g. 'look'")
	mud.send_message(id, '  go <exit>		- Moves through the exit ' + "specified, e.g. 'go outside'")
	mud.send_message(id, '  attack <target>  - attack target ' + "specified, e.g. 'attack cleaning bot'")
	mud.send_message(id, '  check inventory  - check the contents of ' + "your inventory")
	mud.send_message(id, '  take <item>	  - pick up an item lying ' + "on the floor")
	mud.send_message(id, '  drop <item>	  - drop an item from your inventory ' + "on the floor")

def say(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
			if players[id]['canSay'] == 1:
				# go through every player in the game
				for (pid, pl) in list(players.items()):
					# if they're in the same room as the player
					if players[pid]['room'] == players[id]['room']:
						# send them a message telling them what the player said
						mud.send_message(pid, '<f32>{}<r> says: <f159>{}'.format(players[id]['name'], params))
			else:
				mud.send_message(id, 'To your horror, you realise you somehow cannot force yourself to utter a single word!')

def look(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	if players[id]['canLook'] == 1:
		if len(params) < 1:
			# If no arguments are given, then look around and describe surroundings
	
			# store the player's current room
			rm = rooms[players[id]['room']]
	
			# send the player back the description of their current room
			mud.send_message(id, "<f42>" + rm['description'])
	
			playershere = []
			
			itemshere = []
	
			# go through every player in the game
			for (pid, pl) in list(players.items()):
				# if they're in the same room as the player
				if players[pid]['room'] == players[id]['room']:
					# ... and they have a name to be shown
					if players[pid]['name'] is not None and players[pid]['name'] is not players[id]['name']:
						# add their name to the list
						if players[pid]['prefix'] == "None":
							playershere.append(players[pid]['name'])
						else:
							playershere.append("[" + players[pid]['prefix'] + "] " + players[pid]['name'])
	
			##### Show corpses in the room
			for (corpse, pl) in list(corpses.items()):
				if corpses[corpse]['room'] == players[id]['room']:
					playershere.append(corpses[corpse]['name'])
									
			##### Show NPCs in the room #####
			for (nid, pl) in list(npcs.items()):
				if npcs[nid]['room'] == players[id]['room']:
					playershere.append(npcs[nid]['name'])
	
			##### Show items in the room
			for (item, pl) in list(items.items()):
				if items[item]['room'] == players[id]['room']:
					itemshere.append(itemsDB[items[item]['id']]['article'] + ' ' + itemsDB[items[item]['id']]['name'])
			
			# send player a message containing the list of players in the room
			if len(playershere) > 0:
				mud.send_message(id, '<f42>You see: <f77>{}'.format(', '.join(playershere)))
	
			# send player a message containing the list of exits from this room
			mud.send_message(id, '<f42>Exits are: <f94>{}'.format(', '.join(rm['exits'])))
	
			# send player a message containing the list of items in the room
			if len(itemshere) > 0:
				mud.send_message(id, '<f42>You notice: <f222>{}'.format(', '.join(itemshere)))
		else:
			# If argument is given, then evaluate it
			param = params.lower()
			messageSent = False
	
			message = ""
			
			## Go through all players in game
			for p in players:
				if players[p]['authenticated'] != None:
					if players[p]['name'].lower() == param and players[p]['room'] == players[id]['room']:
						message += players[p]['lookDescription']
			
			if len(message) > 0:
				mud.send_message(id, message)
				messageSent = True
	
			message = ""
			
			## Go through all NPCs in game
			for n in npcs:
				if npcs[n]['name'].lower() == param and npcs[n]['room'] == players[id]['room']:
					message += npcs[n]['lookDescription']
	
			if len(message) > 0:
				mud.send_message(id, message)
				messageSent = True
	
			message = ""
			
			## Go through all Items in game
			itemCounter = 0
			for i in items:
				if items[i]['room'].lower() == players[id]['room'] and itemsDB[items[i]['id']]['name'].lower() == param:
					if itemCounter == 0:
						message += itemsDB[items[i]['id']]['long_description']
					itemCounter += 1
	
			if len(message) > 0:
				mud.send_message(id, message)
				messageSent = True
				if itemCounter > 1:
					mud.send_message(id, "You can see " + str(itemCounter) + " of those in the vicinity.")
	
			## If no message has been sent, it means no player/npc/item was found
			if messageSent == False:
				mud.send_message(id, "Look at what?")
	else:
		mud.send_message(id, 'You somehow cannot muster enough perceptive powers to perceive and describe your immediate surroundings...')

def attack(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	if players[id]['canAttack'] == 1:
		isAlreadyAttacking = False
		target = params #.lower()
		targetFound = False
	
		for (fight, pl) in fights.items():
			if fights[fight]['s1'] == players[id]['name']:
				isAlreadyAttacking = True
				currentTarget = fights[fight]['s2']
	
		if isAlreadyAttacking == False:
			if players[id]['name'].lower() != target.lower():
				for (pid, pl) in players.items():							
					if players[pid]['authenticated'] == True and players[pid]['name'].lower() == target.lower():
						targetFound = True
						victimId = pid
						attackerId = id
						if players[pid]['room'] == players[id]['room']:
							fights[len(fights)] = { 's1': players[id]['name'], 's2': target, 's1id': attackerId, 's2id': victimId, 's1type': 'pc', 's2type': 'pc', 'retaliated': 0 }
							mud.send_message(id, '<f214>Attacking <r><u><f32>' + target + '!')
							# addToScheduler('0|msg|<b63>You are being attacked by ' + players[id]['name'] + "!", pid, eventSchedule, eventDB)
						else:
							targetFound = False
	
				# mud.send_message(id, 'You cannot see ' + target + ' anywhere nearby.|')
				if(targetFound == False):
					for (nid, pl) in list(npcs.items()):
						if npcs[nid]['name'].lower() == target.lower():
							victimId = nid
							attackerId = id
							# print('found target npc')
							if npcs[nid]['room'] == players[id]['room'] and targetFound == False:
								targetFound = True
								# print('target found!')
								if players[id]['room'] == npcs[nid]['room']:
									fights[len(fights)] = { 's1': players[id]['name'], 's2': nid, 's1id': attackerId, 's2id': victimId, 's1type': 'pc', 's2type': 'npc', 'retaliated': 0 }
									mud.send_message(id, 'Attacking <u><f21>' + npcs[nid]['name'] + '<r>!')
								else:
									pass
	
				if targetFound == False:
					mud.send_message(id, 'You cannot see ' + target + ' anywhere nearby.')
			else:
				mud.send_message(id, 'You attempt hitting yourself and realise this might not be the most productive way of using your time.')
		else:
			if type(currentTarget) is not int:
				mud.send_message(id, 'You are already attacking ' + currentTarget)
			else:
				mud.send_message(id, 'You are already attacking ' + npcs[currentTarget]['name'])
		# List fights for debugging purposes
		# for x in fights:
			# print (x)
			# for y in fights[x]:
				# print (y,':',fights[x][y])
	else:
		mud.send_message(id, 'Right now, you do not feel like you can force yourself to attack anyone or anything.')

def check(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	if params.lower() == 'inventory' or params.lower() == 'inv':
		mud.send_message(id, 'You check your inventory.')
		if len(list(players[id]['inv'])) > 0:
			mud.send_message(id, 'You are currently in possession of: ')
			for i in list(players[id]['inv']):
				mud.send_message(id, '<b234>' + itemsDB[int(i)]['name'])
		else:
			mud.send_message(id, 'You haven`t got any items on you.')
	elif params.lower() == 'stats':
		mud.send_message(id, 'You check your character sheet.')
	else:
		mud.send_message(id, 'Check what?')

def go(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	if players[id]['canGo'] == 1:
		# store the exit name
		ex = params.lower()

		# store the player's current room
		rm = rooms[players[id]['room']]

		# if the specified exit is found in the room's exits list
		if ex in rm['exits']:
			# go through all the players in the game
			for (pid, pl) in list(players.items()):
				# if player is in the same room and isn't the player
				# sending the command
				if players[pid]['room'] == players[id]['room'] \
					and pid != id:
					# send them a message telling them that the player
					# left the room
					mud.send_message(pid,
							'<f32>{}<r> left via exit {}'.format(players[id]['name'], ex))

			# Trigger old room eventOnLeave for the player
			if rooms[players[id]['room']]['eventOnLeave'] is not "":
				addToScheduler(int(rooms[players[id]['room']]['eventOnLeave']), id, eventSchedule, eventDB)

			# update the player's current room to the one the exit leads to
			players[id]['room'] = rm['exits'][ex]
			rm = rooms[players[id]['room']]
			
			# trigger new room eventOnEnter for the player
			if rooms[players[id]['room']]['eventOnEnter'] is not "":
				addToScheduler(int(rooms[players[id]['room']]['eventOnEnter']), id, eventSchedule, eventDB)

			# go through all the players in the game
			for (pid, pl) in list(players.items()):
				# if player is in the same (new) room and isn't the player
				# sending the command
				if players[pid]['room'] == players[id]['room'] \
					and pid != id:
					# send them a message telling them that the player
					# entered the room
					# mud.send_message(pid, '{} arrived via exit {}|'.format(players[id]['name'], ex))
					mud.send_message(pid, '<f32>{}<r> has arrived.'.format(players[id]['name'], ex))

			# send the player a message telling them where they are now
			#mud.send_message(id, 'You arrive at {}'.format(players[id]['room']))
			mud.send_message(id, 'You arrive at <f106>{}'.format(rooms[players[id]['room']]['name']))
		else:
		# the specified exit wasn't found in the current room
			# send back an 'unknown exit' message
			mud.send_message(id, "Unknown exit <f226>'{}'".format(ex))
	else:
		mud.send_message(id, 'Somehow, your legs refuse to obey your will.')

def drop(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	itemInDB = False
	inventoryNotEmpty = False
	itemInInventory = False
	itemID = None
	itemName = None
	
	for (iid, pl) in list(itemsDB.items()):
		if itemsDB[iid]['name'].lower() == str(params).lower():
			# ID of the item to be dropped
			itemID = iid
			itemName = itemsDB[iid]['name']
			itemInDB = True
			break
		else:
			itemInDB = False
			itemName = None
			itemID = None

	# Check if inventory is not empty
	if len(list(players[id]['inv'])) > 0:
		inventoryNotEmpty = True
	else:
		inventoryNotEmpty = False

	# Check if item is in player's inventory
	for item in players[id]['inv']:
		if int(item) == itemID:
			itemInInventory = True
			break
		else:
			itemInInventory = False
	
	if itemInDB and inventoryNotEmpty and itemInInventory:
		inventoryCopy = deepcopy(players[id]['inv'])
		for i in inventoryCopy:
			if int(i) == itemID:
				# Remove first matching item from inventory
				players[id]['inv'].remove(i)
				break

		# Create item on the floor in the same room as the player
		items[getFreeKey(items)] = { 'id': itemID, 'room': players[id]['room'], 'whenDropped': int(time.time()), 'lifespan': 900000000, 'owner': id }
		
		# Print itemsInWorld to console for debugging purposes
		# for x in itemsInWorld:
			# print (x)
			# for y in itemsInWorld[x]:
					# print(y,':',itemsInWorld[x][y])
					
		mud.send_message(id, 'You drop ' + itemsDB[int(i)]['article'] + ' ' + itemsDB[int(i)]['name'] + ' on the floor.')
		
	else:
		mud.send_message(id, 'You don`t have that!')

def take(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	itemInDB = None
	itemID = None
	itemName = None
	# itemInRoom = None

	for (iid, pl) in list(itemsDB.items()):
		if itemsDB[iid]['name'].lower() == str(params).lower():
			# ID of the item to be picked up
			itemID = iid
			itemName = itemsDB[iid]['name']
			itemInDB = True
			break
		else:
			itemInDB = False
			itemName = None
			itemID = None

	itemsInWorldCopy = deepcopy(items)

	for (iid, pl) in list(itemsInWorldCopy.items()):
		if itemsInWorldCopy[iid]['room'] == players[id]['room']:
			# print(str(itemsDB[itemsInWorld[iid]['id']]['name'].lower()))
			# print(str(params).lower())
			if itemsDB[items[iid]['id']]['name'].lower() == str(params).lower():
				players[id]['inv'].append(str(itemID))
				del items[iid]
				# mud.send_message(id, 'You pick up and place ' + itemsDB[itemID]['article'] + ' ' + itemsDB[itemID]['name'] + ' in your inventory.')
				itemPickedUp = True
				break
			else:
				# mud.send_message(id, 'You cannot see ' + str(params) + ' anywhere.')
				itemPickedUp = False
		else:
			# mud.send_message(id, 'You cannot see ' + str(params) + ' anywhere.')
			itemPickedUp = False
			# break

	if itemPickedUp == True:
		mud.send_message(id, 'You pick up and place ' + itemsDB[itemID]['article'] + ' ' + itemsDB[itemID]['name'] + ' in your inventory.')
		itemPickedUp = False
	else:
		mud.send_message(id, 'You cannot see ' + str(params) + ' anywhere.')
		itemPickedUp = False

def webclienttest(params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	mud.send_message(id, '<f30><u>Foreground')
	mud.send_message(id, '<f31><b>Foreground')
	mud.send_message(id, '<f32><u><b>Foreground')
	mud.send_message(id, '<f33>Foreground')
	mud.send_message(id, '<f34>Foreground')
	mud.send_message(id, '<f35>Foreground')
	mud.send_message(id, '<f36>Foreground')
	mud.send_message(id, '<f37>Foreground')

	mud.send_message(id, '<b40><u>Background')
	mud.send_message(id, '<b41><b>Background')
	mud.send_message(id, '<b42><u><b>Background')
	mud.send_message(id, '<b43>Background')
	mud.send_message(id, '<b44>Background')
	mud.send_message(id, '<b45>Background')
	mud.send_message(id, '<b46>Background')
	mud.send_message(id, '<b47>Background')
	addToScheduler('0|msg|Dying in 10 seconds...', id, eventSchedule, eventDB)
	addToScheduler('10|setPlayerRoom|$rid=666$', id, eventSchedule, eventDB)
	addToScheduler('10|msg|You have died!', id, eventSchedule, eventDB)

def runCommand(command, params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses):
	switcher = {
		"sendCommandError": sendCommandError,
		"go": go,
		"look": look,
		"help": help,
		"say": say,
		"attack": attack,
		"take": take,
		"drop": drop,
		"check": check,
		"webclienttest": webclienttest,
	}

	try:
		switcher[command](params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses)
	except Exception as e:
		print(str(e))
		switcher["sendCommandError"](params, mud, playersDB, players, rooms, npcsDB, npcs, itemsDB, items, envDB, env, eventDB, eventSchedule, id, fights, corpses)
