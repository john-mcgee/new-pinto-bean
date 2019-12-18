# ------------------------------------------------------------------
# Example of a web scraping script using BeautifulSoup and Selenium
# Scrapes select sports stats and records them in a CSV file 
#
# For demonstrative and educational purposes only
# (c) 2019 John McGee, United States
#
# ------------------------------------------------------------------ 

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import time
import csv

today = date.today()
today = today.strftime("%m%d%Y")

#Prepare the soup
site = "https://www.pro-football-reference.com"
chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(options=chrome_options)
browser.get(site)
time.sleep(1)
html = browser.page_source    
homepage = BeautifulSoup(html, 'lxml')

#Create offensive stat CSV file (off_csv) and write headers
off_csv = "FF-Off-Stats-{date}.csv".format(date=today)
off_headers = ["Player","Team","Cmp","Att","Yds","TD","Int","Sk","Yds","Lng","Rate","Att","Yds","TD","Lng","Tgt","Rec","Yds","TD","Lng","Fmb","FL","Week"]
off_file = open(off_csv, "w", newline='')
off_writer = csv.writer(off_file)
off_writer.writerow(off_headers)

#Create defensive stat CSV file (dst_csv) and write headers
dst_csv = "FF-DST-Stats-{date}.csv".format(date=today)
dst_headers = ["Player", "Team","Int","Yds","TD","Lng","PD","Sk","Comb","Solo","Ast","TFL","QBHits","FR","Yds","TD","FF","Week"]
dst_file = open(dst_csv, "w", newline='')
dst_writer = csv.writer(dst_file)
dst_writer.writerow(dst_headers)

#Create snap count stat CSV file (snaps_csv) and write headers
snaps_csv = "FF-Snaps-Stats-{date}.csv".format(date=today)
snaps_headers = ["Player","Pos","Num","Pct","Num","Pct","Num","Pct","Week","Team"]
snaps_file = open(snaps_csv, "w", newline='')
snaps_writer = csv.writer(snaps_file)
snaps_writer.writerow(snaps_headers)

#Function for scraping offense stats
def Offense():
    #Locate offensive player data and save it to a list to be cleaned
    offense_stats = []
    game_content = gamepage.find("div", id="content", role="main")
    player_off = game_content.find("div", id="all_player_offense")
    all_player_off = player_off.find("tbody")
    for player in all_player_off.find_all("tr"):
        player_stats = player.get_text(separator=',')
        offense_stats.append(player_stats)
    
    #Add missing blank QB rating for non-QBs, eliminate in-table headers and save to off_csv
    for each in offense_stats:
        each_list = each.split(",")
        if len(each_list) < 20 or len(each_list) > 30:
            continue
        elif len(each_list) < 22:
            each_list.insert(10," ")
            each_list.append(week)
            off_writer.writerow(each_list)
        else:
            each_list.append(week)
            off_writer.writerow(each_list)
    off_file.close

#Function for scraping defense stats
def Defense():
   #Locate defensive player data
    dst_stats = []
    game_content = gamepage.find("div", id="content", role="main")
    player_def = game_content.find("div", id="all_player_defense")
    table_def = player_def.find("tbody")
    for player in table_def.find_all("tr"):
        player_stats = player.get_text(separator=',')
        dst_stats.append(player_stats)
     
    #Eliminate in-table headers and save to dst_csv
    for each in dst_stats:
        each_list = each.split(",")
        if len(each_list) < 10 or len(each_list) > 30:
            continue
        else:
            each_list.append(week)
            dst_writer.writerow(each_list)
    dst_file.close 

#Function for scraping snap counts
def Snaps():
    #Locate home team snap count data
    h_snaps_stats = []
    game_content = gamepage.find("div", id="content", role="main")
    player_snaps = game_content.find("div", id="div_home_snap_counts")
    table_snaps = player_snaps.find("tbody")
    for player in table_snaps.find_all("tr"):
        player_stats = player.get_text(separator=',')
        h_snaps_stats.append(player_stats)
     
    #Eliminate in-table headers and save to snaps_csv
    for each in h_snaps_stats:
        each_list = each.split(",")
        if len(each_list) < 7 or len(each_list) > 15:
            continue
        elif "\n" in each_list:
            continue
        else:
            each_list.append(week)
            each_list.append(team_home)
            snaps_writer.writerow(each_list)
            
    #Locate visitor team snap count data
    v_snaps_stats = []
    game_content = gamepage.find("div", id="content", role="main")
    player_snaps = game_content.find("div", id="div_vis_snap_counts")
    table_snaps = player_snaps.find("tbody")
    for player in table_snaps.find_all("tr"):
        player_stats = player.get_text(separator=',')
        v_snaps_stats.append(player_stats)
     
    #Eliminate in-table headers and save to snaps_csv
    for each in v_snaps_stats:
        each_list = each.split(",")
        if len(each_list) < 7 or len(each_list) > 15:
            continue
        elif "\n" in each_list:
            continue
        else:
            each_list.append(week)
            each_list.append(team_vis)
            snaps_writer.writerow(each_list)
    
    snaps_file.close

#Scrape the links to the boxscores of the most recent NFL games
gamelink_list = []
for linktd in homepage.find_all("td", class_="right gamelink"):
    gamelink = str(linktd.a)
    linksplit = gamelink.split("\"")
    gamelink_list.append(site+linksplit[1])

#Iterate through each boxscore link to scrape game-specific stats
for gamelink in gamelink_list:
    browser.get(gamelink)
    time.sleep(5)
    game_html = browser.page_source
    gamepage = BeautifulSoup(game_html, "lxml")

    #Identify teams to append to snap counts
    teams = []
    team_list = gamepage.find("table", id="team_stats").find("tr").get_text(separator=',')
    for each in team_list.split(","):
        if each == "\n":
            continue
        else:
            teams.append(each)
    team_home = teams[1]
    team_vis = teams[0]
 
    #Identify week # to append to all tables
    week_text = gamepage.find("h2").find("a").get_text(separator=',')
    week = week_text.strip("Week ")
    
    Offense() #Scrape offensive stats on current game page
    Defense() #Scrape defensive stats on current game page
    Snaps() #Scrape snap counts on current game page





