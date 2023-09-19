import tweepy, requests, pytz, os, lxml.html, re, asyncio, json, tempfile
from io import BytesIO
from PIL import Image
from datetime import datetime
from fastapi import FastAPI, status
from atprototools import Session

consumer_key = os.environ['API_KEY']
consumer_secret = os.environ['API_SECRET']
access_token = os.environ['ACCES_TOKEN']
access_token_secret = os.environ['ACCES_TOKEN_SECRET']
BSKY_USERNAME = os.environ['BSKY_USERNAME']
BSKY_PASSWORD = os.environ['BSKY_PASSWORD']

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret)

api = tweepy.API(auth)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret)

bsky_client_session = Session(BSKY_USERNAME, BSKY_PASSWORD)

months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
          'julio', 'agosto', 'septiembre', 'octubre', 'noviembre']

weekdays = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']


def getdate():
  time_utc = pytz.timezone('UTC').localize(datetime.utcnow())
  now = time_utc.astimezone(pytz.timezone('America/Buenos_Aires'))
  date = now.strftime('%Y,%m,%d,%w')
  return date.split(',')

def post_twitter(img_url, text, filename):
    response = requests.get(img_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        b = BytesIO()
        image.save(b, "PNG")
        b.seek(0)
        media = api.media_upload(filename=filename, file=b)
        tweet = client.create_tweet(text=text, media_ids=[media.media_id])
        return tweet
    else:
        return "Error"

def post_blusky(image_url, text):
    minimum_quality = 50
    quality = 95      
    target = 900000
    img_path = f'{tempfile.gettempdir()}{os.path.sep}image.png'
    img = requests.get(image_url)
    img_file = None
    if img.status_code == 200:
      img_file = img.content
    else:
      return "Error"
    image = Image.open(BytesIO(img_file))
    while True:
        b = BytesIO()
        image.save(b, "JPEG", quality=quality)
        b.seek(0)
        file_size = b.tell()
        print(file_size)
        if file_size <= target or quality <= minimum_quality:
            b.close()
            break
        else:
            quality -= 5
    image.save(img_path, "JPEG", quality=quality)
    try:
        res = bsky_client_session.postBloot(text, img_path)
        return res.content
    except Exception as e:
        return e





app = FastAPI()

@app.post("/tapa_clarin")
def tapa_clarin():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://tapas.clarin.com/tapa/{year}/{month}/{day}/{year}{month}{day}_thumb.jpg"
    text = f"🇦🇷 La tapa de @clarincom de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"clarin_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK


@app.post("/tapa_lanacion")
def tapa_lanacion():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=2260{year}{month}{day}00000000001001&page=1&width=1200"
    text = f"🔴 La tapa de @LANACION de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"lanacion_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK


@app.post("/tapa_elpais_uy")
def tapa_elpais_uy():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=9vl8{year}{month}{day}00000000001001&page=1"
    text = f"🇺🇾 La tapa de @elpaisuy de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"elpaisuy_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_ole")
def tapa_ole():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://tapas2.ole.com.ar/tapa/{year}/{month}/{day}/OLE_{year}{month}{day}_01.jpg"
    text = f"⚽️ La tapa de @DiarioOle de este {weekdays[int(weekday)]} {day} de {months[int(month)-1]} de {year}"
    filename = f"ole_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK


@app.post("/tapa_lavoz")
def tapa_lavoz():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/pressdisplay/docserver/getimage.aspx?file=e158{year}{month}{day}00000000001001&page=1&scale=90"
    text = f"🗞️ La tapa de @LAVOZcomar de este {weekdays[int(weekday)]} {day} de {months[int(month)-1]} de {year}"
    filename = f"lavoz_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_usatoday")
def tapa_usatoday():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=1152{year}{month}{day}00000000001001&page=1&width=1200"
    text = f"🇺🇸 La tapa de @USATODAY de este {weekdays[int(weekday)]}"
    filename = f"usatoday_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_elpais_es")
def tapa_elpais_es():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://srv00.epimg.net/pdf/elpais/snapshot/{year}/{month}/elpais/{year}{month}{day}Big.jpg"
    text = f"🇪🇸 La tapa de @el_pais de este {weekdays[int(weekday)]}"
    filename = f"elpais_es_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_folha")
