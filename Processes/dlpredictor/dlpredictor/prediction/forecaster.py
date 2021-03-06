from dlpredictor.log import *
import dlpredictor.prediction.ims_predictor_util as ims_predictor_util
import dlpredictor.prediction.lr_predictor as lr_predictor
from dlpredictor.util.sparkesutil import *

from imscommon.model.ucday import UCDay
from imscommon.model.ucday_hourly import UCDay_Hourly
import tensorflow as tf
from predictor_dl_model.trainer.client_rest import predict
import math


class Forecaster:

    def __init__(self, cfg):
        self.holiday_list = cfg['holiday_list']
        self.cfg = cfg

    def dl_forecast(self, serving_url, model_stats, ucdoc, ucday_list):

        records_hour_price_map = {}
        day_list = []
        train_window = model_stats['model']['train_window']
        predict_window = model_stats['model']['predict_window']

        # ucday_list is sorted from past to present [2018-01-01, 2018-01-02, ...]
        empthy_list = []
        if len(ucday_list) >= train_window:
            ucday_list = ucday_list[len(ucday_list)-train_window:]
        else:
            empthy_list = [0 for _ in range(0, train_window-len(ucday_list))]
        for ucday in ucday_list:
            day_list.append(ucday.date)
            for hour in range(24):
                for price_cat in range(4):
                    key = (hour, price_cat)
                    if key not in records_hour_price_map:
                        records_hour_price_map[key] = empthy_list[:]
                    records_hour_price_map[key].append(
                        ucday.hours[hour].histogram_value(price_cat))

        records_hour_price_list = []
        for key, value in records_hour_price_map.items():
            records_hour_price_list.append((value, key[0], key[1]))
 
        # URL = "http://10.193.217.105:8501/v1/models/faezeh:predict"
        response = predict(serving_url, model_stats=model_stats, day_list=day_list, uckey=ucdoc.uckey, age=ucdoc.a, si=ucdoc.si, network=ucdoc.t, gender=ucdoc.g,
                           media=ucdoc.m, ip_location=ucdoc.ipl, records_hour_price_list=records_hour_price_list)
 
        ucdayMap = {}
        date = day_list[-1]
        prediction_records = response['predictions']
        i = -1
        for _ in range(predict_window):
            i += 1
            date = ims_predictor_util.get_next_date(date)
            ucday = UCDay(date)
            j = -1
            for _, hour, price_cat in records_hour_price_list:
                j += 1
                count = prediction_records[j][i]
                if math.isnan(count):
                    count = 0
                if price_cat == 0:
                    ucday.hours[hour].h0 = count
                elif price_cat == 1:
                    ucday.hours[hour].h1 = count
                if price_cat == 2:
                    ucday.hours[hour].h2 = count
                if price_cat == 3:
                    ucday.hours[hour].h3 = count
            ucdayMap[date] = ucday.hours

        return ucdayMap