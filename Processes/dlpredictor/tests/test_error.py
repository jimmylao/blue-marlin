from imscommon.es.ims_esclient import ESClient
from pyspark import SparkContext, SparkConf, Row
from pyspark.sql.functions import concat_ws, count, lit, col, udf, expr, collect_list
from pyspark.sql import HiveContext
from pyspark.sql.types import IntegerType, StringType
import math

# read es
es_host = '10.193.217.111'
es_port = '9200'
es_index = 'predictions_02052020'
es_type = 'doc'
es = ESClient(es_host, es_port, es_index, es_type)
hits = es.search({"size": 1000})

es_records = {}
for ucdoc in hits:
    uckey = ucdoc['uckey']
    predictions = ucdoc['ucdoc']['predictions']
    for day, hours in predictions.items():
        hour = -1
        for hour_doc in hours:
            hour += 1
            es_records[(uckey, day, hour, '0')] = hour_doc['h0']
            es_records[(uckey, day, hour, '1')] = hour_doc['h1']
            es_records[(uckey, day, hour, '2')] = hour_doc['h2']
            es_records[(uckey, day, hour, '3')] = hour_doc['h3']

# print(next(iter(es_records.items())))
# print('************')

sc = SparkContext()
hive_context = HiveContext(sc)
sc.setLogLevel('WARN')

# Reading the max bucket_id
bucket_size = 1
bucket_step = 1
factdata = 'factdata3m2'

start_bucket = 0
while True:

    end_bucket = min(bucket_size, start_bucket + bucket_step)

    if start_bucket > end_bucket:
        break

    # Read factdata table
    command = """
        select count_array,day,hour,uckey from {} where bucket_id between {} and {}
        """.format(factdata, str(start_bucket), str(end_bucket))

    command = """
        select * from trainready_tmp
        """

    start_bucket = end_bucket + 1

    df = hive_context.sql(command)
    #df = df.where('day="2018-03-29" or day="2018-03-30" or day="2018-03-31"')

    # statistics
    found_items = 0
    total_error = 0

    # for row in df.collect():
    #     uckey = row['uckey']
    #     day = row['day']
    #     hour = row['hour']
    #     for item in row['count_array']:
    #         parts = item.split(':')
    #         h = parts[0]
    #         count = int(parts[1])
    #         key=(uckey,day,hour,h)
    #         if key in es_records:
    #             # do not count real 0
    #             # if count == 0:
    #             #     continue
    #             found_items+=1
    #             pcount = es_records[key] # predicted count
    #             error = abs(pcount-count)/(count+1)
    #             print('real:{}, predicted:{}, error:{}, uckey:{}, hour:{}, price_cat:{}'.format(count,pcount, error, uckey, hour, h))
    #             total_error += error

    # print('found_items',found_items)
    # print('avg_error',total_error/found_items)

    df_collect = df.collect()
    for row in df_collect:
        uckey = row['uckey']
        uph = row['uph']
        hour = row['hour']
        h = row['price_cat']
        ts_n = row['ts_n']
        days = [('2018-03-29', ts_n[-3]), ('2018-03-30',
                                           ts_n[-2]), ('2018-03-31', ts_n[-1])]

        for day, count in days:
            count = round(math.exp(count)-1)
            key = (uckey, day, hour, h)
            if key in es_records:
                found_items += 1
                pcount = es_records[key]  # predicted count
                error = abs(pcount-count)/(count+1)
                total_error += error
                print('real:{}, predicted:{}, error:{}, uph:{}, hour:{}, price_cat:{}, day:{}'.format(
                    count, pcount, error, uph, hour, h, day))

    print('found_items', found_items)
    print('avg_error', total_error/found_items)
    print('es hits:{},es_records:{},df_collect:{}'.format(
        str(len(hits)), str(len(es_records)), str(len(df_collect))))
