# Import pandas and numpy
import pandas as pd
import numpy as np

# Import unittest 
import unittest

# Import the module to be tested
import bmrs_data


# Create a class to test the functions
class TestBMRSData(unittest.TestCase):
    
    def test_get_bmrs_data(self):
        # Test the function
        data = bmrs_data.get_bmrs_data("2020-01-01")
        
        # Check the type of the data
        self.assertIsInstance(data,pd.DataFrame)
        
        # Check the shape of the data
        self.assertGreater(data.shape[0],0) 
        
        # Check the columns
        self.assertIn("startTime",data.columns)
        self.assertIn("systemSellPrice",data.columns)
        self.assertIn("systemBuyPrice",data.columns)
        
        # Check the data types
        self.assertEqual(data["startTime"].dtype,"datetime64[ns]")
        self.assertEqual(data["systemSellPrice"].dtype,np.float64)
        self.assertEqual(data["systemBuyPrice"].dtype,np.float64)
        
    def test_get_bmrs_data_range(self):
        # Test the function
        data = bmrs_data.get_bmrs_data_range("2020-01-01","2020-01-05")
        
        # Check the type of the data
        self.assertIsInstance(data,pd.DataFrame)
        
        # Check the shape of the data
        self.assertGreater(data.shape[0],0)
        
        # Check the columns
        self.assertIn("startTime",data.columns)
        self.assertIn("systemSellPrice",data.columns)
        self.assertIn("systemBuyPrice",data.columns)
        
        # Check the data types
        self.assertEqual(data["startTime"].dtype,"datetime64[ns]")
        self.assertEqual(data["systemSellPrice"].dtype,np.float64)
        self.assertEqual(data["systemBuyPrice"].dtype,np.float64)
        
        # Create a date index
        date_index = pd.date_range(start="2020-01-01 00:00:00",end="2020-01-05 23:30:00",freq="30T")
        
    
        
        # Check the index in the data
        self.assertTrue(data["startTime"].isin(date_index).all())
        
    
    
# Run the tests
if __name__ == "__main__":
    unittest.main()

# Raise an error if testing is imported
else:
    raise ImportError("This module cannot be imported") 
    
        
        