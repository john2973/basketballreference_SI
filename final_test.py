from final import *
import unittest

class TestBasketballSearch(unittest.TestCase):

    def test_basketball_objects(self):
        basketball_list = get_basketball_name('a')

        self.assertEqual(str(basketball_list[0]), 'Alaa Abdelnaby Career Began: 1991 Career Ended: 1995 Position: F-C Height: 6-10 Weight: 240 Career Points: 5.7')

class TestDataBase(unittest.TestCase):

    def test_player_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Players'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Kareem Abdul-Jabbar',), result_list)
        self.assertEqual(len(result_list), 158)

        sql = '''
            SELECT Name, StartYear, EndYear,
                   Position, Height, Weight
            FROM Players
            WHERE Height = '6-10'
            ORDER BY StartYear DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(result_list[0][0], 'Bam Adebayo')

        conn.close()

    def test_stats_table(self):

        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT GamesPlayed
            FROM Stats
            WHERE AvgPoints= "5.7"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertEqual(len(result_list), 3)
        self.assertEqual(result_list[0][0], 256)

        conn.close()
class TestPlayerSearch(unittest.TestCase):

    def test_player_search(self):
        results = process_command('players position=F new')
        self.assertEqual(results[0][0], 'Bam Adebayo')

        results = process_command('players position=F old')
        self.assertEqual(results[0][0], 'John Abramovic')

class TestStatsSearch(unittest.TestCase):

    def test_stats_search(self):
        results = process_command('stats name=Bob Armstrong')
        self.assertEqual(results[0][1], 19)
        self.assertEqual(results[0][2], 1.5)

        results = process_command('stats name=Jesse Arnelle')
        self.assertEqual(results[0][0], 'Jesse Arnelle')
        self.assertEqual(results[0][1], 31)







if __name__ == '__main__':
    unittest.main()
