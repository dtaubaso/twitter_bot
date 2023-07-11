import tweepy, requests, pytz, os, lxml.html, re, asyncio
from io import BytesIO
from PIL import Image
from datetime import datetime
from fastapi import FastAPI, status
from threads_api.src.threads_api import ThreadsAPI

consumer_key = os.environ['API_KEY']
consumer_secret = os.environ['API_SECRET']
access_token = os.environ['ACCES_TOKEN']
access_token_secret = os.environ['ACCES_TOKEN_SECRET']
threads_user = os.environ['THREADS_USER']
threads_password = os.environ['THREADS_PASSWORD']

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret)

api = tweepy.API(auth)

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret)

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

async def post_threads(text, image):
    threads_api = ThreadsAPI()
    await threads_api.login(threads_user, threads_password)
    result = await threads_api.post(text, image_path=image)

    if result:
        print("Post has been successfully posted")
    else:
        print("Unable to post.")

def funcion_threads(text, image):
  async def activar_post(text, image):
    await post_threads(text, image)
  loop = asyncio.get_event_loop()
  loop.run_until_complete(activar_post(text, image))

app = FastAPI()

@app.post("/tapa_clarin")
def tapa_clarin():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://tapas.clarin.com/tapa/{year}/{month}/{day}/{year}{month}{day}_thumb.jpg"
    text = f"🇦🇷 La tapa de @clarincom de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"clarin_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK


@app.post("/tapa_lanacion")
def tapa_lanacion():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=2260{year}{month}{day}00000000001001&page=1&width=1200"
    text = f"🔴 La tapa de @LANACION de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"lanacion_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK


@app.post("/tapa_elpais_uy")
def tapa_elpais_uy():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=9vl8{year}{month}{day}00000000001001&page=1"
    text = f"🇺🇾 La tapa de @elpaisuy de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"elpaisuy_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_ole")
def tapa_ole():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://tapas2.ole.com.ar/tapa/{year}/{month}/{day}/OLE_{year}{month}{day}_01.jpg"
    text = f"⚽️ La tapa de @DiarioOle de este {weekdays[int(weekday)]} {day} de {months[int(month)-1]} de {year}"
    filename = f"ole_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK


@app.post("/tapa_lavoz")
def tapa_lavoz():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/pressdisplay/docserver/getimage.aspx?file=e158{year}{month}{day}00000000001001&page=1&scale=90"
    text = f"🗞️ La tapa de @LAVOZcomar de este {weekdays[int(weekday)]} {day} de {months[int(month)-1]} de {year}"
    filename = f"lavoz_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_usatoday")
def tapa_usatoday():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://i.prcdn.co/img?file=1152{year}{month}{day}00000000001001&page=1&width=1200"
    text = f"🇺🇸 La tapa de @USATODAY de este {weekdays[int(weekday)]}"
    filename = f"usatoday_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_elpais_es")
def tapa_elpais_es():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://srv00.epimg.net/pdf/elpais/snapshot/{year}/{month}/elpais/{year}{month}{day}Big.jpg"
    text = f"🇪🇸 La tapa de @el_pais de este {weekdays[int(weekday)]}"
    filename = f"elpais_es_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
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
    return status.HTTP_200_OK

@app.post("/tapa_mercurio")
def tapa_mercurio():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/cl/cl_mercurio.jpg"
    text = f"🇨🇱 La tapa de @ElMercurio_cl de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"mercurio_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_larepublica")
def tapa_larepublica():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://presmedia.glr.pe/1024x1298/larepublica/printed/{year}/{month}/{day}/lima/pages/01.jpeg"
    text = f"🇵🇪 La tapa de @larepublica_pe de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"larepublica_pe_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK


@app.post("/tapa_losandes")
def tapa_losandes():
    year, month, day, weekday = getdate()
    imageUrl = f"https://i.prcdn.co/pressdisplay/docserver/getimage.aspx?file=e866{year}{month}{day}00000000001001&page=1"
    text = f"La tapa de @LosAndesDiario de este {weekdays[int(weekday)]}"
    filename = f"tapa_losandes_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    funcion_threads(text, imageUrl)
    return status.HTTP_200_OK

@app.post("/tapa_gestion")
def tapa_gestion():
    year, month, day, weekday = getdate()
    imageUrl = f"https://i.prcdn.co/img?file=eag6{year}{month}{day}00000000001001&page=1&height=1200"
    text = f"🇵🇪 La tapa de @Gestionpe de este {weekdays[int(weekday)]}"
    filename = f"tapa_gestion_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    funcion_threads(text, imageUrl)
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
    return status.HTTP_200_OK

@app.post("/tapa_yedioth")
def tapa_yedioth():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/il/yedioth_ahronoth.jpg"
    text = f"🇮🇱 La tapa de @YediotAhronot de este {weekdays[int(weekday)]}"
    filename = f"tapa_yedioth_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_wsj")
def tapa_wsj():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/us/wsj.jpg"
    text = f"La tapa del @WSJ de este {weekdays[int(weekday)]}"
    filename = f"tapa_wsj_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_thetimes")
def tapa_thetimes():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/uk/the_times.jpg"
    text = f"🇬🇧 La tapa de @thetimes de este {weekdays[int(weekday)]}"
    filename = f"tapa_thetimes_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

@app.post("/tapa_lemonde")
def tapa_lemonde():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://img.kiosko.net/{year}/{month}/{day}/fr/lemonde.jpg"
    text = f"🇫🇷 La tapa de @lemondefr de este {weekdays[int(weekday)]}"
    filename = f"tapa_lemondefr_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK

