# requires pyton3.4+
import elasticsearch, html

DB = 'http://es-master.ipricegroup.com:9200'  # PROD
# DB = 'http://52.220.14.61:9200' # QA

PAGES = ["may-anh/phu-kien/pin", "dien-thoai-may-tinh-bang/phu-kien/tai-nghe-bluetooth"]

# PAGES = ["tin-hoc/laptop/ultrabook","tin-hoc/may-in","tin-hoc/phan-cung","tin-hoc/may-tinh-ban","tin-hoc/phan-mem/diet-virus","tin-hoc/phu-kien/ban-phim","tin-hoc/phu-kien/day-cap/hdmi","may-anh/phu-kien/day-deo","may-anh/the-nho","tv-video-dvd/dau-dvd"]

# PAGES = ["diem-danh-5-mau-ao-bong-da-dep-nhat-ngoai-hang-anh","nguoi-dung-dong-nam-a-tan-huong-cyber-monday-nhu-the-nao","don-loc-cuoi-nam-voi-10-coupons-may-man-tuan-7122015","4-ly-do-ban-khong-the-bo-qua-dai-tiec-sinh-nhat-lazada","me-man-phong-cach-toi-gian-day-bien-hoa-cua-quy-co-van-nguoi-me-ha-vy","truy-cap-iprice-nhan-ngay-10-coupons-hap-dan-tuan-14122015","axtro-sports-chinh-thuc-tham-gia-iprice","hoa-trang-halloween-dep-nhu-sao-don-gian-hon-ban-nghi","4-tuyet-chieu-nang-tam-phong-cach-cho-chang-trai-cong-so","giai-dap-nhung-hieu-lam-thuong-gap-cua-phu-nu-ve-ung-thu-vu","10-mon-hang-hieu-gia-re-cho-tin-do-cong-nghe-tai-cach-mang-mua-sam-truc-tuyen","10-mon-do-gia-dung-thong-minh-tai-cach-mang-mua-sam-lazada","tha-ga-mua-sam-don-loc-dau-nam-cung-sieuthibepnhapkhauvn","mua-sam-tha-ga-voi-10-uu-dai-lon-tuan-21122015","nhung-website-khong-the-bo-qua-cho-nguoi-yeu-lam-vuon","bung-no-cach-mang-tieu-dung-thoi-dai-so-tai-iprice","demomo2u-an-so-moi-tren-iprice","mach-ban-6-mon-qua-y-nghia-tang-thay-co-nhan-ngay-20-thang-11","diem-danh-7-coupons-khong-the-bo-qua-tuan-30112015","bat-mi-bi-quyet-cham-soc-da-mua-giam-can","goi-y-trang-diem-halloween-lac-vao-xu-so-than-tien-cung-meo-chashire","tung-bung-mua-sam-cuoi-nam-voi-nhieu-uu-dai-tuan-28122015","yesasia-da-co-mat-tai-iprice","tong-hop-cac-san-pham-noi-bat-tai-cach-mang-mua-sam-truc-tuyen-lazada","rang-ro-chao-8-thang-3-lan-da-can-gi","chon-noi-y-theo-dang-nguc-bi-mat-cua-su-quyen-ru","nhan-ngay-li-xi-voi-nhieu-coupons-uu-dai-tuan-412016","goi-y-trang-diem-halloween-noi-loan-gothic-cung-michelle-phan","10-san-pham-duong-da-khong-the-thieu-cho-mua-dong-tu-cach-mang-mua-sam-truc-tuyen","san-uu-dai-len-den-60-cung-coupons-tuan-11012016","nikon","nestle","skinfood","the-body-shop","nokia","armani","jimmy-choo","canon","thefaceshop","nha-cua-gia-dung/den","tui/tui-vi","dien-may/am-thanh/may-nghe-nhac-mp3","dien-may/tv-video/dvd","dien-may/choi-game","dien-may/may-vi-tinh-laptops/laptops","dien-may/am-thanh/loa-di-dong/loa-bluetooth","dien-may/may-vi-tinh-laptops/may-in","dien-may/am-thanh/tai-nghe","dien-may/may-vi-tinh-laptops/may-tinh-ban","dien-may/may-anh/phu-kien/pin","dien-may/choi-game/may-choi-game-playstation","dien-may/may-vi-tinh-laptops/phan-cung","dien-may/dien-thoai-may-tinh-bang/phu-kien/tai-nghe-bluetooth","dien-may/may-vi-tinh-laptops/hop-so-mang/router-wifi","dien-may/may-vi-tinh-laptops/bo-luu-tru-ngoai/the-nho","dien-may/am-thanh/dan-am-thanh-hi-fi/loa","dien-may/may-vi-tinh-laptops/laptops/ultrabook","dien-may/may-vi-tinh-laptops/phan-cung/bo-nho-trong","dien-may/am-thanh/dan-am-thanh-hi-fi/ampli","dien-may/dien-thoai-may-tinh-bang/dong-ho-thong-minh","dien-may/dien-thoai-may-tinh-bang/dien-thoai-thong-minh/dien-thoai-blackberry","giay-dep/giay-de-bang","quan-ao/the-thao","quan-ao/phu-kien/gang-tay","tre-em-do-choi/do-choi","quan-ao/do-boi/quan-boi-nam","dien-may/may-vi-tinh-laptops/phu-kien/day-cap/cap-hdmi","dien-may/am-thanh/loa-di-dong","dien-may/may-anh/phu-kien/tui-dung-may-anh","dien-may/may-anh/camera-hanh-trinh","dien-may/may-anh/phu-kien/the-nho","dien-may/dien-thoai-may-tinh-bang/phu-kien/pin","suc-khoe-lam-dep/dung-cu-cao-rau/may-cao-rau","dien-may/may-anh/camera-ip-giam-sat/may-anh-khong-guong-lat","dien-may/may-anh/phu-kien/day-deo-may-anh","dien-may/dien-thoai-may-tinh-bang/dien-thoai-thong-minh/dien-thoai-android","dien-may/may-vi-tinh-laptops/laptops/netbook","dien-may/may-vi-tinh-laptops/phan-mem/diet-virus"]

