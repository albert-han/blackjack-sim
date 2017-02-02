import random, pylab

class Strategy(object):
    def __init__(self, dealer_upcard, value, cards):
        self.dealerUpcard = dealer_upcard
        self.value = value 
        self.cards = cards
        self.a, self.n = self.getRanks()

    def upcardRange(self, a, b):
        if self.dealerUpcard == 'Ace':
            return False
        return a <= int(self.dealerUpcard) <= b

    def getRanks(self):
        a = [card[1] for card in self.cards['ace']]
        n = [card[1] for card in self.cards['number']]
        return a, n

class StandStrategy(Strategy):
    def getMove(self):
        if self.value == 12:
            if self.upcardRange(4, 6):
                return 'stand'
            else:
                return 'hit'
        elif self.value in range(13, 16+1):
            if self.upcardRange(2, 6):
                return 'stand'
            else:
                return 'hit'
        elif self.value in range(17, 21+1):
            return 'stand'

        if len(self.a) == 1 and len(self.n) == 1:
            if self.n[0] == '9':
                return 'stand'

        return 'no more steps'

class DoubleDownStrategy(Strategy):
    def getMove(self):
        if self.value == 8:
            if self.upcardRange(5, 6):
                return 'double'
            else:
                return 'hit'
        elif self.value == 9:
            if self.upcardRange(2, 6):
                return 'double'
            else:
                return 'hit'
        elif self.value == 10:
            if self.upcardRange(2, 9):
                return 'double'
            else:
                return 'hit'
        elif self.value == 11:
            return 'double'
        
        if len(self.a) == 1 and len(self.n) == 1:
            if self.n[0] in ['2', '3', '4', '5']:
                if self.upcardRange(4, 6):
                    return 'double'
                else:
                    return 'hit'
            elif self.n[0] == '6':
                if self.upcardRange(2, 6):
                    return 'double'
                else:
                    return 'hit'
            elif self.n[0] == '7':
                if self.upcardRange(3, 6):
                    return 'double'
                elif self.dealer_upcard in ['2', '7', '8', 'Ace']:
                    return 'stand'
                else:
                    return 'hit'
            elif self.n[0] == '8':
                if self.upcardRange(6, 6):
                    return 'double'
                else:
                    return 'stand'

        return 'step3'


class SplitStrategy(Strategy):
    def getMove(self):
        if self.a == ['Ace', 'Ace']:
            return 'Ace'
        elif self.n == ['2', '2']:
            if self.upcardRange(3, 7):
                return '2'
            else:
                return 'hit'
        elif self.n == ['3', '3']:
            if self.upcardRange(4, 7):
                return '3'
            else:
                return 'hit'
        elif self.n == ['6', '6']:
            if self.upcardRange(2, 6):
                return '6'
            else:
                return 'hit'
        elif self.n == ['7', '7']:
            if self.upcardRange(2, 7):
                return '7'
            elif self.dealer_upcard == '10':
                return 'stand'
            else:
                return 'hit'
        elif self.n == ['8', '8']:
            return '8'
        elif self.n == ['9', '9']:
            if (self.upcardRange(2, 6) or self.upcardRange(8, 9)):
                return '9'
            else:
                return 'Stand'
        else:
            return 'step2'