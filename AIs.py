# Collection of functions each AI should implement:
# __init__(self, name)
# playCard(self)
# updateInfo(self)
# orderUp(self, center_card)
# pickUp(self, card)
# pickSuit(self, out_suit)
# reset(self)
# setHand(self, new-hand)


from my_globals import *

import random
random.seed() # automatically uses system time

class Player(object):
	def __init__(self, name):
		self.BaseSetUp(name)
		
	def printHand(self):
		for x in range(len(self.hand)):
			print "[%d: %s], " % (x, self.hand[x]),
		print
		
	def BaseSetUp(self, name):
		self.name = name # name is a unique identifier
		self.tricks = 0
		self.hand = []
		
	def validMoves(self):
		# assume that the lead, left bower problem is taken care of
		validmoves = [] 
		for x in self.hand:
			if x.num == 11:
				if game.lead == game.trump and x.suit == offSuit(game.trump):
					validmoves.append(x)
			elif x.suit == game.lead:
				validmoves.append(x)
	
		if not validmoves:
			validmoves = self.hand
			
		return tuple(validmoves)
		
	def setHand(self, hand):
		assert len(hand) == 5, "from setHand of %s, hand needs to be 5" % self.name
		self.hand = hand
		
	def trumpIsSet(self):
		pass

class RandomPlay(Player):
	def __init__(self, name):
		self.BaseSetUp(name)
		
	def playCard(self):
		moves = self.validMoves()
		chosen = random.choice(moves)
		self.hand.remove(chosen)
		print "%s plays %s" % (self.name, chosen)
		return chosen
		
	def updateInfo(self, winner):
		# not necessary for random play
		pass

	def orderUp(self, center_card):
		choice = random.choice([True, False])
		if choice == True:
			print "%s orders up" % (self.name)
		else:
			print "%s passes" % (self.name)

	def pickSuit(self, out_suit):
		if random.choice([True, False]) or game.dealer == self:
			choice = random.choice([x for x in [heart, spade, club, diamond] if x != out_suit])
			print "%s plays %s" % (self.name, choice)
			return choice
		else:
			print "%s passes" % (self.name)
			return None

	def pickUp(self, top):
		assert type(top) == Card, "pickUp was given a %s, it wants a Card" % type(top)
		discard = random.choice(self.hand)
		self.hand.remove(discard)
		self.hand.append(top)
		return discard
		
	def reset(self):
		# not necessary for random play
		pass

class SimpleStat(Player):
	def __init__(self, name):
		self.BaseSetUp(name)
		
		self.tfc = set(allcards) # tfc stands for total free cards
		self.pm = set(allcards) # partner model
		self.opp1m = set(allcards) # opponent 1 model
		self.opp2m = set(allcards) # opponent 2 model
		
		self.reset()
		
	def setHand(self, hand):
		Player.setHand(self, hand)
		self.tfc -= set(self.hand)
		
	def setRelations(self, partner, opp1, opp2):
		self.partner = partner
		self.opp1 = opp1
		self.opp2 = opp2
		
	def playCard(self):
		poss_opp_cards = self.tfc & (self.opp2m | self.opp1m)
		
		poss_par_cards = self.tfc & self.pm
		
		valids = self.validMoves()
		
		if len(valids) == 1:
			self.hand.remove(valids[0])
			print "%s plays %s" % (self.name, valids[0])
			return valids[0]
			
		if game.center:
			if len(poss_opp_cards & self.suits[game.lead]) < 3:
				chosen = random.choice(self.hand)
				self.hand.remove(chosen)
				print "%s plays %s" % (self.name, chosen)
				return chosen
		chosen = sorted(self.hand, key=lambda c: c.num, reverse=True)[0]
		self.hand.remove(chosen)
		print "%s plays %s" % (self.name, chosen)
		return chosen
			
			

	def updateInfo(self, winner):
		assert len(game.center) == 4, "there should be four cards in the center"
		self.tfc -= set(game.center.keys())
		
		for c in game.center.keys():
			if game.center[c] == winner:
				win_card = c
				break
		
		for c, p in game.center.items():
			if p == self: continue
			
			# if they lost then we can consider that they do not have any better cards in their hand
			if self.opp1 != winner and self.opp2 != winner:
				if game.lead == win_card.suit:
					if p == self.opp1:
						self.opp1m -= self.suits[game.lead]
					elif p == self.opp2:
						self.opp2m -= self.suits[game.lead]
						
				else:
					pass
			else:
				if game.lead == win_card.suit:
					self.pm -= self.suits[game.lead]

	def orderUp(self, center_card):
		poss_powers = filter(lambda c: c.suit == center_card.suit, self.hand)
		
		if len(poss_powers) >= 3:
			print "%s orders up" % (self.name)
			return True
			
		for c in self.hand:
			if (c.suit == center_card.suit or c.suit == offSuit(center_card.suit)) and c.num == 11:
				if len(poss_powers) >= 2:
					print "%s orders up" % (self.name)
					return True
		print "%s passes" % (self.name)
		return False

	def pickSuit(self, out_suit):
		nums = { heart: 0, club : 0, spade : 0, diamond : 0 }
		
		for c in self.hand:
			nums[c.suit] += 1
				
		for s, n in nums.items():
			if n >= 3:
				print "%s chooses %s" % (self.name, s)
				return s
		print "%s passes" % (self.name)
		return None

	def pickUp(self, card):
		nums = { heart: 0, club : 0, spade : 0, diamond : 0 }
		
		for c in self.hand:
			nums[c.suit] += 1
		
		d_suit = [] # suits to possibly discard
		
		for s, n in nums.items():
			if n == 1 and s != card.suit:
				d_suit.append(s)
				
		if not d_suit:	
			for s, n in nums.items():
				if n == 2 and s != card.suit:
					d_suit.append(s)
					break
					
		d_cards = [] # cards to consider for discard
		
		for c in self.hand:
			if c.suit in d_suit:
				d_cards.append(c)
				
		if len(d_cards) == 1: return d_cards[0]
		elif len(d_cards) == 0:
			try:
				return random.choice(filter(lambda c: c.suit != card.suit, self.hand))
			except IndexError:
				# if that doesnt work then it doesn't matter because you have all the trump
				return random.choice(self.hand)
		else:
			return random.choice(self.hand)

	def reset(self):
		"""Reset the information gathered by the ai without reinstatiating it.
		
			For use between rounds.
		"""
		
		self.tfc = set(allcards)
		
		# Jacks are a special case
		self.suits = {heart:set(filter(lambda c: c.suit == heart and c.num != 11, allcards)),
			spade:set(filter(lambda c: c.suit == spade and c.num != 11, allcards)),
			club:set(filter(lambda c: c.suit == club and c.num != 11, allcards)),
			diamond:set(filter(lambda c: c.suit == diamond and c.num != 11, allcards))}
		
	def trumpIsSet(self):
		jacks = filter(lambda c: c.num == 11, allcards)
		
		for c in jacks:
			if c.suit == offSuit(game.trump):
				if game.trump == heart:
					self.suits[heart].add(c)
				elif game.trump == spade:
					self.suits[spade].add(c)
				elif game.trump == club:
					self.suits[club].add(c)
				else:
					self.suits[diamond].add(c)
					
			else:
				if c.suit == heart:
					self.suits[heart].add(c)
				elif c.suit == spade:
					self.suits[spade].add(c)
				elif c.suit == club:
					self.suits[club].add(c)
				else:
					self.suits[diamond].add(c)
		
