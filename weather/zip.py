import urllib.request
import json
import yaml

class ConfirmZip():

    def __init__(self):
        
        # read yaml
        with open('application.yaml', 'rt') as fp:
            text = fp.read()
        data = yaml.safe_load(text)
        self.crient_id = data['api']['yahoo']['client_id']
        self.base_url = data['api']['yahoo']['zip_url']

    
    # return 郵便番号検索API
    def return_zipresult_all(self, zipCode):
        
        zipcode_url = '%squery=%s&appid=%s&output=json' % (self.base_url , zipCode, self.crient_id)
        response = urllib.request.urlopen(zipcode_url).read()
        data_json = json.loads(response.decode('utf-8'))
        
#        print(data_json)
        return data_json
    
    # あとでjsonの内容をbeanにつめようかな。一旦仮で 緯度経度/都市名取得
    def return_zip_tmp(self, zipCode):
        json_str = self.return_zipresult_all(zipCode)
        
        coordinates = json_str['Feature'][0]['Geometry']['Coordinates']
        point_name = json_str['Feature'][0]['Property']['Address']
        
        return [coordinates, point_name]