# coding=utf-8
# !/usr/bin/python

import codecs, pandas, json, re, sys
from collections import OrderedDict
from lxml import html
from HTMLParser import HTMLParser

reload(sys)
sys.setdefaultencoding("UTF-8")


# Simple Counts
def character_count(string):
    string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
    return len(string)


def word_count(string):
    string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
    matches = re.findall(r"[\w']+", string)
    return len(matches)


def paragraph_count(dom):
    elements = dom.cssselect("p")
    count = 0
    for e in elements:
        if not (e.text and e.text.strip() == ""):
            count = count + 1
    elements = dom.cssselect("br")
    for e in elements:
        count = count + 1
    return count


def h1_count(string):
    matches = re.findall(r"(</h1>)", string)
    return len(matches)


def h2_count(string):
    matches = re.findall(r"(</h2>)", string)
    return len(matches)


def h3_count(string):
    matches = re.findall(r"(</h3>)", string)
    return len(matches)


def list_count(string):
    matches = re.findall(r"(</ul>)|(</ol>)", string)
    return len(matches)


def table_count(string):
    matches = re.findall(r"(</table>)", string)
    return len(matches)


def image_count(string):
    matches = re.findall(r"(<img)", string)
    return len(matches)


def iframe_count(string):
    matches = re.findall(r"(<iframe)", string)
    return len(matches)


def link_count_internal(dom):
    internal = 0
    elements = dom.cssselect("a[href]")
    for e in elements:
        if 'iprice' in e.get('href') and not "#" in e.get('href'):
            internal = internal + 1

    return internal


def link_count_external(dom):
    external = 0
    elements = dom.cssselect("a[href]")
    for e in elements:
        if not 'iprice' in e.get('href'):
            external = external + 1

    return external


def cc_count(cc, string):
    matches = re.findall(r" (" + cc + r")\b", string, re.I)
    return len(matches)


def country_count(cc, string):
    countries = {
        'id': 'indonesia',
        'hk': 'hong kong',
        'my': 'malaysia',
        'ph': 'philippines',
        'sg': 'singapore',
        'th': 'thailand',
        'vn': 'việt nam'
    }
    matches = re.findall(r"\b(" + countries[cc] + r")\b", string, re.I)
    return len(matches)


def has_title(string):
    return len(string) > 0


def has_heading(string):
    return len(string) > 0


def has_meta(string):
    return len(string) > 0


def has_logo(string):
    return len(string) > 0


def has_reviews(string):
    return len(string) > 0


def has_specs(string):
    return len(string) > 0


def has_news(string):
    return len(string) > 0


def count_images(array):
    return len(array)


def count_redirects(array):
    return len(array)


def int_url_count(array):
    count = 0
    for item in array:
        if len(item) > 0:
            count = count + 1
    return count


# HTML Rules
def single_item_list(dom):
    elements = dom.cssselect("ul, ol")
    broken = 0
    for e in elements:
        sub = e.cssselect("li")
        if len(sub) < 2:
            broken = broken + 1
    return broken


def empty_paragraph(dom):
    elements = dom.cssselect("p")
    broken = 0
    for e in elements:
        if e.text and e.text.strip() == "":
            broken = broken + 1
    return broken


def spaces_at_end(string):
    matches = re.findall(r"(&nbsp;</)|( </)", string)
    return len(matches)


def double_spaces(string):
    string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
    matches = re.findall(r"(&nbsp;&nbsp;)|(  )", string)
    return len(matches)


def missing_table_header(dom):
    elements = dom.cssselect("table")
    broken = 0
    for e in elements:
        sub = e.cssselect("th")
        if len(sub) == 0:
            broken = broken + 1
    return broken


def table_width_height(dom):
    elements = dom.cssselect("table, tr, th, td")
    broken = 0
    for e in elements:
        if (e.attrib and "style" in e.attrib) and ("width" in e.attrib['style'] or "height" in e.attrib['style']):
            broken = broken + 1
    return broken


def image_in_table(dom):
    tables = dom.cssselect("table")
    broken = 0
    for t in tables:
        images = t.cssselect("img")
        for i in images:
            broken = broken + 1
    return broken


def image_not_cdn(dom):
    elements = dom.cssselect("img")
    broken = 0
    for e in elements:
        if "iprice-prod" in e.attrib['src']:
            broken = broken + 1
    return broken


