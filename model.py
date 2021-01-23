from gevent import monkey; monkey.patch_all()

import csv
import bs4
import re
import tkinter
from tkinter import ttk
import itertools
import cProfile
from datetime import date
from selenium import webdriver
import subprocess


class Player:
    def __init__(self, name, PPG, HEAT, Sal, Team, Opponent, DvP, PM, pointsLast5, FPPM, projPoints, projValue, pos=[]):
        self.name = name
        self.pos = pos
        self.PPG = PPG
        self.HEAT = HEAT
        self.Sal = Sal
        self.Team = Team
        self.Opponent = Opponent
        self.DvP = DvP
        self.PM = PM
        self.pointsLast5 = pointsLast5
        self.FPPM = FPPM
        self.projPoints = projPoints
        self.projValue = projValue
        self.totalValue = 0


class Team5:
    def __init__(self, PG, SG, SF, PF, C, value, salary):
        self.PG = PG
        self.SG = SG
        self.SF = SF
        self.PF = PF
        self.C = C
        self.value = value
        self.salary = salary

    def depth(self):
        names = []
        names.append(self.PG.name)
        names.append(self.SG.name)
        names.append(self.SF.name)
        names.append(self.PF.name)
        names.append(self.C.name)
        return names

    def combine(self, team3):
        newSal = self.salary + team3.salary
        newVal = self.value + team3.value
        newestTeam = Team8(self.PG, self.SG, self.SF, self.PF, self.C, team3.G, team3.F, team3.Util, newVal, newSal)
        return newestTeam
class Team3:
    def __init__(self, G, F, Util, value, salary):
        self.G = G
        self.F = F
        self.Util = Util
        self.value = value
        self.salary = salary

    def depth(self):
        names = []
        names.append(self.G.name)
        names.append(self.F.name)
        names.append(self.Util.name)
        return names

class Team8:
    def __init__(self, PG, SG, SF, PF, C, G, F, Util, value, salary):
        self.PG = PG
        self.SG = SG
        self.SF = SF
        self.PF = PF
        self.C = C
        self.G = G
        self.F = F
        self.Util = Util
        self.value = value
        self.salary = salary

    def depth(self):
        names = []
        names.append(self.PG.name)
        names.append(self.SG.name)
        names.append(self.SF.name)
        names.append(self.PF.name)
        names.append(self.C.name)
        names.append(self.G.name)
        names.append(self.F.name)
        names.append(self.Util.name)
        return names

    def depthWithPlayerObject(self):
        names = []
        names.append(self.PG)
        names.append(self.SG)
        names.append(self.SF)
        names.append(self.PF)
        names.append(self.C)
        names.append(self.G)
        names.append(self.F)
        names.append(self.Util)
        return names

top = tkinter.Tk()
canvas = tkinter.Canvas(top, height=700, width=700, bg="#263D42")
canvas.pack()

frame = tkinter.Frame(top, bg="white")
frame.place(relwidth = .8, relheight=.8, relx=.1, rely=.1)
salary_cap = 50000
team_abbr = {"ATL": "ATLANTA", "BKN": "BROOKLYN", "CLE": "CLEVELAND", "DET": "DETROIT", "LAL": "LOS ANGELES LAKERS",
             "MEM": "MEMPHIS",
             "MIN": "MINNESOTA", "NY": "NEW YORK", "OKC": "OKLAHOMA", "PHO": "PHOENIX"
    , "SAC": "SACRAMENTO", "POR": "PORTLAND", "TOR": "TORONTO", "BOS": "BOSTON", "CHA": "CHARLOTTE", "CHI": "CHICAGO",
             "DEN": "DENVER", "GS": "GOLDEN", "HOU": "HOUSTON", "IND": "INDIANA",
             "LAC": "LOS ANGELES CLIPPERS", "MIA": "MIAMI", "MIL": "MILWAUKEE", "NO": "NEW ORLEANS", "ORL": "ORLANDO",
             "PHI": "PHILADELPHIA", "SA": "SAN",
             "UTA": "UTAH", "WAS": "WASHINGTON", "DAL": "DALLAS"}
team_abbr_full = {"ATL": "Atlanta", "BKN": "Brooklyn", "CLE": "Cleveland", "DET": "Detroit", "LAL": "LA Lakers",
                  "MEM": "Memphis",
                  "MIN": "Minnesota", "NY": "New York", "OKC": "Okla City", "PHO": "Phoenix"
    , "SAC": "Sacramento", "POR": "Portland", "TOR": "Toronto", "BOS": "Boston", "CHA": "Charlotte", "CHI": "Chicago",
                  "DEN": "Denver", "GS": "Golden State", "HOU": "Houston", "IND": "Indiana",
                  "LAC": "LA Clippers", "MIA": "Miami", "MIL": "Milwaukee", "NO": "New Orleans", "ORL": "Orlando",
                  "PHI": "Philadelphia", "SA": "San Antonio",
                  "UTA": "Utah", "WAS": "Washington", "DAL": "Dallas"}
