import unittest 
from tree_sort import tree_sort 
 
class TestTreeSort(unittest.TestCase): 
 
    def test_empty(self): 
        self.assertEqual(tree_sort([]), []) 
 
    def test_one(self): 
        self.assertEqual(tree_sort([5]), [5]) 
 
    def test_sorted(self): 
        self.assertEqual(tree_sort([1, 2, 3]), [1, 2, 3]) 
 
    def test_unsorted(self): 
        self.assertEqual(tree_sort([3, 1, 2]), [1, 2, 3]) 
 
    def test_duplicates(self): 
        self.assertEqual(tree_sort([3, 1, 3, 2]), [1, 2, 3, 3]) 
 
    def test_negative(self): 
        self.assertEqual(tree_sort([-1, -3, 2]), [-3, -1, 2]) 
 
if __name__ == '__main__': 
    unittest.main()
