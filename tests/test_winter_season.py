"""python -m unittest tests.test_winter_season"""
import unittest
from tools.winter import collect

def heat(name, ranks, status='Finished'):
    return {'name': name, 'status': status, 'official': 'Official' if status == 'Finished' else 'Start List',
            'competitors': [{'rank': r, 'name': f'p{i}', 'noc': 'KOR', 'time': '40.1'} for i, r in enumerate(ranks)]}

class Podiums(unittest.TestCase):
    def test_short_track_final_a_only(self):
        dist = {'rounds': [{'name': 'Semifinals', 'heats': [heat('Heat 1', [1, 2, 3, 4])]},
                           {'name': 'Finals', 'heats': [heat('Final', [None] * 5, 'Getting Ready'), heat('Final B', [1, 2, 3])]}]}
        self.assertIsNone(collect.podium_st(dist))  # Final B or semis never make a podium
        dist['rounds'][1]['heats'][0] = heat('Final', [2, 1, 3, 4, 5])
        self.assertEqual([p['rank'] for p in collect.podium_st(dist)], [1, 2, 3])

    def test_speed_division_b_ignored(self):
        race = {'division': 'B', 'official': True, 'rows': [{'rank': 1, 'name': 'a', 'noc': 'KOR', 'time': '1'}]}
        self.assertIsNone(collect.podium_ss(race))
        race['division'] = 'A'
        self.assertEqual(len(collect.podium_ss(race)), 1)

    def test_figure_needs_all_segments(self):
        seg = lambda st: {'SP': {'status': 'Finished'}, 'FS': {'status': st}}
        cat = {'rows': [{'rank': 1, 'name': 'a', 'noc': 'KOR', 'points': '250', 'segments': seg('Scheduled')}]}
        self.assertIsNone(collect.podium_fs(cat))
        cat['rows'][0]['segments'] = seg('Finished')
        self.assertEqual(collect.podium_fs(cat)[0]['time'], '250')

if __name__ == '__main__':
    unittest.main()
