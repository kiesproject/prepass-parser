import email.utils as eut
import io
import json
import re
import datetime
from collections import OrderedDict
import pytz
import requests
import unicodedata
import csv

genre_data = json.load(open("genre_data.json", "r"))

def parse_date(text):
    return datetime.datetime(*eut.parsedate(text)[:6])


def load_data(url, exclude):
    r = requests.get(url)

    update = parse_date(r.headers["Last-Modified"])
    update = pytz.timezone('UTC').localize(update)
    update = update.astimezone(pytz.timezone('Asia/Tokyo'))

    # 文字エンコーディングの変更
    r.encoding = r.apparent_encoding

    text = re.sub(exclude, "", r.text)

    # 全角英数字を半角英数字に変換して読み込み
    reader = csv.DictReader(io.StringIO(unicodedata.normalize("NFKC", text)))
    next(reader)

    return reader, update


def generate_genres(genre_list):
    if 'その他' in genre_list:
        genre_list.remove('その他')

    genres = []
    for i in genre_list:
        for big_genre in genre_data:
            if i in genre_data[big_genre]:
                genres.append(OrderedDict(
                    {
                        "big_genre": big_genre,
                        "genre": i
                    }
                ))
                break
    return genres


def load_prepass_data(base_url):
    prepass, update = load_data(base_url + "csv/openData_prepass.csv", r'プレミアム・パスポート　事業協賛店一覧,,\d{8} \n')
    baby, _ = load_data(base_url + "csv/openData_baby.csv", r'「赤ちゃんの駅」　登録施設一覧,,\d{8} \n')

    last_update_json = open('last-update.json', 'w')
    last_update_json.write(json.dumps({'prepass': update.strftime("%Y-%m-%dT%H:%M:%S%z")}, ensure_ascii=False, indent=2))
    last_update_json.close()

    baby_ids = [[int(i["企業ID"].replace("co", "")), int(i["店舗ID"].replace("ofid", ""))] for i in baby]

    data_list = []
    for row in prepass:
        data = OrderedDict()
        data["company_id"] = int(row["企業ID"].replace("co", ""))
        data["shop_id"] = int(row["店舗ID"].replace("ofid", ""))
        data["shop_name"] = row["店舗・施設名"]
        data["zip_code"] = row["郵便"]
        data["address"] = row["住所"]
        data["building_address"] = row["住所建物"]

        lat = float(row["緯度"])
        lon = float(row["経度"])

        # 金沢アピタの"CABINE（キャビーヌ）"の位置情報がおかしい
        if data["company_id"] == 267607:
            lat = 36.5595173
            lon = 136.6425032

        # "フィットネスガレージななお"の緯度経度が逆
        if data["company_id"] == 101474:
            lat = float(row["経度"])
            lon = float(row["緯度"])

        data["location"] = OrderedDict((('lat', lat), ('lon', lon)))

        data["tel"] = row["電話"]
        data["fax"] = row["FAX"]
        data["url"] = row["URL"]
        data["open_time"] = row["営業・利用可能時間"]
        data["close_time"] = row["定休日"]
        data["pr_message"] = row["お店PR"]
        data["genres"] = generate_genres(list(set(row["ジャンル"].split(","))))

        data["is_baby_station"] = [data["company_id"], data["shop_id"]] in baby_ids
        data["is_feed_space"] = row["授乳スペース"] != ""
        data["is_change_diaper_space"] = row["オムツ替えスペース"] != ""
        data["is_microwave_oven"] = row["電子レンジ"] != ""
        data["can_buy_wet_tissues"] = row["おむつ又はおしりふきシートの設置(販売)"] != ""
        data["is_boil_water"] = row["粉ミルク用のお湯提供"] != ""
        data["is_child_toilet"] = row["子ども用トイレ・ベビーキーパー"] != ""
        data["is_kids_corner"] = row["キッズコーナー"] != ""
        data["is_lent_stroller"] = row["ベビーカーの貸し出し"] != ""
        data["is_child_privilege"] = row["子ども特典"] != ""
        data["is_child_menu"] = row["子どもメニュー"] != ""
        data["is_no_smoking_room"] = row["禁煙席"] != ""
        data["is_private_room"] = row["個室"] != ""
        data["is_zashiki"] = row["小上がり(お座敷)"] != ""

        data["antiallergic_support"] = row["アレルギー対応"]

        data["privileges"] = OrderedDict(
            (
                ('two_children', row["プレパス特典内容(3子) "]),
                ('three_children', row["プレパス特典内容(2子)"])
            )
        )

        data["last_update"] = update.strftime("%Y-%m-%dT%H:%M:%S%z")

        data_list.append(data)
    return data_list
