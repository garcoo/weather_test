from weather import ConfirmWeather
from zip import ConfirmZip
from chatwork import ControlChatwork


weather_class = ConfirmWeather()
zip_class = ConfirmZip()
chat_class = ControlChatwork()

# 速報対象のエリアと通知済みの天候状況を取得
weather_info = weather_class.return_send_done_report()

for index, db_result in enumerate(weather_info):

    # 住所情報を取得
    zip_info = zip_class.return_zip_tmp(db_result['zip_cd'])
    # お天気取得
    wether_api = weather_class.return_weather(zip_info[0])
    weather_rep = wether_api['Feature'][0]['Property']['WeatherList']['Weather']

    # 今と10分後の雨Lv
    rain_info_u10 = [
        weather_class.return_rain_lv_kbn(weather_rep[0]['Rainfall'])
        ,weather_class.return_rain_lv_kbn(weather_rep[1]['Rainfall'])
    ]


    imano_ame_lv = ''
    if rain_info_u10[0] == '00' and rain_info_u10[1] == '00':
        imano_ame_lv = '00'
    elif (rain_info_u10[0] != '00'):
        imano_ame_lv = rain_info_u10[0]
    elif (rain_info_u10[1] != '00'):
        imano_ame_lv = rain_info_u10[1]

    # date
    date = weather_rep[0]['Date'][0:4] + "/" + weather_rep[0]['Date'][4:6] + "/" + weather_rep[0]['Date'][6:8] + " " + weather_rep[0]['Date'][8:10] + "時" + weather_rep[0]['Date'][10:12] + "分時点"

    print(db_result['send_rain_lv'])
    print(imano_ame_lv)
    if db_result['send_rain_lv'] == '00':
        # 降ってなかった場合
        if imano_ame_lv == '00':
            # 通知状態 = 今の状態の場合は処理しない
            continue
        else:
            # 降ってる
            msg = weather_class.return_rainreport(weather_rep, 1)
            chat_class.talk(db_result['room_id'],
                "[info][title]☂️雨雲が近づいてきたよ:o  (" + date + ")[/title]" + "「" + zip_info[1] + "」のお天気速報ーʕ◔ϖ◔ʔ\n" + msg +"[/info]")
            weather_class.update_t_weather_info(weather_rep, db_result['zip_cd'],imano_ame_lv)
            continue
    else:
        # 降ってた場合
        if imano_ame_lv == '00':
            # 通知状態 = 今の状態の場合は処理しない

            msg = weather_class.return_rainreport(weather_rep, 0)
            chat_class.talk(db_result['room_id'],
                "[info][title]☀︎雨があがったよ(F)  (" + date + ")[/title]" + "「" + zip_info[1] + "」のお天気速報ーʕ◔ϖ◔ʔ\n" + msg +"[/info]")
            weather_class.update_t_weather_info(weather_rep, db_result['zip_cd'],imano_ame_lv)
            continue
        else:
            # 降ってる
            continue




#print("「" + zip_info[1] + "」のお天気なう")
#print(wether_now)

# chatworkのルームに投稿

#chat_class = ControlChatwork()
#chat_class.talk(room_id,
#                "【☀︎goemonのお天気なう ʕ◔ϖ◔ʔ】\n" + "「" + zip_info[1] + "」の天気は\n" + wether_now)