pos_dict = {"PG": {}, "SG": {}, "C": {}, "PF": {}, "SF": {}}
team_dict = {"ATL": {}, "BKN": {}, "CLE": {}, "DET": {}, "LAL": {}, "MEM": {}, "MIN": {}, "NY": {}, "OKC": {}, "PHO": {}
    , "SAC": {}, "TOR": {}, "BOS": {}, "CHA": {}, "CHI": {}, "DEN": {}, "GS": {}, "HOU": {}, "IND": {},
             "LAC": {}, "MIA": {}, "MIL": {}, "NO": {}, "ORL": {}, "PHI": {}, "POR": {}, "PHX": {}, "SA": {},
             "UTA": {}, "WAS": {}, "DAL": {}}
team_spread_dict = {"ATL": {}, "BKN": {}, "CLE": {}, "DET": {}, "LAL": {}, "MEM": {}, "MIN": {}, "NY": {}, "OKC": {},
                    "PHO": {}
    , "SAC": {}, "POR": {}, "TOR": {}, "BOS": {}, "CHA": {}, "CHI": {}, "DEN": {}, "GS": {}, "HOU": {}, "IND": {},
                    "LAC": {}, "MIA": {}, "MIL": {}, "NO": {}, "ORL": {}, "PHI": {}, "SA": {},
                    "UTA": {}, "WAS": {}, "DAL": {}}
player_dict = {}
pos_dict = {"PG": {}, "SG": {}, "C": {}, "PF": {}, "SF": {}}
driver = webdriver.Chrome("chromedriver.exe")
starters = {}
PGs = []
SGs = []
PFs = []
SFs = []
Cs = []
bestPGs = []
bestSGs = []
bestPFs = []
bestSFs = []
bestCs = []
bestPlayers = []
guards = []
forwards = []
finalListOfTeams = []

def sportsbookScraper():
    games = []
    FullTeamData = {}
    driver.get("https://mybookie.ag/sportsbook/nba/")
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, "html.parser")
    for b in soup.findAll('div', attrs={'id': 'mainBets3'}):
        for a in b.findAll('div', attrs={'class': 'row m-0 mobile sportsbook-lines mb-2 border'}):
            for tag in a.findAll('div', attrs={'class': 'col-2 p-0 spread-lines'}):

                for item in tag.contents:

                    TeamData = {}
                    newstring = str(item)

                    newlist = newstring.split(" ")

                    for data in newlist:

                        teamName = ""

                        if "data-odds" in data:
                            name = re.split("\s*=\s*([\S\s]+)", data)
                            cleanOdds = name[1][1:]

                            teamOdds = data
                            TeamData["Odds"] = cleanOdds
                        elif "data-spread" in data:
                            name = re.split("\s*=\s*([\S\s]+)", data)
                            cleanSpread = name[1][1:]

                            teamSpread = data
                            TeamData["Spread"] = cleanSpread
                        elif "data-team" in data:
                            name = re.split("\s*=\s*([\S\s]+)", data)
                            cleanname = name[1][1:]

                            if cleanname == "NEW":
                                teamName2 = newlist.index(data)
                                teamName3 = newlist[teamName2 + 1]
                                cleanname += " " + teamName3
                            elif cleanname == "LOS":
                                teamName2 = newlist.index(data)
                                teamName3 = newlist[teamName2 + 1]
                                teamName4 = teamName3 + " " + newlist[teamName2 + 2]
                                cleanname += " " + teamName4[:-1]

                            TeamData["Team"] = cleanname

                    if len(TeamData) != 0:
                        for key in team_abbr:
                            if TeamData["Team"] == team_abbr[key]:
                                team_spread_dict[key]["Odds"] = TeamData["Odds"][:-1]
                                team_spread_dict[key]["Spread"] = TeamData["Spread"][:-1]
            for tag2 in a.findAll('div', attrs={'class': 'col-2 p-0 total-lines'}):

                for item in tag2.contents:
                    TeamData = {}

                    newstring = str(item)

                    newlist = newstring.split(" ")

                    for data in newlist:

                        teamName = ""

                        if "data-spread" in data:
                            name = re.split("\s*=\s*([\S\s]+)", data)  # this.players\s*=\s*([\S\s]+[]])
                            cleanOdds = name[1][:-1]

                            TeamData["Total"] = cleanOdds
                        elif "data-team" in data:
                            name = re.split("\s*=\s*([\S\s]+)", data)
                            cleanname = name[1][1:]
                            if cleanname == "NEW":

                                teamName2 = newlist.index(data)
                                teamName3 = newlist[teamName2 + 1]
                                cleanname += " " + teamName3
                            elif cleanname == "LOS":
                                teamName2 = newlist.index(data)
                                teamName3 = newlist[teamName2 + 1]
                                teamName4 = teamName3 + " " + newlist[teamName2 + 2]
                                cleanname += " " + teamName4[:-1]

                            TeamData["Name"] = cleanname

                    if len(TeamData) != 0:
                        for key in team_abbr:

                            if TeamData["Name"] == team_abbr[key]:
                                team_spread_dict[key]["Total O/U"] = abs(float(TeamData["Total"][1:]))


