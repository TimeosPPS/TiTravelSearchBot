from API import FOURSQUARE_API_KEY
import requests
def get_venue_photo(place_id):
    url = f'https://api.foursquare.com/v3/places/{place_id}/photos'
    headers = {
        'Accept': 'application/json',
        'Authorization': FOURSQUARE_API_KEY
    }
    forsquare = requests.get(url, headers=headers)
    if forsquare.status_code == 200:
        fsdata = forsquare.json()
        if fsdata:
            prefix = fsdata[0]['prefix']
            suffix = fsdata[0]['suffix']
            return f"{prefix}original{suffix}"
        else:
            return "https://previews.123rf.com/images/vecstock/vecstock2003/vecstock200314926/142708451-projeto-do-%C3%ADcone-do-estilo-do-bloco-da-linha-do-dispositivo-da-c%C3%A2mera-foco-digital-da-foto-do.jpg"