def tapa_folha():
    year, month, day, weekday = getdate()
    res = requests.get(f"https://www1.folha.uol.com.br/fsp/fac-simile/{year}/{month}/{day}/index.shtml")
    tree = lxml.html.fromstring(res.content)
    imageUrl  = tree.xpath("//img/@src")[0]
    imageUrl = imageUrl.replace("sm.jpg","rt.jpg")
    text = f"🇧🇷 La tapa de @folha de este {weekdays[int(weekday)]}"
    filename = f"folha_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_mercurio")
def tapa_mercurio():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/cl/cl_mercurio.jpg"
    text = f"🇨🇱 La tapa de @ElMercurio_cl de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"mercurio_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_larepublica")
def tapa_larepublica():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://presmedia.glr.pe/1024x1298/larepublica/printed/{year}/{month}/{day}/lima/pages/01.jpeg"
    text = f"🇵🇪 La tapa de @larepublica_pe de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"larepublica_pe_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    #funcion_threads(text, imageUrl)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK


@app.post("/tapa_losandes")
def tapa_losandes():
    year, month, day, weekday = getdate()
    imageUrl = f"https://i.prcdn.co/pressdisplay/docserver/getimage.aspx?file=e866{year}{month}{day}00000000001001&page=1"
    text = f"La tapa de @LosAndesDiario de este {weekdays[int(weekday)]}"
    filename = f"tapa_losandes_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_gestion")
def tapa_gestion():
    year, month, day, weekday = getdate()
    imageUrl = f"https://i.prcdn.co/img?file=eag6{year}{month}{day}00000000001001&page=1&height=1200"
    text = f"🇵🇪 La tapa de @Gestionpe de este {weekdays[int(weekday)]}"
    filename = f"tapa_gestion_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_eluniversal")
def tapa_eluniversal():
    year, month, day, weekday = getdate()
    res = requests.get("https://www.eluniversal.com.mx/")
    tree = lxml.html.fromstring(res.content)
    src_data = tree.xpath("//picture[@class='portada__pic flex']/img/@data-src")[0]
    img_partial_url = re.sub(r".*(cloudfront.*)",r"\1", src_data)
    imageUrl = f"https://{img_partial_url}"
    text = f"🇲🇽 La tapa de @El_Universal_Mx de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"tapa_eluniversal_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_yedioth")
def tapa_yedioth():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/il/yedioth_ahronoth.jpg"
    text = f"🇮🇱 La tapa de @YediotAhronot de este {weekdays[int(weekday)]}"
    filename = f"tapa_yedioth_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_wsj")
def tapa_wsj():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/us/wsj.jpg"
    text = f"La tapa del @WSJ de este {weekdays[int(weekday)]}"
    filename = f"tapa_wsj_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_thetimes")
def tapa_thetimes():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/uk/the_times.jpg"
    text = f"🇬🇧 La tapa de @thetimes de este {weekdays[int(weekday)]}"
    filename = f"tapa_thetimes_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK

@app.post("/tapa_lemonde")
def tapa_lemonde():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/fr/lemonde.jpg"
    text = f"🇫🇷 La tapa de @lemondefr de este {weekdays[int(weekday)]}"
    filename = f"tapa_lemondefr_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK



@app.post("/tapa_lanacionpy")
def tapa_lanacionpy():
    year, month, day, weekday = getdate()
    js_url = "https://www.lanacion.com.py/pf/api/v3/content/fetch/content-search-feed?query=%7B%22feedFrom%22%3A0%2C%22feedQuery%22%3A%22taxonomy.sites._id%3A%2522%2Ftapa%2522%22%2C%22feedSize%22%3A1%2C%22website%22%3A%22lanacionpy%22%7D&_website=lanacionpy"
    res = requests.get(js_url)
    tapa_object = json.loads(res.text)
    imageUrl  = tapa_object['content_elements'][0]['promo_items']['basic']['featured_image']['url']
    text = f"🇵🇾 La tapa de @lanacionpy de este {weekdays[int(weekday)]}"
    filename = f"tapa_lanacionpy_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    post_blusky(imageUrl, text)
    return status.HTTP_200_OK