def overUnderScraper():
    driver.get("https://www.teamrankings.com/nba/trends/ou_trends/")
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, "html.parser")
    for a in soup.findAll('tr', attrs={'role': 'row'}):

        for tag in a.findAll('td', attrs={'class': 'text-right green sorting_1'}):

            over_percent = float(tag.contents[0][:-1])
            team = a.find('a').contents[0]

            for key in team_abbr_full:
                if team_abbr_full[key] == team:
                    team_spread_dict[key]["O"] = over_percent
                    team_spread_dict[key]["U"] = 100 - over_percent
        for tag in a.findAll('td', attrs={'class': 'text-right sorting_1'}):

            over_percent = float(tag.contents[0][:-1])
            team = a.find('a').contents[0]

            for key in team_abbr_full:
                if team_abbr_full[key] == team:
                    team_spread_dict[key]["O"] = over_percent
                    team_spread_dict[key]["U"] = 100 - over_percent

def depthChartScraper():
    driver.get("http://www.espn.com/nba/depth")
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, "html.parser")
    for a in soup.findAll('tr'):

        for b in a.findAll('td'):
            player1 = b.text.split()
            if len(player1) == 3:
                fullPlayer = player1[1] + " " + player1[2]

                if "(IL)" in fullPlayer:
                    final = fullPlayer.strip("(IL)").strip()
                    starters[final] = "IL"
                else:
                    starters[fullPlayer] = ""

            elif len(player1) == 2:
                fullPlayer = player1[1]
                starters[fullPlayer] = ""
def depthChartScraper():
    driver.get("http://www.espn.com/nba/depth")
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, "html.parser")
    for a in soup.findAll('tr'):

        for b in a.findAll('td'):
            player1 = b.text.split()
            if len(player1) == 3:
                fullPlayer = player1[1] + " " + player1[2]

                if "(IL)" in fullPlayer:
                    final = fullPlayer.strip("(IL)").strip()
                    starters[final] = "IL"
                else:
                    starters[fullPlayer] = ""

            elif len(player1) == 2:
                fullPlayer = player1[1]
                starters[fullPlayer] = ""
def depthChartScraper():
    driver.get("http://www.espn.com/nba/depth")
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, "html.parser")
    for a in soup.findAll('tr'):

        for b in a.findAll('td'):
            player1 = b.text.split()
            if len(player1) == 3:
                fullPlayer = player1[1] + " " + player1[2]

                if "(IL)" in fullPlayer:
                    final = fullPlayer.strip("(IL)").strip()
                    starters[final] = "IL"
                else:
                    starters[fullPlayer] = ""

            elif len(player1) == 2:
                fullPlayer = player1[1]
                starters[fullPlayer] = ""
def playerCreator():
    #todaysDate = str(date.month) + "_" + str(date.day) + "_" + str(date.year)
    #print(todaysDate)
    with open("DFS Data 3_6_20 - NBA DK.csv", 'r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)

        for line in csv_reader:
            name = line[1]
            if line[1] == 'Player':
                continue
            if line[1] == "0":
                continue
            else:
                if "/" in line[0]:
                    positions = line[0].split("/")
                else:
                    positions = line[0]
                p1 = Player(line[1], float(line[2]), line[3], float(line[4]), line[8], line[9], float(line[10]),
                            float(line[11]), float(line[12]), float(line[13]), float(line[14]), float(line[15]),
                            positions)
                player_dict[p1.name] = p1
                team_dict[p1.Team][p1.name] = p1
                if isinstance(p1.pos, list):
                    for pos in p1.pos:
                        pos_dict[pos][p1.name] = p1
                else:
                    pos_dict[p1.pos][p1.name] = p1


def pg_rank(player_dict, team_dict, team_spread_dict, pos_dict):
    pure_value = 0
    for guy in pos_dict["PG"]:
        player = pos_dict["PG"][guy]
        #print(player.name)
        firstInitial = player.name[0]
        lastName = (player.name).split()[1]
        #print(lastName)
        if player.PM == 0 or player.projPoints == 0 or player.projValue == 0:

            continue
        else:
            pure_value = player.PPG + ((player.PM / 10) * player.FPPM) + player.pointsLast5 + (
                        player.projPoints * player.DvP) - (player.Sal / 100)
            print(player.Team)
            if float(team_spread_dict[player.Team]['Total O/U']) > 216:
                pure_value += 3
            if float(team_spread_dict[player.Team]['Total O/U']) > 224:
                pure_value += 4
            if float(team_spread_dict[player.Team]['Total O/U']) < 216:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['Total O/U']) < 210:
                pure_value -= 4
            if float(team_spread_dict[player.Team]['O']) > 50:
                pure_value += 3
            if float(team_spread_dict[player.Team]['O']) >= 55:
                pure_value += 4

            if float(team_spread_dict[player.Team]['U']) > 50:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['U']) >= 45:
                pure_value -= 4

            if abs(float(team_spread_dict[player.Team]["Spread"])) >= 10:
                pure_value -= 5

            player.totalValue += pure_value
            if player.totalValue >= 30:
                bestPlayers.append(player)
                bestPGs.append(player)
            PGs.append(player)
            guards.append(player)


