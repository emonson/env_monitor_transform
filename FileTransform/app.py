import importlib

class TheTransformer(object):
    def __init__(self,
                 dataframe,
                 file_type: str):
        self.module = self.dynamic_import(file_type)
        self.dataframe = dataframe

    def main(self):
        # output dataframe must be created here
        try:
            # NOTE: This might not be right... May need to store directory path in this
            #   object and just send that to the Transform() method...
            self.module.Transform(**self.dataframe)
        except ValueError as err:
            print('Error Message(s)', 'Incorrect Value Type: {}'.format(err))
        else:
            print('Success')

        return output

    def dynamic_import(self, file_type: str) -> importlib.types.ModuleType:
          """Convenience function to bind path with select import type."""
          return importlib.import_module(
              'FileValidator.{}.type'.format(file_type))
