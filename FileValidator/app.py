import importlib
from decimal import Decimal
from math import isnan
from string import ascii_letters, digits

import pyrsistent as p
from tqdm import tqdm #Optional if you want a status bar
from toolz import  keymap
from toolz.dicttoolz import valfilter, dissoc

class TheValidator(object):
    def __init__(self,
                 dataframe,
                 file_type: str):
        self.validate_dict = dataframe.to_dict(orient='records')
        self.module = self.dynamic_import(file_type)
        self.dataframe = dataframe

    def main(self):
        #Make a copy of the original dataframe to return status
        output = self.dataframe.copy()
        output['Status'] = None
        output['Error Message(s)'] = None
        """tqdm is a progress bar module"""
        for idx, row in enumerate(tqdm(self.validate_dict)):
            try:
                self.validation(row)
            except  p.InvariantException as err:
                if err.missing_fields:
                    output.set_value(idx,
                      'Error Message(s)','Missing: {}'.format(err.missing_fields))
                    output.loc[idx, 'Status'] = 'Error'
                elif err.invariant_errors:
                    output.set_value(idx,
                      'Error Message(s)', 'Failed Validation: {}'.format(err.invariant_errors))
                    output.loc[idx, 'Status'] = 'Error'
                continue
            except ValueError as err:
                output.set_value(idx, 'Error Message(s)', 'Incorrect Value Type: {}'.format(err))
                output.loc[idx, 'Status'] = 'Error'
            else:
                output.loc[idx, 'Status'] = 'Success'

        return output

    def dynamic_import(self, file_type: str) -> importlib.types.ModuleType:
          """Convenience function to bind path with select import type."""
          return importlib.import_module(
              'FileValidator.{}.type'.format(file_type))

    def pop_nan(self, dct):
          """Given dict, return dict with keys popped where isnan(val)."""
          res = dict(dct)
          nans = valfilter(
              lambda x: (
                  x is None or str(x).strip() == '' or
                  (isinstance(x, (Decimal, float)) and isnan(x))), res)
          return dissoc(res, *nans.keys())

    def variableize(self, x: str, max_length: int=64) -> str:
           """Converts a user defined string into a valid variable format."""
           VALID_CHARS = ascii_letters + digits + '_'
           chars = '_'
           if x and x[0] not in digits: chars = ''
           replaced_spaces = x.replace(' ','_')
           chars += ''.join([char for char in replaced_spaces
                             if char in VALID_CHARS])[:max_length]
           return chars.lower()

    def validation(self, row):
          cleaned_row = self.pop_nan(row)
          cleaned_row = keymap(self.variableize, cleaned_row)
          return self.module.Validate(**cleaned_row)
