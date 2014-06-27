import sys,urllib,re,time
import wapiti2


URL = "http://www.example.com/"
DOMAIN = "example.com"
URLS_ARRAY = []

def find_item(item):
    global URLS_ARRAY
    global DOMAIN
    for i in range(len(URLS_ARRAY)):
        if URLS_ARRAY[i].find(item) >= 0:
            return 1 
    return 0


def spider(url, outfile):
    global URLS_ARRAY
    url = convert(url)
    if ((url.find(".css") < 0) and (url.find(".jpg") < 0) and (url.find(".jpeg") < 0) and (url.find(".gif") < 0) and (url.find(".png") < 0) and (url.find(".js") < 0) and (url.find("javascript") < 0) and (url.find(".html") <0) and (url.find(".shmtl") <0)) and (url.find(DOMAIN) > 0):
        pass
    else:
        return 0
    

    if find_item(url) == 0:
        URLS_ARRAY.append(url)
    else:
        return 0
    try:
        wp = urllib.urlopen(url)
        content = wp.read()
    except:
        print "Invalid url:%s" % url
        return 0

    regex = 'href[\\s]*=[\\s]*[\"|\']([^<\"]+)[\"|\']'

    obj = re.compile(regex)
    lines = obj.findall(content)
    data = wapiti2.webscan(url)
    if data.strip() != '':
        write_to_file(outfile, data)

    for i in range(len(lines)):
        spider(lines[i], outfile)
        if i % 2 == 0:
            time.sleep(0.5)

   
def write_to_file(out_file, line):
    file_obj = open(out_file, "a")
    if (line.find(".css") < 0) and (line.find(".jpg") < 0) and (line.find(".jpeg") < 0) and (line.find(".gif") < 0) and (line.find(".png") < 0) and (line.find(".js") < 0) and (line.find("javascript") < 0):
        file_obj.writelines(line + "\r\n")

    file_obj.close()
    
def convert(url):
    global URL
    if url.find("/") == 0:
        url = URL + url

    return url


if __name__ == "__main__":
    #url="http://www.meituan.com"
    #url="http://www.tizi.com"
    outfile="result.txt"
    spider(URL, outfile)
