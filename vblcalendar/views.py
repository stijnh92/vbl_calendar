from django.shortcuts import render
import requests
from lxml import html
import vobject
import datetime
from django.http import HttpResponse
import pytz
from ast import literal_eval


# Create your views here.
def home(request):
    page = requests.get('http://vblweb.wisseq.eu/Home/Competities')
    tree = html.fromstring(page.text)
    competitions = tree.xpath('//ul[@id="tabs"]/li/a')
    regions = {}

    for _x in competitions:
        temp_code = _x.xpath('@ng-click')[0]
        # example temp_code: "loadPoules('http://vblCB.wisseq.eu/VBLCB_WebService/data', 'BVBL9180')"
        # replace loadPoules and cast result to tuple
        temp_code = literal_eval(temp_code.replace('loadPoules', ''))
        code = temp_code[1]
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

    # games = (d for d in competitions['wedstrijden'] if d['teamThuisGUID'] == 'BVBL1379HSE  1')

    return render(request,
                  'devision.html',
                  {
                    'name': competitions['naam'],
                    # 'games': games,
                    'teams': competitions['teams']
                  }
                  )


def team(request, code):

    code = code.replace(' ', '+')
    # Games
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/TeamMatchesByGuid?teamGuid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    games = response.json()

    print games

    games = sorted(games, key=lambda k: k['jsDTCode'])

    return render(request,
                  'team.html',
                  {
                    'games': games,
                    'team_code': code
                  }
                  )


def team_ics_file(request, code):
    code = code.replace(' ', '+')
    # Games
    competitions_url = "http://vblcb.wisseq.eu/VBLCB_WebService/data/TeamMatchesByGuid?teamGuid=%s" % code

    # request the URL and parse the JSON
    response = requests.get(competitions_url)
    response.raise_for_status()
    games = response.json()

    games = sorted(games, key=lambda k: k['jsDTCode'])

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    event_list = []
    local_tz = pytz.timezone('Europe/Brussels')

    for game in games:
        # Add event detail
        vevent = cal.add('vevent')
        vevent.add('summary').value = '%s - %s' % (game['tTNaam'], game['tUNaam'])
        """
        datumString: 15-08-2015
        beginTijd: 20.00
        """
        time_string = '%s %s' % (game['datumString'], game['beginTijd'])

        try:
            local_time = datetime.datetime.strptime(time_string, '%d-%m-%Y %H.%M')
        except:
            time_string += '12.00'
        local_dt = local_tz.localize(local_time, is_dst=None)
        utc_start = local_dt.astimezone(pytz.utc)
        utc_end = utc_start + datetime.timedelta(hours=2)

        start = vevent.add('dtstart')
        start.value = utc_start

        end = vevent.add('dtend')
        end.value = utc_end

        # vevent.add('dtstart').value = time
        # vevent.add('dtend').value = end_time
        vevent.add('location').value = game['accNaam']
        vevent.add('description').value = '%s - %s\n%s' % (game['tTNaam'], game['tUNaam'], game['uitslag'])

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, content_type='text/calendar')
    response['Filename'] = '%s.ics' % code  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=%s.ics' % code

    return response
