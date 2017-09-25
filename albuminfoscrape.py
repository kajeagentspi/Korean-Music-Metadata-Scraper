#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import time

albumId=input("Album ID: ")

source=input("Source : ")
soundquality=input("SQ: ")
albumUrl="http://www.melon.com/album/detail.htm?albumId="
r = requests.get(albumUrl+albumId)
albumData = r.text
albumDataParsed = BeautifulSoup(albumData, "html.parser")
album=albumDataParsed.find('div',class_='wrap_album_info').find('p',class_='albumname').text.replace("\r\n","").replace("\n","").replace("\t","").replace("앨범명","").replace("[EP]","").replace("`","'")
albumartist=albumDataParsed.find('a',class_='atistname').text
year=albumDataParsed.find('dt', string='발매일').nextSibling.nextSibling.text
discnumber="1"
totaltracks=albumDataParsed.find('h3',class_='title first arr').find('span',class_='no').text.replace("(","").replace(")","")
delimiter="  -  "
fo = open (albumId+".txt", 'w', encoding="utf8")
fo.write('\ufeff')
for row in albumDataParsed.find('tbody').find_all('tr'):
	songUrl="http://www.melon.com/song/detail.htm?songId="
	songId=row.find('a',class_="btn btn_icon_detail")['href'].replace("javascript:melon.link.goSongDetail('","").replace("');","")
	r = requests.get(songUrl+songId)
	songData = r.text
	songDataParsed = BeautifulSoup(songData, "html.parser")
	genre=songDataParsed.find('dt', string='장르').nextSibling.nextSibling.text
	track=int(row.find('td', class_='no').text)
	title=row.find('input', class_='input_check')['title'].replace(" 곡 선택","").replace(" (CD Only)","").replace("`","'")
	artist=row.find('div',id="artistName").find('a',class_="fc_mgray").text	
	fo.write('%s%s%s%s%s%s%s%s%02d%s%s%s%s%s%s%s%s%s%s%s%s\n' % (title,delimiter,artist,delimiter,album,delimiter,year,delimiter,track,delimiter,genre,delimiter,albumartist,delimiter,discnumber,delimiter,totaltracks,delimiter,source,delimiter,soundquality))
	time.sleep(2)
fo.close()

# naver
# for row in albumDataParsed.find('ol',class_='song_info_ol').find_all('li'):
# 	row.find('span',class_='info').find('em',string='작사').nextSibling.nextSibling.text