ES = elasticsearch.Elasticsearch(DB, verify_certs=False)


def download(page):
    query = {
        "query": {
            "term": {
                "url": page
            }
        }
    }

    res = ES.search(index="content_vn", body=query)

    return (res['hits']['hits'][0]['_id'], res['hits']['hits'][0]['_type'], res['hits']['hits'][0]['_source']['text'])


def update(id, doctype, fixed):
    query = {
        "doc": {
            "text": fixed,
            "draft": {
                "text": fixed
            }
        }
    }

    res = ES.update(index="content_vn", doc_type=doctype, id=id, body=query)
    print(res)


def fix(text):
    # load file and unescape 
    # with open(page + "-broken.html") as file:
    text = html.unescape(text)
    # text = text.replace(r'\"', '"')
    # text = text.replace(r'\r\n', '')
    # text = text.replace(r'\n', '')

    # save to temporary file
    with open("temp.tmp", "w") as file:
        file.write(text)

    # open as binary
    with open("temp.tmp", "rb") as file:
        binary = file.read()

    # do magic
    REPLACE = {
        b'\xc3\x84\xc6\x92': b'\xc4\x83',
        b'\xc3\x84\xe2\x80\x98': b'\xc4\x91',

        b'\xc3\x84\xc2\x90': b'\xc4\x90',
        b'\xc3\x84\xc2\xa9': b'\xc4\xa9',
        b'\xc3\x85\xc2\xa9': b'\xc5\xa9',
        b'\xc3\x85\xc2\x8d': b'\xc5\x8d',
        b'\xc3\x86\xc2\xa1': b'\xc6\xa1',
        b'\xc3\x86\xc2\xb0': b'\xc6\xb0',
        b'\xc3\x8c\xc2\x81': b'\xcc\x81',
        b'\xc3\x8c\xc2\xa3': b'\xcc\xa3',
        b'\xc3\x8c\xc6\x92': b'\xcc\x83',
        b'\xc3\x8c\xe2\x82\xac': b'\xcc\x80',
        b'\xc3\x8c\xe2\x80\xb0': b'\xcc\x89',

        b'\xc3\xa1\xc2\xba\xc2\xa1': b'\xe1\xba\xa1',
        b'\xc3\xa1\xc2\xba\xc2\xa2': b'\xe1\xba\xa2',
        b'\xc3\xa1\xc2\xba\xc2\xa3': b'\xe1\xba\xa3',
        b'\xc3\xa1\xc2\xba\xc2\xa5': b'\xe1\xba\xa5',
        b'\xc3\xa1\xc2\xba\xc2\xa7': b'\xe1\xba\xa7',
        b'\xc3\xa1\xc2\xba\xc2\xa9': b'\xe1\xba\xa9',
        b'\xc3\xa1\xc2\xba\xc2\xab': b'\xe1\xba\xab',
        b'\xc3\xa1\xc2\xba\xc2\xad': b'\xe1\xba\xad',
        b'\xc3\xa1\xc2\xba\xc2\xaf': b'\xe1\xba\xaf',
        b'\xc3\xa1\xc2\xba\xc2\xb1': b'\xe1\xba\xb1',
        b'\xc3\xa1\xc2\xba\xc2\xb3': b'\xe1\xba\xb3',
        b'\xc3\xa1\xc2\xba\xc2\xb7': b'\xe1\xba\xb7',
        b'\xc3\xa1\xc2\xba\xc2\xb9': b'\xe1\xba\xb9',
        b'\xc3\xa1\xc2\xba\xc2\xbb': b'\xe1\xba\xbb',
        b'\xc3\xa1\xc2\xba\xc2\xbd': b'\xe1\xba\xbd',
        b'\xc3\xa1\xc2\xba\xc2\xbf': b'\xe1\xba\xbf',

        b'\xc3\xa1\xc2\xbb\xc2\x81': b'\xe1\xbb\x81',
        b'\xc3\xa1\xc2\xbb\xc2\x8d': b'\xe1\xbb\x8d',
        b'\xc3\xa1\xc2\xbb\xc2\x8f': b'\xe1\xbb\x8f',
        b'\xc3\xa1\xc2\xbb\xc2\x90': b'\xe1\xbb\x90',
        b'\xc3\xa1\xc2\xbb\xc2\x9d': b'\xe1\xbb\x9d',
        b'\xc3\xa1\xc2\xbb\xc2\xa1': b'\xe1\xbb\xa1',
        b'\xc3\xa1\xc2\xbb\xc2\xa3': b'\xe1\xbb\xa3',
        b'\xc3\xa1\xc2\xbb\xc2\xa5': b'\xe1\xbb\xa5',
        b'\xc3\xa1\xc2\xbb\xc2\xa7': b'\xe1\xbb\xa7',
        b'\xc3\xa1\xc2\xbb\xc2\xa9': b'\xe1\xbb\xa9',
        b'\xc3\xa1\xc2\xbb\xc2\xab': b'\xe1\xbb\xab',
        b'\xc3\xa1\xc2\xbb\xc2\xad': b'\xe1\xbb\xad',
        b'\xc3\xa1\xc2\xbb\xc2\xaf': b'\xe1\xbb\xaf',
        b'\xc3\xa1\xc2\xbb\xc2\xb1': b'\xe1\xbb\xb1',
        b']xc3\xa1\xc2\xbb\xc2\xb3': b'\xe1\xbb\xb3',
        b'\xc3\xa1\xc2\xbb\xc2\xb7': b'\xe1\xbb\xb7',
        b'\xc3\xa1\xc2\xbb\xc2\xb9': b'\xe1\xbb\xb9',

        b'\xc3\xa1\xc2\xbb\xc5\xb8': b'\xe1\xbb\x9f',
        b'\xc3\xa1\xc2\xbb\xc6\x92': b'\xe1\xbb\x83',

        b'\xc3\xa1\xc2\xbb\xe2\x80\x94': b'\xe1\xbb\x97',
        b'\xc3\xa1\xc2\xbb\xe2\x80\x98': b'\xe1\xbb\x91',
        b'\xc3\xa1\xc2\xbb\xe2\x80\x9c': b'\xe1\xbb\x93',
        b'\xc3\xa1\xc2\xbb\xe2\x80\x9d': b'\xe1\xbb\x94',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xa0': b'\xe1\xbb\x86',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xa2': b'\xe1\xbb\x95',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xa6': b'\xe1\xbb\x85',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xb9': b'\xe1\xbb\x8b',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xb0': b'\xe1\xbb\x89',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xba': b'\xe1\xbb\x9b',
        b'\xc3\xa1\xc2\xbb\xe2\x80\xa1': b'\xe1\xbb\x87',
        b'\xc3\xa1\xc2\xbb\xe2\x82\xac': b'\xe1\xbb\x80',
        b'\xc3\xa1\xc2\xbb\xe2\x84\xa2': b'\xe1\xbb\x99',

        b'\xc3\xaa\xc3\x8c\xc6\x92': b'\xc3\xaa\xcc\x83',
        b'\xc3\xa2\xc3\x8c\xc6\x92': b'\xc3\xa2\xcc\x83',
    }

    for key, value in REPLACE.items():
        binary = binary.replace(key, value)

    # save to temporary file
    with open("temp.tmp", "wb") as file:
        file.write(binary)

    # open as text
    with open("temp.tmp", "r") as file:
        fixed = file.read()

    return fixed


def save(binary):
    with open(page + "-fixed.html", "wb") as file:
        file.write(bytearray("<html><head><meta charset='utf8'/></head><body>", "utf8"))
        file.write(binary)
        file.write(bytearray("</body></html>", "utf8"))


def main():
    for page in PAGES:
        id, doctype, text = download(page)
        fixed = fix(text)
        update(id, doctype, fixed)


if __name__ == '__main__':
    main()
