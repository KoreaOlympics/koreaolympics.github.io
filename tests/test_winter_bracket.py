"""python -m unittest tests.test_winter_bracket"""
import unittest
from tools.winter import bracket

def heat(*rows):
    return {'competitors': [{'name': n, 'noc': 'X', 'rank': r, 'time': t, 'qual': q} for n, r, t, q in rows]}

class Bracket(unittest.TestCase):
    def test_parse(self):
        r = bracket.parse_rule('The first placed skater from each race and up to a maximum of ten fastest second place skaters qualify for Heats.')
        self.assertEqual((r['places'], r['extra'], r['extra_place'], r['next']), (1, 10, 2, 'Heats'))
        r = bracket.parse_rule('The first, second and third placed skaters from each race and up to a maximum of one fastest fourth place skater qualify for Quarterfinals.')
        self.assertEqual((r['places'], r['extra'], r['extra_place']), (3, 1, 4))

    def test_official_codes_win(self):
        hs = [heat(('a', 1, '44.0', 'Q'), ('b', 2, '44.5', 'Q'), ('c', 3, '44.6', 'q'), ('d', 4, '45.0', '')),
              heat(('e', 1, '43.9', 'Q'), ('f', 2, '44.1', 'Q'), ('g', 3, '44.9', ''), ('h', 4, '46', 'ADV'))]
        q = bracket.qualifiers(hs, bracket.parse_rule('The first and second placed skaters from each race and up to a maximum of one fastest third place skaters qualify for Final.'))
        self.assertEqual([c['name'] for c in q], ['e', 'a', 'f', 'b', 'h', 'c'])

    def test_rule_before_codes(self):
        hs = [heat(('a', 1, '44.0', ''), ('b', 2, '44.5', ''), ('c', 3, '44.6', '')),
              heat(('e', 1, '43.9', ''), ('f', 2, '44.1', ''), ('g', 3, '44.4', ''))]
        q = bracket.qualifiers(hs, bracket.parse_rule('The first and second placed skaters from each race and up to a maximum of one fastest third place skaters qualify for Final.'))
        self.assertEqual([c['name'] for c in q], ['e', 'a', 'f', 'b', 'g'])

    def test_serpentine(self):
        races = bracket.distribute(list(range(8)), 2)
        self.assertEqual(races, [[0, 3, 4, 7], [1, 2, 5, 6]])

if __name__ == '__main__':
    unittest.main()
