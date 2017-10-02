#!/usr/bin/python3
from mutagen.flac import Picture, FLAC
from bs4 import BeautifulSoup
from mutagen import File
import requests
import urllib
import time
import os
import re

def parseAlbumID(albumId):
	albumUrl="http://www.melon.com/album/detail.htm?albumId="
	r = requests.get(albumUrl+albumId)
	albumData = r.text
	albumDataParsed = BeautifulSoup(albumData, "html.parser")
	return albumDataParsed

def getAlbumData(albumDataParsed): #Return list of lists
	albumContent=[]
	album=albumDataParsed.find('div',class_='wrap_album_info').find('p',class_='albumname').text.replace("\r\n","").replace("\n","").replace("\t","").replace("앨범명","").replace("[EP]","").replace("`","'").replace("[싱글]","")
	albumartist=albumDataParsed.find('a',class_='atistname').text
	year=albumDataParsed.find('dt', string='발매일').nextSibling.nextSibling.text
	discnumber="1"
	totaltracks=albumDataParsed.find('h3',class_='title first arr').find('span',class_='no').text.replace("(","").replace(")","")
	for i in range (0,int(totaltracks)):
		albumContent+=[{"album":album, "albumartist":albumartist, "year":year, "discnumber":discnumber, "totaltracks":totaltracks, "source":source, "soundquality":soundquality}]
	for row in albumDataParsed.find('tbody').find_all('tr'):
		songId=row.find('a',class_="btn btn_icon_detail")['href'].replace("javascript:melon.link.goSongDetail('","").replace("');","")
		title=row.find('input', class_='input_check')['title'].replace(" 곡 선택","").replace(" (CD Only)","").replace("`","'")
		artist=row.find('div',id="artistName").find('a',class_="fc_mgray").text
		track=row.find('td', class_='no').text.zfill(2)
		albumContent[int(track)-1].update({"title":title,"artist":artist,"track":track})
		albumContent[int(track)-1].update(getSongData(parseSongID(songId),track))
		time.sleep(2)
	return albumContent

def parseSongID(songId):
	songUrl="http://www.melon.com/song/detail.htm?songId="
	r = requests.get(songUrl+songId)
	songData = r.text
	songDataParsed = BeautifulSoup(songData, "html.parser")
	return songDataParsed

def parseAlbumIdNaver(albumIdNaver):
	albumUrl="http://music.naver.com/album/index.nhn?albumId="
	r = requests.get(albumUrl+albumIdNaver)
	albumData = r.text
	albumDataParsed = BeautifulSoup(albumData, "html.parser")
	return albumDataParsed

def getLyricsNaver(albumDataParsed,track):
	songUrl='http://music.naver.com/lyric/index.nhn?trackId='
	songId=albumDataParsed.find('a',class_=re.compile('^_lyric NPI=a:lyric,r:'+str(int(track))))['class'][1].rsplit(':',1)[-1]
	r = requests.get(songUrl+songId)
	songData = r.text
	songDataParsed = BeautifulSoup(songData, "html.parser")
	breaks=songDataParsed.find('div',class_='show_lyrics').find_all('br')
	for br in breaks:
		br.replace_with("\n")
	lyrics=songDataParsed.find('div',class_='show_lyrics').text
	return lyrics

def getSongData(songDataParsed,track):
	lyricist=""
	composer=""
	arranger=""
	lyrics=""
	genre=songDataParsed.find('dt', string='장르').nextSibling.nextSibling.text.split(" / ")
	for row in songDataParsed.find_all('div',class_='box_lyric'):	
		if row.find('dt',string='작사') is not None:
			if lyricist!="":
				lyricist+=", "
				lyricist+=row.find('dd',class_='atist').text
			else:
				lyricist=row.find('dd',class_='atist').text
			continue
		elif row.find('dt',string='작곡') is not None:
			if composer!="":
				composer+=", "
				composer+=row.find('dd',class_='atist').text
			else:
				composer=row.find('dd',class_='atist').text
			continue
		elif row.find('dt',string='편곡 ') is not None:
			if arranger!="":
				arranger+=", "
				arranger+=row.find('dd',class_='atist').text
			arranger=row.find('dd',class_='atist').text
	breaks=songDataParsed.find('div',class_='lyric')
	if breaks is not None:
		breaks=breaks.find_all('br')
		for br in breaks:
			br.replace_with("\n")
		lyrics=songDataParsed.find('div',class_='lyric').text
	else:
		lyrics=getLyricsNaver((parseAlbumIdNaver(albumIdNaver)),track)
	return {"lyricist":lyricist, "composer":composer, "arranger":arranger, "genre":genre ,"lyrics":lyrics}

def getAlbum(albumId):
	return getAlbumData(parseAlbumID(albumId))

def getAlbumArt(albumIdNaver):
	coverlocation=albumIdNaver.zfill(9).strip()
	link='http://musicmeta.phinf.naver.net/album/'.strip()
	link+=coverlocation[0:3].strip()
	link+='/'.strip()
	link+=coverlocation[3:6].strip()
	link+='/'.strip()
	link+=albumIdNaver.strip()
	link+='.jpg'.strip()
	print(albumIdNaver)
	print(link)
	cover=urllib.request.urlopen(link)
	image = Picture()
	image.type=3
	image.mime='image/jpeg'
	image.data=cover.read()
	return image

def addTags(albumIdNaver,albumContent,foldername):
	image=getAlbumArt(albumIdNaver)
	for i in range (0,len(albumContent)):
		for item in os.listdir(foldername):
			if re.search(albumContent[i]['track'],item):
				audio = File(foldername+'/'+item)
				audio.delete()
				audio.clear_pictures()
				audio.add_picture(image)
				for tag,value in albumContent[i].items():
					audio[tag]=value
				audio.save()
			continue


albumId=input("Album ID: ")
albumIdNaver=input("Naver Album ID: ")
source=input("Source : ")
soundquality=input("SQ: ")
foldername=input("Folder Name: ")
print(addTags(albumIdNaver,getAlbum(albumId),foldername))