class RealPlayer(Player):
	def __init__(self, name):
		self.BaseSetUp(name)
	
	def playCard(self):
		self.printHand()
		move = int(raw_input("Please enter the # of the card you wish to play (%s|%s):" % (game.trump, game.lead)))
		valid = self.validMoves()
		while True:
			if type(move) is int and 0 <= move < len(self.hand) and self.hand[move] in valid:
				chosen = self.hand.pop(move)
				print "%s plays %s" % (self.name, chosen)
				return chosen
			else:
				move = int(input("Please enter a valid move: "))
				
	def updateInfo(self, winner):
		print "The scores are A: %s, B %s" % (game.scoreA, game.scoreB)
		print "The winner of the previous trick was %s" % (winner.name)
		keys = game.center.keys()
		#print "Cards played: %s, %s, %s, %s" % (keys[0], keys[1], keys[2], keys[3])

	def orderUp(self, center_card):
		self.printHand()
		if self == game.dealer:
			if query_yes_no("Do you want to pick up %s?" % (center_card)):
				print "%s orders up %s" % (self.name, center_card.suit)
				return True
			else:
				print "%s passes" % (self.name)
				return False

		else:
			choice = query_yes_no("Do you want to order the dealer up: %s?" % (center_card))
			if choice == False:
				print "%s passes" % (self.name)
			else:
				print "%s orders up %s" % (self.name, center_card.suit)
			return choice

	def pickSuit(self, out_suit):
		open_suits = (set(heart, spade, diamond, club) - set(out_suit))
		if query_yes_no("Do you want to pick a suit? (out suit is %s)" % out_suit):
			print "Pick %s, %s, or %s." % (open_suits[0], open_suits[1], open_suits[2])
			
			while True:
				choice = raw_input("Enter the first letter of the suit name: ").lower()
				if choice[0] == 'd':
					if diamond in open_suits:
						print "%s plays %s" % (self.name, "diamond")
						return diamond
				elif choice[0] == 'h':
					if heart in open_suits:
						print "%s plays %s" % (self.name, "heart")
						return heart
				elif choice[0] == 's':
					if spade in open_suits:
						print "%s plays %s" % (self.name, "spade")
						return spade
				elif choice[0] == 'c':
					if club in open_suits:
						print "%s plays %s" % (self.name, "club")
						return club
				else:
					print "Please enter a valid choice."
		else:
			return False
		
	def pickUp(self, center_card):
		print "You are picking up %s." % (center_card)
		print "Your hand contains:",
		self.printHand()
		
		discard = int(raw_input("Please enter the # of the card you wish to discard: "))
		while True:
			if type(discard) is int and 0 <= discard < len(self.hand):
				choice = self.hand.pop(discard)
				self.hand.append(center_card)
				return choice
			else:
				discard = int(input("Please enter a valid discard: "))
	
	def reset(self):
		# not necessary for a real player
		pass
