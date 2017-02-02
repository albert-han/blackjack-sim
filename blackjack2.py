import random
from itertools import combinations_with_replacement
import re, pdb
from strategy import StandStrategy, DoubleDownStrategy, SplitStrategy
import numpy as np

class Hand(object):
    def __init__(self):
        self.cards = {'ace':[], 'number':[], 'face':[]}
        self.value = self.getValue()

    def addCard(self, card, split_pos=0):
        if 'Ace' in card:
            self.cards['ace'].append(card)
            self.value = self.getValue()
        elif any([f in card for f in ['Jack', 'Queen', 'King']]):
            self.cards['face'].append(card)
            self.value = self.getValue()
        else:
            self.cards['number'].append(card)
            self.value = self.getValue()

    def getAceValue(self, ace_cards, fv, nv):
        if len(ace_cards) == 0:
            return 0
        combos = list(combinations_with_replacement('12', r=len(ace_cards)))
        aceCombos = []
        for combo in combos:
            newCombo = []
            for i in range(len(combo)):
                newCombo.append(re.sub('2', '11', combo[i]))
            aceCombos.append(tuple(newCombo))
        curValue = fv+nv
        aceCombos.reverse()
        aceValue = self.getBestAceValue(aceCombos, curValue)
        return aceValue

    def getBestAceValue(self, aceCombos, curValue):
        aceValue = sum([int(ace) for ace in aceCombos[0]])
        if len(aceCombos) == 1:
            return aceValue
        elif aceValue + curValue < 22:
            return aceValue
        return self.getBestAceValue(aceCombos[1:], curValue)


class DealerHand(Hand):
    def getValue(self):
        faceValue = len(self.cards['face'])*10
        numberValue = sum([int(card[1]) for card in self.cards['number']])
        aceValue = self.getAceValue(self.cards['ace'], faceValue, numberValue)
        return faceValue + numberValue + aceValue


class PlayerHandMultiple(object):
    def __init__(self):
        self.hands = []

    def addPlayerHand(self, player_hand):
        self.hands.append(player_hand)


class PlayerHandSingle(Hand):
    def __init__(self, player_hand_multiple):
        Hand.__init__(self)
        self.playerHandMultiple = player_hand_multiple

    def getValue(self):
        faceValue = len(self.cards['face'])*10
        numberValue = sum([int(card[1]) for card in self.cards['number']])
        aceValue = self.getAceValue(self.cards['ace'], faceValue, numberValue)
        return faceValue + numberValue + aceValue

    def splitHand(self, rank):
        if rank == 'Ace':
            splitCard = self.cards['ace'][1]
            del self.cards['ace'][1]
        elif re.search('[1-9]+', rank):
            splitCard = self.cards['number'][1]
            del self.cards['number'][1]
        else:
            splitCard = self.cards['face'][1]
            del self.cards['face'][1]
        newPlayerHandSingle = PlayerHandSingle(self.playerHandMultiple)
        newPlayerHandSingle.addCard(splitCard)
        index = self.playerHandMultiple.hands.index(self)
        self.playerHandMultiple.hands.insert(index+1, newPlayerHandSingle)

    def checkSplitCards(self, dealer_upcard):
        splitStrategy = SplitStrategy(dealer_upcard, self.getValue(), self.cards)
        move = splitStrategy.getMove()
        return move

    def checkDoubleDown(self, dealer_upcard):
        doubleDownStrategy = DoubleDownStrategy(dealer_upcard, self.getValue(), self.cards)
        move = doubleDownStrategy.getMove()
        return move

    def checkStand(self, dealer_upcard):
        standStrategy = StandStrategy(dealer_upcard, self.getValue(), self.cards)
        move = standStrategy.getMove()
        return move


class Deck(object):
    def __init__(self, reshuffle_percentage):
        #random.seed(0)
        self.rp = reshuffle_percentage
        self.deck = self.buildDeck()
        self.n = len(self.deck)

    def buildDeck(self, n=1):
        deck = []
        suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
        ranks = ['Ace', '2', '3', '4', '5', '6', '7',
                 '8', '9', '10', 'Jack', 'Queen', 'King']
        for suit in suits:
            for rank in ranks:
                deck.append((suit, rank))
        return deck*n

    def checkReshuffle(self):
        if (len(self.deck) / self.n) < self.rp:
            self.reshuffleDeck()

    def reshuffleDeck(self):
        self.deck = self.buildDeck()

    def randomDraw(self):
        self.checkReshuffle()
        card = random.choice(self.deck)
        self.deck.remove(card)
        return card


