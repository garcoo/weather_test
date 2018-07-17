import urllib.request
import json
import yaml
import mysql.connector

class ConfirmWeather():

    def __init__(self):

                # read yaml
        with open('application.yaml', 'rt') as fp:
            text = fp.read()
        data = yaml.safe_load(text)
        self.crient_id = data['api']['yahoo']['client_id']
        self.base_url = data['api']['yahoo']['weather_url']

        # db connect info
        self.db_con = data['datasource']

    # return お天気API
    def return_send_done_report(self):
                # con db
        con = mysql.connector.connect(
            host=self.db_con['host'],
            db=self.db_con['db'],
            user=self.db_con['user'],
            passwd=self.db_con['password']
        )
        cur = con.cursor(dictionary=True)

        # 通知対象を全て取得
        cur.execute(
            "select"
            +"   mcr.room_id"
            +"    ,wrr.zip_cd"
            +"    ,twi.send_rain_lv"
            +"    ,twi.rain_lv_now"
            +"    ,twi.rain_lv_10"
            +" from"
            +"    m_chat_room mcr"
            +"    inner join m_weather_report_room wrr"
            +"    on mcr.room_id = wrr.room_id"
            +"    inner join t_weather_info twi"
            +"    on wrr.zip_cd = twi.zip_cd"
            +" where"
            +"    mcr.activ_flg = 1;"
                )
        all_row = cur.fetchall()

        # 切断
        cur.close()
        con.close()

        return all_row


    # return お天気API
    def return_weather(self, coordinates):

        get_weather_url = '%scoordinates=%s&appid=%s&output=json' % (self.base_url, coordinates, self.crient_id)
        response = urllib.request.urlopen(get_weather_url).read()
        data_json = json.loads(response.decode('utf-8'))

        return data_json


    # 雨レベルを取得
    def return_rain_lv_kbn(self, rainfall):

          HARE_KUMORI = '00'
          PARAPARA = '01'
          HONKAKUTEKI = '02'
          TUYOME = '03'
          DOSYABURI = '04'
          TAKINOYOU = '05'
          KIROKUTEKI = '06'

          if (rainfall == 0.0):
              return HARE_KUMORI
          elif (rainfall < 3.0):
              return PARAPARA
          elif (rainfall < 5.0):
              return HONKAKUTEKI
          elif (rainfall < 10.0):
              return TUYOME
          elif (rainfall < 30.0):
              return DOSYABURI
          elif (rainfall < 80.0):
              return TAKINOYOU
          elif (rainfall >= 80.0):
              return KIROKUTEKI

    def return_rainfall(self, coordinates):

        data_json = self.return_weather(coordinates)

        weather_info = data_json['Feature'][0]['Property']['WeatherList']['Weather']
        base_minutes = 10

        weather_word = ""
        for index, var in enumerate(weather_info):
              info = self.retrun_rain_level(var['Rainfall'])

              if index == 0:
                  before_words = "今(" + var['Date'][8:10] + "時" + var['Date'][10:12] + "分時点)、"
                  if var['Rainfall'] == 0.0:
                      after_words = "っていないんだな"
                  else:
                      after_words = "っているよ"
              elif (index == 1 or index == 2 or index == 4 or index == 5):
                  base_minutes += 10
                  continue

              else:
                  if index == 6:
                      before_words = '1時間後、'
                  else:
                      before_words = '%s分後、' % (base_minutes)

                  if var['Rainfall'] == 0.0:
                      after_words = "らないんじゃないかと思うんだな"
                  else:
                      after_words = "るんじゃないかと思うんだな"
                  base_minutes += 10

              weather_word += before_words + info + after_words + "\n"

        return weather_word


    def return_rainreport(self, weather_rep, rain_flg):
        msg = ''

        if rain_flg == 0:
            msg = '雨が上がったよ\nこの後の天気の変化に気をつけてねー\n'
        else:
            msg = '雨雲が近づいて来てるよ\n傘は持ってるかな？\n'
        msg += '\n'
        msg += '---むこう1時間の天気予報---\n'

        base_minutes = 0

        for index, var in enumerate(weather_rep):
              info = self.retrun_rain_level(var['Rainfall'])

              if (index == 0 or index == 2 or index == 4 or index == 5):
                  base_minutes += 10
                  continue
              else:
                  if index == 6:
                      before_words = '1時間後、'
                  else:
                      before_words = '%s分後、' % (base_minutes)

                  if var['Rainfall'] == 0.0:
                      after_words = "らない予報なんだな"
                  else:
                      after_words = "るんじゃないかと思うんだな"
                  base_minutes += 10

              msg += before_words + info + after_words + "\n"

        return msg


    def update_t_weather_info(self, weather_rep, zip_cd, send_rain_lv):

        con = mysql.connector.connect(
            host=self.db_con['host'],
            db=self.db_con['db'],
            user=self.db_con['user'],
            passwd=self.db_con['password']
        )
        cur = con.cursor(dictionary=True)

        # 通知対象を全て取得
        cur.execute(
            "update t_weather_info "
            +"set rain_lv_now = '" + self.return_rain_lv_kbn(weather_rep[0]['Rainfall']) + "'"
            +"    ,rain_lv_10 = '" + self.return_rain_lv_kbn(weather_rep[1]['Rainfall']) + "'"
            +"    ,rain_lv_30 = '" + self.return_rain_lv_kbn(weather_rep[3]['Rainfall']) + "'"
            +"    ,rain_lv_60 = '" + self.return_rain_lv_kbn(weather_rep[6]['Rainfall']) + "'"
            +"    ,send_rain_lv = '" + send_rain_lv + "'"
            +"    ,sys_version = sys_version +1"
            +"    ,sys_upd_date = now()"
            +" where"
            +"    zip_cd = '" + zip_cd + "'"
                )
        # 切断
        cur.close()
        con.commit()
        con.close()

        return


    def retrun_rain_level(self, rainfall):
          if (rainfall == 0.0):
              rain_level = "雨は降"
          elif (rainfall < 3.0):
              rain_level = "傘がいるかどうか微妙な雨が降"
          elif (rainfall < 5.0):
              rain_level = "本格的に雨が降"
          elif (rainfall < 10.0):
              rain_level = "結構強めに雨が降"
          elif (rainfall < 20.0):
              rain_level = "やや強い雨がザーザーと降"
          elif (rainfall < 30.0):
              rain_level = "土砂降りで、傘をさしていてもぬれる雨が降"
          elif (rainfall < 50.0):
              rain_level = "マジで激しい雨が降"
          elif (rainfall < 80.0):
              rain_level = "滝のように非常に激しい雨が降"
          elif (rainfall >= 80.0):
              rain_level = "記録に残るような豪雨にな"
          return rain_level

    def return_day_weather(self, area_cd):
        # 天気取得
        #area_cd_saitama = '110010'
        area_cd_kanagawa = '140010'
        get_weather_url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=%s&output=json' % (area_cd_kanagawa)

        response = urllib.request.urlopen(get_weather_url).read()
        data_json = json.loads(response.decode('utf-8'))

        max_temperature = ""
        min_temperature = ""
        date = data_json['forecasts'][0]['date']
        weather = data_json['forecasts'][0]['telop']
        try:
            max_temperature = data_json['forecasts'][0]['temperature']['max']['celsius']
        except TypeError:
            pass
        try:
            min_temperature = data_json['forecasts'][0]['temperature']['min']['celsius']
        except TypeError:
            pass

        date_str = date[0:4] + "年" + date[5:7] + "月" + date[8:10] + "日の天気は"
        masg = date_str + weather + "なんだな"
        if max_temperature != "":
            masg += "\n最高気温が" + max_temperature + "℃なんだな"
        if min_temperature != "":
            masg += "\n最低気温が" + min_temperature + "℃なんだな"
        masg += "\nちなみに、明日は" + data_json['forecasts'][1]['telop'] + "なんだな"

        return masg

    # pattern check
    # 0 day
    # 1 real
 #   def invok_cont(self, pattern_kbn):
 #       if pattern_kbn == 0:
 #           # 毎日のお天気は朝の8時だけ実行するよ
 #           if(datetime.now().hour == 8):
 #               return 1
 #       elif pattern_kbn == 1:
            # 天気の情報が変わる時だけ