def sg_rank(player_dict, team_dict, team_spread_dict, pos_dict):
    pure_value = 0
    for guy in pos_dict["SG"]:
        player = pos_dict["SG"][guy]

        if player.PM == 0 or player.projPoints == 0 or player.projValue == 0:

            continue
        else:
            pure_value = player.PPG + ((player.PM / 10) * player.FPPM) + player.pointsLast5 + (
                        player.projPoints * player.DvP) - (player.Sal / 100)
            if float(team_spread_dict[player.Team]['Total O/U']) > 216:
                pure_value += 3
            if float(team_spread_dict[player.Team]['Total O/U']) > 224:
                pure_value += 4
            if float(team_spread_dict[player.Team]['Total O/U']) < 216:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['Total O/U']) < 210:
                pure_value -= 4
            if float(team_spread_dict[player.Team]['O']) > 50:
                pure_value += 3
            if float(team_spread_dict[player.Team]['O']) >= 55:
                pure_value += 4

            if float(team_spread_dict[player.Team]['U']) > 50:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['U']) >= 45:
                pure_value -= 4

            if abs(float(team_spread_dict[player.Team]["Spread"])) >= 10:
                pure_value -= 4

            player.totalValue += pure_value
            if player.totalValue >= 30:
                bestPlayers.append(player)
                bestSGs.append(player)
            SGs.append(player)
            guards.append(player)


def sf_rank(player_dict, team_dict, team_spread_dict, pos_dict):
    pure_value = 0
    for guy in pos_dict["SF"]:
        player = pos_dict["SF"][guy]

        if player.PM == 0 or player.projPoints == 0 or player.projValue == 0:

            continue
        else:
            pure_value = player.PPG + ((player.PM / 10) * player.FPPM) + player.pointsLast5 + (
                        player.projPoints * player.DvP) - (player.Sal / 100)
            if float(team_spread_dict[player.Team]['Total O/U']) > 216:
                pure_value += 3
            if float(team_spread_dict[player.Team]['Total O/U']) > 224:
                pure_value += 4
            if float(team_spread_dict[player.Team]['Total O/U']) < 216:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['Total O/U']) < 210:
                pure_value -= 4
            if float(team_spread_dict[player.Team]['O']) > 50:
                pure_value += 3
            if float(team_spread_dict[player.Team]['O']) >= 55:
                pure_value += 4

            if float(team_spread_dict[player.Team]['U']) > 50:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['U']) >= 45:
                pure_value -= 4

            if abs(float(team_spread_dict[player.Team]["Spread"])) >= 10:
                pure_value -= 5

            player.totalValue += pure_value
            if player.totalValue >= 30:
                bestPlayers.append(player)
                bestSFs.append(player)
            SFs.append(player)
            forwards.append(player)


def pf_rank(player_dict, team_dict, team_spread_dict, pos_dict):
    pure_value = 0
    for guy in pos_dict["PF"]:
        player = pos_dict["PF"][guy]

        if player.PM == 0 or player.projPoints == 0 or player.projValue == 0:

            continue
        else:
            pure_value = player.PPG + ((player.PM / 10) * player.FPPM) + player.pointsLast5 + (
                        player.projPoints * player.DvP) - (player.Sal / 100)
            if float(team_spread_dict[player.Team]['Total O/U']) > 216:
                pure_value += 3
            if float(team_spread_dict[player.Team]['Total O/U']) > 224:
                pure_value += 4
            if float(team_spread_dict[player.Team]['Total O/U']) < 216:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['Total O/U']) < 210:
                pure_value -= 4
            if float(team_spread_dict[player.Team]['O']) > 50:
                pure_value += 3
            if float(team_spread_dict[player.Team]['O']) >= 55:
                pure_value += 4

            if float(team_spread_dict[player.Team]['U']) > 50:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['U']) >= 45:
                pure_value -= 4

            if abs(float(team_spread_dict[player.Team]["Spread"])) >= 10:
                pure_value -= 5

            player.totalValue += pure_value
            if player.totalValue >= 30:
                bestPlayers.append(player)
                bestPFs.append(player)
            PFs.append(player)
            forwards.append(player)


