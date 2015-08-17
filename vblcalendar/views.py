from django.shortcuts import render
import requests
from lxml import html, etree


# Create your views here.
def home(request):
    page = requests.get('http://vblweb.wisseq.eu/Home/Competities')
    tree = html.fromstring(page.text)
    competitions = tree.xpath('//td/a')

    regions = {}
    for _x in competitions:
        code = _x.xpath('@href')[0].strip().rsplit('=', 1)[1]
        text = _x.xpath('text()')[0].strip()
        regions.update({
            code: text
        })

    return render(request,
                  'home.html',
                  {
                    'regions': regions
                  }
                  )


def region(request, code):
    # Competities
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/ListByRegio?IssRegioguid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    competitions = response.json()

    return render(request,
                  'region.html',
                  {
                    'competitions': competitions
                  }
                  )


def devision(request, code):
    # Competities
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/pouleByGuid?pouleguid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    competitions = response.json()[0]

    for d in competitions['wedstrijden']:
        print d['teamThuisGUID'] == 'BVBL1379HSE  1'

    games = (d for d in competitions['wedstrijden'] if d['teamThuisGUID'] == 'BVBL1379HSE  1')

    return render(request,
                  'devision.html',
                  {
                    'name': competitions['naam'],
                    'games': games,
                    'teams': competitions['teams']
                  }
                  )


def team(request, code):

    code = code.replace(' ', '+')
    # Games
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/matchesbyteamguid?teamGuid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    games = response.json()[0]

    team = games['naam']
    games = sorted(games['wedstrijden'], key=lambda k: k['datSort'])

    return render(request,
                  'team.html',
                  {
                    'team': team,
                    'games': games
                  }
                  )
