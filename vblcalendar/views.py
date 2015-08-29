from django.shortcuts import render
import requests
from lxml import html, etree
import vobject
import datetime
from django.http import HttpResponse
from django.utils import timezone
import pytz


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
                    'games': games,
                    'team_code': code
                  }
                  )


def team_ics_file(request, code):
    code = code.replace(' ', '+')
    # Games
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/matchesbyteamguid?teamGuid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    games = response.json()[0]

    team = games['naam']
    games = sorted(games['wedstrijden'], key=lambda k: k['datSort'])

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    event_list = []
    utc = vobject.icalendar.utc
    for game in games:
        # Add event detail
        vevent = cal.add('vevent')
        vevent.add('summary').value = '%s - %s' % (game['teamThuisNaam'], game['teamUitNaam'])
        """
        datumString: 15-08-2015
        beginTijd: 20.00
        """
        time_string = '%s %s' % (game['datumString'], game['beginTijd'])
        time = datetime.datetime.strptime(time_string, '%d-%m-%Y %H.%M')
        timezone.make_aware(time, pytz.timezone('Europe/Brussels'))

        end_time = time + datetime.timedelta(hours=2)

        vevent.add('dtstart').value = time
        vevent.add('dtend').value = end_time
        vevent.add('location').value = game['accommOmschr']
        vevent.add('description').value = '%s - %s' % (game['teamThuisNaam'], game['teamUitNaam'])

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, content_type='text/calendar')
    response['Filename'] = '%s.ics' % team  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=%s.ics' % team

    return response
