import tweepy, requests, pytz, os
from io import BytesIO
from PIL import Image
from datetime import datetime
from fastapi import FastAPI, status

consumer_key = os.environ['API_KEY']
consumer_secret = os.environ['API_SECRET']
access_token = os.environ['ACCES_TOKEN']
access_token_secret = os.environ['ACCES_TOKEN_SECRET']

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

weekday = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']

def getdate():
  time_utc = pytz.timezone('UTC').localize(datetime.utcnow())
  now = time_utc.astimezone(pytz.timezone('America/Buenos_Aires'))
  date = now.strftime('%Y,%m,%d,%w')
  return date.split(',')

def post_twitter(img_url, text, filename):
    response = requests.get(img_url)
    image = Image.open(BytesIO(response.content))
    b = BytesIO()
    image.save(b, "PNG")
    b.seek(0)
    media = api.media_upload(filename=filename, file=b)
    response = client.create_tweet(text=text, media_ids=[media.media_id])
    return response

app = FastAPI()
@app.post("/tapa_clarin")
def tapa_clarin():
    year, month, day, weekday = getdate()
    imageUrl  = f"https://tapas.clarin.com/tapa/{year}/{month}/{day}/{year}{month}{day}_thumb.jpg"
    text = f"🇦🇷 La tapa de @clarincom de hoy, {day} de {months[int(month)-1]} de {year}"
    filename = f"clarin_{year}{month}{day}"
    post_twitter(imageUrl, text, filename)
    return status.HTTP_200_OK