def c_rank(player_dict, team_dict, team_spread_dict, pos_dict):
    pure_value = 0
    for guy in pos_dict["C"]:
        player = pos_dict["C"][guy]

        if player.PM == 0 or player.projPoints == 0 or player.projValue == 0:

            player.totalValue = 0
        else:

            pure_value = player.PPG + ((player.PM / 10) * player.FPPM) + player.pointsLast5 + (
                        player.projPoints * player.DvP) - (player.Sal / 100)
            if float(team_spread_dict[player.Team]['Total O/U']) > 216:
                pure_value += 3
            if float(team_spread_dict[player.Team]['Total O/U']) > 224:
                pure_value += 4
            if float(team_spread_dict[player.Team]['Total O/U']) < 216:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['Total O/U']) < 210:
                pure_value -= 4
            if float(team_spread_dict[player.Team]['O']) > 50:
                pure_value += 3
            if float(team_spread_dict[player.Team]['O']) >= 55:
                pure_value += 4

            if float(team_spread_dict[player.Team]['U']) > 50:
                pure_value -= 3
            if float(team_spread_dict[player.Team]['U']) >= 45:
                pure_value -= 4

            if abs(float(team_spread_dict[player.Team]["Spread"])) >= 10:
                pure_value -= 5

            if len(player.HEAT) != 0:
                if player.HEAT == "❄":
                    pure_value -= 6
                elif player.HEAT == "🔥":
                    pure_value += 6

            player.totalValue += pure_value
            if player.totalValue >= 30:
                bestPlayers.append(player)
                bestCs.append(player)
            Cs.append(player)


def rankAll():
    pg_rank(player_dict, team_dict, team_spread_dict, pos_dict)
    sg_rank(player_dict, team_dict, team_spread_dict, pos_dict)
    pf_rank(player_dict, team_dict, team_spread_dict, pos_dict)
    sf_rank(player_dict, team_dict, team_spread_dict, pos_dict)
    c_rank(player_dict, team_dict, team_spread_dict, pos_dict)





def positionRankAndSort():
    PGs.sort(key=lambda x: x.totalValue)
    PGs.reverse()
    SGs.sort(key=lambda x: x.totalValue)
    SGs.reverse()
    PFs.sort(key=lambda x: x.totalValue)
    PFs.reverse()
    SFs.sort(key=lambda x: x.totalValue)
    SFs.reverse()
    Cs.sort(key=lambda x: x.totalValue)
    Cs.reverse()


