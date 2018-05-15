import pymongo

MONGO_URL = 'localhost'
MONGO_DB = 'toutiao'

coon = pymongo.MongoClient(MONGO_URL, connect=False)
db = coon[MONGO_DB]


def save_to_mongodb(table, data):
    """
    存储数据到mongodb
    :param table: 存储数据的表名
    :param data: 字典类型的数据
    """
    if data:
        if db[table].find(data):
            print('数据已存在', data)
            return False
        else:
            db[table].insert(data)
            print('插入数据库成功', data)
            return True
    else:
        print('数据为空')
        return False