class BlackJack(object):
    def __init__(self, num_trials, reshuffle_percentage):
        self.deck = Deck(reshuffle_percentage)
        self.numTrials = num_trials
        self.games = []
        self.scores = self.runSim()

    def runSim(self):
        results = []
        for i in range(self.numTrials):
            g = Game(self.deck)
            g.playGame()
            results.append(g.scores)
            self.games.append(g)
            #self.deck.reshuffleDeck()
        return results


class Game(object):
    def __init__(self, deck):
        self.dealerHand = DealerHand()
        self.playerHandMultiple = PlayerHandMultiple()
        self.playerHandSingle = PlayerHandSingle(self.playerHandMultiple)
        self.deck = deck
        self.dealerUpcard = ''
        self.playerResults = []
        self.scores = {}

    def processDealerUpcard(self, rank):
        if rank in ['Queen', 'King', 'Jack']:
            return 10
        else:
            return rank

    def hit(self, hand):
        hand.addCard(self.deck.randomDraw())

    def deal(self):
        self.playerHandSingle.addCard(self.deck.randomDraw())
        upcard = self.deck.randomDraw()
        self.dealerHand.addCard(upcard)
        self.dealerUpcard = self.processDealerUpcard(upcard[1])
        self.playerHandSingle.addCard(self.deck.randomDraw())
        self.dealerHand.addCard(self.deck.randomDraw())
        self.playerHandMultiple.addPlayerHand(self.playerHandSingle)

    def compareResults(self, pr, dr):
        playerScore = 0
        dealerScore = 0
        try:
            for result in pr:
                if dr > 21:
                    if result <= 21:
                        playerScore += 1
                    else:
                        dealerScore += 1
                elif dr <= 21:
                    if result > 21:
                        dealerScore += 1
                    elif result == dr:
                        continue
                    elif result > dr:
                        playerScore += 1
                    else:
                        dealerScore += 1
        except TypeError:
            pdb.set_trace()
        return {'Player Score': playerScore, 'Dealer Score': dealerScore}

    def playGame(self):
        self.deal()
        self.playerResults = np.array(self.playerCheckHands()).flatten()
        self.dealerResults = np.array(self.dealerCheckHand()).flatten()
        self.scores = self.compareResults(self.playerResults, self.dealerResults)


    def dealerCheckHand(self):
        while self.dealerHand.getValue() < 17:
            self.hit(self.dealerHand)
        return self.dealerHand.getValue()

    def playerCheckHands(self):
        results = []
        handsAtStart = self.playerHandMultiple.hands.copy()
        for hand in handsAtStart:
            result = self.playStrat(hand, self.dealerUpcard)
            for elt in results:
                results.append(elt)
        return result

    def playStrat(self, hand, dealer_upcard):
        if hand.getValue() >= 17:
            return hand.getValue()
        step1 = hand.checkSplitCards(dealer_upcard)
        if hand.getValue() < 8:
            self.hit(hand)
            return self.playStrat(hand, dealer_upcard)
        if step1 == 'hit':
            self.hit(hand)
            return self.playStrat(hand, dealer_upcard)
        elif step1 == 'stand':
            return hand.getValue()
        elif step1 in ['Ace', '2', '3', '6', '7', '8', '9']:
            hand.splitHand(step1)
            return self.playerCheckHands()
        elif step1 == 'step2':
            step2 = hand.checkDoubleDown(dealer_upcard)
            if step2 == 'hit':
                self.hit(hand)
                return self.playStrat(hand, dealer_upcard)
            elif step2 == 'stand':
                return hand.getValue()
            elif step2 == 'double':
                self.hit(hand)
                return hand.getValue()
            elif step2 == 'step3':
                step3 = hand.checkStand(dealer_upcard)
                if step3 == 'hit':
                    self.hit(hand)
                    return self.playStrat(hand, dealer_upcard)
                elif step3 == 'stand':
                    return hand.getValue()



blackJack = BlackJack(100, reshuffle_percentage=.30)
print(blackJack.scores)