def showPlayers(position, top):
    if position == "PG":
        for player in PGs:
            x = tkinter.Checkbutton(top, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
            x.grid()
            print(x)
    elif position == "SG":
        for player in SGs:
            x = tkinter.Checkbutton(top, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
            x.grid()
            print(x)
    elif position == "SF":
        for player in SFs:
            x = tkinter.Checkbutton(top, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
            x.grid()
            print(x)
    elif position == "PF":
        for player in PFs:
            x = tkinter.Checkbutton(top, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
            x.grid()
            print(x)
    elif position == "C":
        for player in Cs:
            x = tkinter.Checkbutton(top, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
            x.grid()
            print(x)

def showPointGuards():
    for player in PGs:
        x = tkinter.Checkbutton(frame, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
        x.pack()
        continue

def guiCreator(top):
    #top.title("DraftKings Lineup Optimizer")
    #w = tkinter.Menubutton(top, text="Positions")
    #w.grid()
    #w.menu = tkinter.Menu(w, tearoff=0)
    #show = tkinter.BooleanVar
    #w["menu"] = w.menu
    #for position in pos_dict:
     #   w.menu.add_checkbutton(label=position, variable=show, offvalue=0, onvalue=1,
     #                          command=lambda: showPlayers(position))
    tabControl = ttk.Notebook(frame)
    tab1 = ttk.Frame(tabControl)
    # scrollbar1 = tkinter.Scrollbar(frame)
    # scrollbar1.pack(side="right", fill="y")
    tabControl.add(tab1, text="Point Guards")
    # mylist = tkinter.Listbox(tab1, yscrollcommand=scrollbar1.set, width=40)
    # for player in PGs:
    #     #mylist.insert("end", player.name + " " + str(player.Sal) + " " + str(round(player.totalValue, 3)))
    #     x = tkinter.Checkbutton(tab1, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
    #     x.pack()
    #     mylist.insert("end", x)
    # mylist.pack(side="left", fill="both")
    # scrollbar1.config(command=mylist.yview)
    tab2 = ttk.Frame(tabControl)
    # scrollbar2 = tkinter.Scrollbar(tab2)
    # scrollbar2.pack(side="right", fill="y")
    # mylist2 = tkinter.Listbox(tab2, yscrollcommand=scrollbar2.set, width=40)
    # for player in SGs:
    #     #mylist2.insert("end", player.name + " " + str(player.Sal) + " " + str(round(player.totalValue, 3)))
    #     x = tkinter.Checkbutton(tab2, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal) + "\n")
    #     mylist2.insert("end", x)
    # mylist2.pack(side="left", fill="both")
    # mylist2.pack()
    # scrollbar2.config(command=mylist2.yview)
    tabControl.add(tab2, text="Shooting Guards")
    tabControl.pack(expand=1, fill="both")
    text = tkinter.Text(tab1, cursor="arrow")
    vsb = tkinter.Scrollbar(tab1, command=text.yview)
    button = tkinter.Button(tab1, text="Get Values")
    text.configure(yscrollcommand=vsb.set)

    button.pack(side="top")
    vsb.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)

    checkbuttons = []
    vars = []
    for player in PGs:
        var = tkinter.IntVar(value=0)
        cb = tkinter.Checkbutton(text, text=player.name + " " + str(player.totalValue) + " " + str(player.Sal),
                            variable=var, onvalue=1, offvalue=0)
        text.window_create("end", window=cb)
        text.insert("end", "\n")
        checkbuttons.append(cb)
        vars.append(var)
    text.configure(state="disabled")
    text2 = tkinter.Text(tab2, cursor="arrow")
    vsb2 = tkinter.Scrollbar(tab2, command=text.yview)
    button2 = tkinter.Button(tab2, text="Get Values")
    text2.configure(yscrollcommand=vsb.set)

    button2.pack(side="top")
    vsb2.pack(side="right", fill="y")
    text2.pack(side="left", fill="both", expand=True)

    checkbuttons2 = []
    vars2 = []
    for player in SGs:
        var2 = tkinter.IntVar(value=0)
        cb = tkinter.Checkbutton(text, text=player.name + " " + str(round(player.totalValue, 3)) + " " + str(player.Sal),
                                 variable=var2, onvalue=1, offvalue=0)
        text2.window_create("end", window=cb)
        text2.insert("end", "\n")
        checkbuttons2.append(cb)
        vars2.append(var)
    text.configure(state="disabled")
    #pointGuards = tkinter.Button(frame, text="Point Guards", padx=10, pady=5, fg="white", bg="#263D42", command=showPointGuards()) #command=showPointGuards(frame)
    #pointGuards.pack()
    #shootingGuards = tkinter.Button(frame, text="Shooting Guards", padx=10, pady=5, fg="white", bg="#263D42")
    #shootingGuards.pack()
    top.mainloop()

    def get_values(self):
        for cb, var in zip(self.checkbuttons, self.vars):
            text = cb.cget("text")
            value = var.get()
            print("%s: %d" % (text, value))
def teamValue(teamList):
    value = 0
    for player in teamList:
        try:
            value += player.totalValue
        except:
            return 0
    return value


def teamSalary(teamList):
    salary = 0
    for player in teamList:
        try:
            salary += player.Sal
        except:
            return 0

    return salary


def top10teamCreator(combo, back3combo):

    bestTeamsWithSalary = []
    bestTeams = list(itertools.product(*combo))

    back3 = list(itertools.product(*back3combo))
    print(len(back3))
    print("LEN BACK 3 ^^^^^^")
    print(len(bestTeams))
    print("LEN BEST TEAMS ^^^^^^^^^")

    back3salary = []
    for team in back3:
        #index = back3.index(team)
        #previous = index-1
        currentSal = teamSalary(team)
        currentValue = teamValue(team)
        if len(set(team)) != 3:
            continue
        #elif set(back3[previous]) == set(team):
          #  continue
        else:
            if currentSal <= 16000 and currentValue >= 135:
                newTeam = Team3(team[0], team[1], team[2], currentValue, currentSal)
                back3salary.append(newTeam)


    for team in bestTeams:
        pgCount = 0
        sgCount = 0
        sfCount = 0
        pfCount = 0
        cCount = 0
        #index = bestTeams.index(team)
        #previous = index - 1
        value = teamValue(team)
        Sal = teamSalary(team)
       # if set(bestTeams[previous]) == set(team):
       #     continue
        if currentSal <= 41000 and value >= 295:
            newTeam = Team5(team[0], team[1], team[2], team[3], team[4], value, Sal)
            bestTeamsWithSalary.append(newTeam)
            continue
        for player in team:
            if player.pos == "PG":
                pgCount += 1
            if player.pos == "SG":
                sgCount += 1
            if player.pos == "SF":
                sfCount += 1
            if player.pos == "PF":
                pfCount += 1
            if player.pos == "C":
                cCount += 1
        if pgCount > 2 or sgCount > 2 or sfCount > 2 or pfCount > 2 or cCount > 2:
            bestTeams.remove(team)
            try:
                bestTeamsWithSalary.remove(newTeam)
            except:
                continue


    bestTeamsWithSalary.sort(key=lambda x: x.value)
    bestTeamsWithSalary.reverse()
    back3salary.sort(key=lambda x: x.value)
    back3salary.reverse()

    return bestTeamsWithSalary, back3salary


def fileWrite():
    file1 = open("PointGuards.txt", "w")
    file2 = open("ShootingGuards.txt", "w")
    file3 = open("PowerForwards.txt", "w")
    file4 = open("SmallForwards.txt", "w")
    file5 = open("Centers.txt", "w")
    for dude in PGs:
        file1.write(dude.name + "\n")
        file1.write(str(dude.totalValue) + "\n")
        file1.write(str(dude.Sal) + "\n")
        file1.write("\n")
    for dude in SGs:
        file2.write(dude.name + "\n")
        file2.write(str(dude.totalValue) + "\n")
        file2.write(str(dude.Sal) + "\n")
        file2.write("\n")
    for dude in PFs:
        file3.write(dude.name + "\n")
        file3.write(str(dude.totalValue) + "\n")
        file3.write(str(dude.Sal) + "\n")
        file3.write("\n")
    for dude in SFs:
        file4.write(dude.name + "\n")
        file4.write(str(dude.totalValue) + "\n")
        file4.write(str(dude.Sal) + "\n")
        file4.write("\n")
    for dude in Cs:
        file5.write(dude.name + "\n")
        file5.write(str(dude.totalValue) + "\n")
        file5.write(str(dude.Sal) + "\n")
        file5.write("\n")











def teamCombiner(s5, b3):
    print(str(len(s5)) + " LEN S5")

    print(str(len(b3))+ " LEN B3")
    fullTeams = []
    for team in s5:
        for team2 in b3:

            finalTeam = team.combine(team2)
            #print(finalTeam.depth())
            #print(len(set(finalTeam.depth())))
            #print(finalTeam.salary)
            if len(set(finalTeam.depth())) != 8:
                continue
            elif finalTeam.salary >= 50000:
                continue
            else:
                fullTeams.append(finalTeam)
    fullTeams.sort(key=lambda x: x.value)
    fullTeams.reverse()
    for i in range(0, len(fullTeams)-1):
        try:
            if fullTeams[i].value == fullTeams[i-1].value and fullTeams[i].salary == fullTeams[i-1].salary:
                del fullTeams[i]
        except IndexError:
            continue
    return fullTeams





def bestTeamWriter(teams):
    file = open("Best Teams.txt", "w")
    for team in teams:
        file.write("=====TEAM=====" + "\n")
        file.write(str(team.salary) + "\n")
        file.write(str(team.value) + "\n")
        for dude in team.depthWithPlayerObject():
            file.write(dude.name + " " + dude.pos + " " + str(dude.totalValue) + "\n")
        file.write("\n")

def certain1Player(player1, s5, b3):
    teamsWithPlayer = []
    fileName = "Teams With " + player1 + ".txt"

    for team in s5:
        for team2 in b3:
            finalTeam = team.combine(team2)
            if len(set(finalTeam.depth())) != 8:
                continue
            elif finalTeam.salary >= 50000:
                continue
            elif player1 in finalTeam.depth():
                teamsWithPlayer.append(finalTeam)
    teamsWithPlayer.sort(key=lambda x: x.value)
    teamsWithPlayer.reverse()

    file = open(fileName, "w")
    for team in teamsWithPlayer:
        index = teamsWithPlayer.index(team)
        previous = index-1
        try:
            if teamsWithPlayer[index].value == teamsWithPlayer[previous].value and teamsWithPlayer[index].salary == teamsWithPlayer[previous].salary:
                del teamsWithPlayer[index]
        except IndexError:
            continue
        file.write("=====TEAM=====" + "\n")
        file.write(str(team.salary) + "\n")
        file.write(str(team.value) + "\n")
        for dude in team.depthWithPlayerObject():
            file.write(dude.name + " " + dude.pos + "\n")
        file.write("\n")
    print("Thank you! Your lists are ready")

def certain2Players(player1, player2, s5, b3):
    teamsWithPlayer = []
    fileName = "Teams With " + player1 + " " + player2+ ".txt"

    for team in s5:
        for team2 in b3:
            finalTeam = team.combine(team2)
            if len(set(finalTeam.depth())) != 8:
                continue
            elif finalTeam.salary >= 50000:
                continue
            elif player1 in finalTeam.depth() and player2 in finalTeam.depth():
                teamsWithPlayer.append(finalTeam)
    teamsWithPlayer.sort(key=lambda x: x.value)
    teamsWithPlayer.reverse()
    file = open(fileName, "w")
    for team in teamsWithPlayer:
        index = teamsWithPlayer.index(team)
        previous = index - 1
        try:
            if teamsWithPlayer[index].value == teamsWithPlayer[previous].value and teamsWithPlayer[index].salary == \
                    teamsWithPlayer[previous].salary:
                del teamsWithPlayer[index]
        except IndexError:
            continue
        file.write("=====TEAM=====" + "\n")
        file.write(str(team.salary) + "\n")
        file.write(str(team.value) + "\n")
        for dude in team.depthWithPlayerObject():
            file.write(dude.name + " " + dude.pos + "\n")
        file.write("\n")
    print("Thank you! Your lists are ready")


def certain3Players(player1, player2, player3, s5, b3):
    teamsWithPlayer = []
    fileName = "TeamsWith" + player1 + " " + player2 + " " + player3 + ".txt"
    for team in s5:
        for team2 in b3:
            finalTeam = team.combine(team2)
            if len(set(finalTeam.depth())) != 8:
                continue
            elif finalTeam.salary >= 50000:
                continue
            elif player1 in finalTeam.depth() and player2 in finalTeam.depth():
                teamsWithPlayer.append(finalTeam)
    teamsWithPlayer.sort(key=lambda x: x.value)
    teamsWithPlayer.reverse()
    file = open(fileName, "w")
    for team in teamsWithPlayer:
        index = teamsWithPlayer.index(team)
        previous = index - 1
        try:
            if teamsWithPlayer[index].value == teamsWithPlayer[previous].value and teamsWithPlayer[index].salary == \
                    teamsWithPlayer[previous].salary:
                del teamsWithPlayer[index]
        except IndexError:
            continue
        file.write("=====TEAM=====" + "\n")
        file.write(str(team.salary) + "\n")
        file.write(str(team.value) + "\n")
        for dude in team.depthWithPlayerObject():
            file.write(dude.name + " " + dude.pos + "\n")
        file.write("\n")
    print("Thank you! Your lists are ready")

def certain4Players(player1, player2, player3, player4, s5, b3):
    teamsWithPlayer = []
    fileName = "TeamsWith" + player1 + " " + player2 + " " + player3 + " " + player4 + ".txt"
    for team in s5:
        for team2 in b3:
            finalTeam = team.combine(team2)
            if len(set(finalTeam.depth())) != 8:
                continue
            elif finalTeam.salary >= 50000:
                continue
            elif player1 in finalTeam.depth() and player2 in finalTeam.depth():
                teamsWithPlayer.append(finalTeam)
    teamsWithPlayer.sort(key=lambda x: x.value)
    teamsWithPlayer.reverse()
    file = open(fileName, "w")
    for team in teamsWithPlayer:
        file.write("=====TEAM=====" + "\n")
        file.write(str(team.salary) + "\n")
        file.write(str(team.value) + "\n")
        for dude in team.depthWithPlayerObject():
            file.write(dude.name + " " + dude.pos + "\n")
        file.write("\n")
    print("Thank you! Your lists are ready")


def askForPlayer(s5, b3):
    asked = False
    desirePlayer = input("Would you like to specify just one single player? ")
    if desirePlayer == "Yes" or desirePlayer == "yes" or desirePlayer == "y" or desirePlayer == "Y":
        asked = True
        who = input("What player would you like? ")
        for person in player_dict:
            if person == who:
                certain1Player(who, s5, b3)
    elif desirePlayer == "No" or desirePlayer == "no" or desirePlayer == "n" or desirePlayer == "N":
        more = input("would you like to specify more than one player? ")
        if more == "Yes" or more == "yes" or more == "y" or more == "Y":
            asked = True
            howMany = input("How many players? Please use an integer: ")
            if howMany == "2":
                count = 0
                player1 = input("Please enter the first players full name: ")
                player2 = input("Please enter the second players full name: ")
                for person in player_dict:
                    if player1 == person or player2 == person:
                        count += 1
                if count == 2:
                    certain2Players(player1, player2, s5, b3)
            elif howMany == "3":
                count = 0
                player1 = input("Please enter the first players full name: ")
                player2 = input("Please enter the second players full name: ")
                player3 = input("Please enter the third players full name: ")
                for person in player_dict:
                    if player1 == person or player2 == person or player3 == person:
                        count += 1
                if count == 3:
                    certain3Players(player1, player2, player3, s5, b3)
            elif howMany == "4":
                count = 0
                player1 = input("Please enter the first players full name: ")
                player2 = input("Please enter the second players full name: ")
                player3 = input("Please enter the third players full name: ")
                player4 = input("Please enter the fourth players full name: ")
                for person in player_dict:
                    if player1 == person or player2 == person or player3 == person or player4 == person:
                        count += 1
                if count == 4:
                    certain4Players(player1, player2, player3, player4, s5, b3)
        
            else:
                print("Incorrect Value")


    return asked

def main():
    print(1)
    sportsbookScraper()
    print(2)
    overUnderScraper()
    print(3)
    depthChartScraper()
    print(4)
    driver.close()
    print(5)
    playerCreator()
    print(6)
    print(team_spread_dict)
    rankAll()
    print(7)
    positionRankAndSort()
    print(8)
    combo = [bestPGs, bestSGs, bestSFs, bestPFs, bestCs]
    print(9)
    back3combo = [guards, forwards, bestPlayers]
    print(combo)
    print(10)
    fullTeam = top10teamCreator(combo, back3combo)
    print(11)
    starting5final = fullTeam[0]

    print(12)
    back3final = fullTeam[1]
    print(13)
    #norepeatsback3 = list(set(back3final))
    #print(norepeatsback3)
    print(14)
    back3final.sort(key=lambda x: x.value)
    print(15)
    back3final.reverse()
    print(16)
    asked = askForPlayer(starting5final, back3final)
    print(17)
    if not asked:

        theEnd = teamCombiner(starting5final, back3final)
        print(18)
        bestTeamWriter(theEnd)
        print(19)
        fileWrite()
        print(20)
    else:

        fileWrite()
        print(21)


    #guiCreator(top)


if __name__ == "__main__":
    #cProfile.run("main()")
    main()


