import os
import pandas as pd

this_dir = os.path.dirname(os.path.realpath(__file__))


class SampleFactory:
    _dfs = {}

    @classmethod
    def get_sample(cls, name) -> pd.DataFrame:
        if name not in cls._dfs:
            cls._dfs[name] = pd.read_hdf(os.path.join(this_dir, "%s.h5" % name))
        return cls._dfs[name]