def custom_styles(string):
    count = 0
    matches = re.findall(r"style=(\".*\")", string)
    for match in matches:
        if "padding-left" in match or "center" in match:
            count = count + 1
    return count


def broken_definition_list(dom):
    elements = dom.cssselect("dl")

    broken = 0
    for e in elements:
        dt = len(e.cssselect("dt"))
        dd = len(e.cssselect("dd"))
        if dt != dd:
            broken = broken + 1

    return broken


def bold_not_heading(string):
    matches = re.findall(r"([a-zA-Z0-9]+</strong></p>)", string)
    return len(matches)


def get_field(field, row):
    if field in row['_source']:
        return str(row['_source'][field])
    else:
        return ''


def get_array(field, row):
    if field in row['_source']:
        return row['_source'][field]
    else:
        return ''


def get_nested(field, nested, row):
    array = get_array(field, row)
    if nested in array:
        return str(array[nested])
    else:
        return ''


def calculate_stats(data):
    stats = []
    for row in data:
        topText = get_field('shortText', row)
        leftText = get_field('sideText', row)
        bottomText = get_field('text', row)
        newsText = get_field('news', row)
        reviewsText = get_field('reviews', row)
        totalSearchVolume = get_field('googleSearchVolume', row) + get_field('addedSearchVolume', row)

        if not topText and not bottomText and not leftText and not row['_type'] == 'variant' and (
                totalSearchVolume == '0' or totalSearchVolume == '10'):
            continue

        stat = OrderedDict()
        stat['URL'] = "/" + get_field('url', row) + "/"
        stat['CC'] = row['_index'].split("_")[1]
        stat['Created'] = get_field('created', row)
        stat['Updated'] = get_field('updated', row)

        stat['Brand'] = get_nested('source', 'brand', row)
        stat['Series'] = get_nested('source', 'series', row)
        stat['Model'] = get_nested('source', 'model', row)
        stat['Category'] = get_nested('source', 'category', row)
        stat['Page_Heading'] = stat['Brand'] + ' ' + stat['Category'][stat['Category'].rfind('/') + 1:]

        type = row['_type']
        if type in ['brand', 'category', 'filtered']:
            stat['Product'] = 'Discovery'
            if type == 'filtered':
                subProduct = [
                    'brand' if get_nested('source', 'brand', row) else '',
                    'series' if get_nested('source', 'series', row) else '',
                    'model' if get_nested('source', 'model', row) else '',
                    'category' if get_nested('source', 'category', row) else '',
                    'gender' if get_nested('source', 'gender', row) in ['1', '2'] else ''
                ]
                stat['SubProduct'] = "-".join(filter(None, subProduct))
            else:
                stat['SubProduct'] = type
        elif type in ['variant']:
            stat['Product'] = 'PriceComparison'
            c1 = get_field('source.characteristic.c1', row)
            if c1:
                stat['SubProduct'] = 'variant'
            else:
                stat['SubProduct'] = 'model'

            prefix = {
                "hk": "compare",
                "id": "harga",
                "my": "compare",
                "ph": "compare",
                "sg": "compare",
                "th": "ราคา",
                "vn": "gia-ban"
            }
            stat['URL'] = "/" + prefix[stat['CC']] + stat['URL']
        elif type in ['blog', 'page']:
            stat['Product'] = 'Static'
            stat['SubProduct'] = type
            stat['URL'] = "/blog" + stat['URL']
        elif type in ['store', 'couponCategory']:
            stat['Product'] = 'Coupon'
            stat['SubProduct'] = type
            stat['URL'] = "/coupons" + stat['URL']
        else:
            continue

        stat['SV'] = get_field('googleSearchVolume', row)
        stat['AddedSV'] = get_field('addedSearchVolume', row)
        stat['CrawlingFrequency'] = get_field('crawlFrequency', row)
        stat['Has_AutoText'] = True if get_field('autoText', row) else False

        domTopText = html.fragment_fromstring(topText, create_parent="div")
        domLeftText = html.fragment_fromstring(leftText, create_parent="div")
        domBottomText = html.fragment_fromstring(bottomText, create_parent="div")
        domNewsText = html.fragment_fromstring(newsText, create_parent="div")
        domReviewsText = html.fragment_fromstring(reviewsText, create_parent="div")

        stat['International_URLs'] = int_url_count([
            get_field('internationalUrl.HK', row),
            get_field('internationalUrl.ID', row),
            get_field('internationalUrl.MY', row),
            get_field('internationalUrl.PH', row),
            get_field('internationalUrl.SG', row),
            get_field('internationalUrl.TH', row),
            get_field('internationalUrl.VN', row)
        ])

        stat['Has_Logo'] = str(has_logo(get_field('image', row)))
        stat['Has_Title'] = str(has_title(get_field('title', row)))
        stat['Has_Meta'] = str(has_meta(get_field('meta', row)))
        stat['Has_Heading'] = str(has_heading(get_field('heading', row)))
        stat['Has_Redirect'] = count_redirects(get_array('redirects', row))

        stat['PC_Specs'] = str(has_specs(get_field('specs', row)))
        stat['PC_News'] = str(has_news(get_field('news', row)))
        stat['PC_Reviews'] = str(has_reviews(get_field('reviews', row)))
        stat['PC_Images_Small'] = count_images(get_array('images.small', row))
        stat['PC_Images_Medium'] = count_images(get_array('images.medium', row))
        stat['PC_Images_Large'] = count_images(get_array('images.large', row))

        stat['Top_Characters'] = character_count(topText)
        stat['Left_Character'] = character_count(leftText)
        stat['Bottom_Characters'] = character_count(bottomText)
        stat['News_Characters'] = character_count(newsText)
        stat['Reviews_Characters'] = character_count(reviewsText)

        stat['Top_Words'] = word_count(topText)
        stat['Left_Words'] = word_count(leftText)
        stat['Bottom_Words'] = word_count(bottomText)
        stat['News_Words'] = word_count(newsText)
        stat['Reviews_Words'] = word_count(reviewsText)

        stat['Top_Paragraphs'] = paragraph_count(domTopText)
        stat['Left_Paragraphs'] = paragraph_count(domLeftText)
        stat['Bottom_Paragraphs'] = paragraph_count(domBottomText)
        stat['News_Paragraphs'] = paragraph_count(domNewsText)
        stat['Reviews_Paragraphs'] = paragraph_count(domReviewsText)

        stat['Top_H1'] = h1_count(topText)
        stat['Left_H1'] = h1_count(leftText)
        stat['Bottom_H1'] = h1_count(bottomText)

        stat['Top_H2'] = h2_count(topText)
        stat['Left_H2'] = h2_count(leftText)
        stat['Bottom_H2'] = h2_count(bottomText)

        stat['Top_H3'] = h3_count(topText)
        stat['Left_H3'] = h3_count(leftText)
        stat['Bottom_H3'] = h3_count(bottomText)

        stat['Bottom_List'] = list_count(bottomText)
        stat['Bottom_Image'] = image_count(bottomText)
        stat['Bottom_Iframe'] = iframe_count(bottomText)
        stat['Bottom_Table'] = table_count(bottomText)
        stat['Bottom_Internal_Links'] = link_count_internal(domBottomText)
        stat['Bottom_External_Links'] = link_count_external(domBottomText)
        stat['Bottom_CC'] = cc_count(stat['CC'], bottomText)
        stat['Bottom_Country'] = country_count(stat['CC'], bottomText)

        stat['Single_Item_List'] = single_item_list(domBottomText)
        stat['Empty_Paragraph'] = empty_paragraph(domBottomText)
        stat['Missing_Table_Header'] = missing_table_header(domBottomText)
        stat['Table_Width_Height'] = table_width_height(domBottomText)
        stat['Image_In_Table'] = image_in_table(domBottomText)
        stat['Image_Not_CDN'] = image_not_cdn(domBottomText)
        stat['Spaces_At_End'] = spaces_at_end(bottomText)
        stat['Double_Spaces'] = spaces_at_end(bottomText)
        stat['Custom_Styles'] = custom_styles(bottomText)
        stat['Broken_Definition_List'] = broken_definition_list(domBottomText)
        stat['Bold_Not_Heading'] = bold_not_heading(bottomText)

        stats.append(stat)

    return stats


def read_data(filename):
    data = []
    with codecs.open(filename, 'r', 'utf-8') as data_file:
        for row in data_file:
            try:
                data.append(json.loads(row))
            except ValueError, e:
                print >> sys.stderr, "WARNING: can't parse row - %s" % row
    return data


def output(stats):
    output = pandas.DataFrame(stats, columns=stats[0].keys())
    output.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


data = read_data(sys.argv[1])
stats = calculate_stats(data)
output(stats)
