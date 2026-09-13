import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from spice_utils import at,crossing,average,logic
class Measurements(unittest.TestCase):
    def test_interpolation_and_time_weighted_average(self):
        rows=[[0,0],[1,2],[4,2]]
        self.assertEqual(at(rows,.5,1),1)
        self.assertEqual(average(rows,1,0,4),1.75)
        self.assertAlmostEqual(average(rows,1,.5,2),2.75/1.5)
    def test_edges_are_direction_and_window_specific(self):
        rows=[[0,0],[1,2],[2,0],[3,2]]
        self.assertEqual(crossing(rows,1,1,0,1,True),.5)
        self.assertEqual(crossing(rows,1,1,1,2,False),1.5)
        with self.assertRaises(ValueError): crossing(rows,1,1,1,2,True)
    def test_reject_ambiguous_logic(self):
        self.assertEqual(logic(.1,1.8),0)
        self.assertEqual(logic(1.7,1.8),1)
        with self.assertRaises(AssertionError): logic(.9,1.8)
    def test_no_extrapolation(self):
        with self.assertRaises(ValueError): at([[0,0],[1,1]],2,1)
if __name__=='__main__': unittest.main()
