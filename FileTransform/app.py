import importlib

class TheTransformer(object):
    def __init__(self,
                 file_path,
                 file_type: str):
        self.module = self.dynamic_import(file_type)
        self.file_path = file_path

    def main(self):
        # output dataframe must be created here
        try:
            self.module.Transform(**self.file_path)
        except ValueError as err:
            print('Error Message(s)', 'Incorrect Value Type: {}'.format(err))
        else:
            print('Success')

        return output

    def dynamic_import(self, file_type: str) -> importlib.types.ModuleType:
          """Convenience function to bind path with select import type."""
          return importlib.import_module(
              'FileValidator.{}.type'.format(file_type))
