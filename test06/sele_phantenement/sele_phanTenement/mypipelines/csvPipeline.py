import os
import pandas as pd
from sele_phanTenement.settings import BASE_PATH


class MyTenementPipelines(object):

    def process_item(self, item, spider):
        dataframe = pd.DataFrame.from_dict(item, orient='index').T
        dataframe.to_csv('{}.csv'.format(os.path.join(BASE_PATH, item['name'])), mode='a', header=False, index=False)
