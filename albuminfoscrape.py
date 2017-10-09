#!/usr/bin/python3
from mutagen.flac import Picture, FLAC
from bs4 import BeautifulSoup
from mutagen import File
import requests
import urllib
import time
import os
import re


def dataGrab(url):
	r = requests.get(url)
	data = r.text
	return BeautifulSoup(data, "html.parser")

def naverSearch(artist,albumName):
	naverSearchURL="http://music.naver.com/search/search.nhn?query="
	naverSearchData=dataGrab(naverSearchURL+artist+"+"+albumName+"&target=album")
	return naverSearchData.find('a',class_='btn_play')['onclick'].split('(')[1].split(',')[0]

def melonSearch(artist,albumName):
	melonSearchURL="http://www.melon.com/search/album/index.htm?q="
	melonSearchData = dataGrab(melonSearchURL+artist+"+"+albumName)
	return melonSearchData.find('a',class_="ellipsis")['href'].split(";")[1].split("'")[1]

def getMelonAlbumData(melonAlbumID):
	melonAlbumURL="http://www.melon.com/album/detail.htm?albumId="
	melonAlbumData=dataGrab(melonAlbumURL+melonAlbumID)
	return melonAlbumData

def getNaverAlbumData(naverAlbumID):
	naverAlbumURL="http://music.naver.com/album/index.nhn?albumId="
	naverAlbumData=dataGrab(naverAlbumURL+naverAlbumID)
	return naverAlbumData

def getMelonSongData(melonSongID):
	melonSongURL="http://www.melon.com/song/detail.htm?songId="
	melonSongData=dataGrab(melonSongURL+melonSongID)
	return melonSongData

def getNaverSongData(naverSongID):
	naverSongURL="http://music.naver.com/lyric/index.nhn?trackId="
	naverSongData=dataGrab(naverSongURL+naverSongID)
	return naverSongData

def getAlbumTags(naverAlbumID,melonAlbumData):
	albumTag=[]
	album=melonAlbumData.find('div',class_='wrap_album_info').find('p',class_='albumname').text.replace("\r\n","").replace("\n","").replace("\t","").replace("앨범명","").replace("[EP]","").replace("`","'").replace("[싱글]","")
	albumartist=melonAlbumData.find('a',class_='atistname').text.split(", ")
	year=melonAlbumData.find('dt', string='발매일').nextSibling.nextSibling.text
	discnumber="1"
	totaltracks=melonAlbumData.find('h3',class_='title first arr').find('span',class_='no').text.replace("(","").replace(")","")
	for i in range (0,int(totaltracks)):
		albumTag+=[{"album":album, "albumartist":albumartist, "year":year, "discnumber":discnumber, "totaltracks":totaltracks}]
	for row in melonAlbumData.find('tbody').find_all('tr'):
		melonSongID=row.find('a',class_="btn btn_icon_detail")['href'].replace("javascript:melon.link.goSongDetail('","").replace("');","")

		title=row.find('input', class_='input_check')['title'].replace(" 곡 선택","").replace("`","'")
		if "(CD Only)" in title:
			source="CD"
			title=title.replace(" (CD Only)","")
		else:
			source="WEB"
		artist=row.find('div',id="artistName").find('a',class_="fc_mgray").text
		track=row.find('td', class_='no').text.zfill(2)
		albumTag[int(track)-1].update({"title":title,"artist":artist,"track":track,"source":source})
		albumTag[int(track)-1].update(getMelonSong(naverAlbumID,getMelonSongData(melonSongID),track))
		time.sleep(2)
	return albumTag

def getMelonSong(naverAlbumID,melonSongData,track):
	lyricist=[]
	composer=[]
	arranger=[]
	lyrics=""
	genre=melonSongData.find('dt', string='장르').nextSibling.nextSibling.text.split(" / ")

	for row in melonSongData.find_all('div',class_='box_lyric'):	
		if row.find('dt',string='작사') is not None:
			lyricist+=[row.find('dd',class_='atist').text]
			continue
		elif row.find('dt',string='작곡') is not None:
			composer+=[row.find('dd',class_='atist').text]
			continue
		elif row.find('dt',string='편곡 ') is not None:
			arranger+=[row.find('dd',class_='atist').text]

	breaks=melonSongData.find('div',class_='lyric')

	lyrics=getLyricsNaver((getNaverAlbumData(naverAlbumID)),track)
		
	return {"lyricist":lyricist, "composer":composer, "arranger":arranger, "genre":genre ,"lyrics":lyrics}

def getLyricsNaver(naverAlbumData,track):
	naverSongID=naverAlbumData.find_all('tr',class_=re.compile('^_tracklist_move'))[int(track)]['trackdata'].split("|")[0]
	if naverSongID is None:
		return ""
	naverSongData=getNaverSongData(naverSongID)
	lyricsDiv=naverSongData.find('div',class_='show_lyrics')
	if lyricsDiv is None:
		return ""
	else:
		breaks=lyricsDiv.find_all('br')
	for br in breaks:
		br.replace_with("\n")
	lyrics=naverSongData.find('div',class_='show_lyrics').text.replace("`","'")
	return lyrics

def itunesGetAlbumArt(artist, albumName):
	itunesSearchURL="https://itunes.apple.com/search?term="
	itunesParameters="&country=ph&entity=album&limit=1&callback=jQuery111208656545422876729_1507203610992&_=1507203610993"
	itunesSearchData = dataGrab(itunesSearchURL+artist+"+"+albumName+itunesParameters)
	return itunesSearchData.text.split("artworkUrl60\":\"")[1].split("\", \"artworkUrl100")[0].replace("60x60bb","100000x100000-999")

def naverGetAlbumArt(naverAlbumID):
	coverlocation=naverAlbumID.zfill(9).strip()
	link='http://musicmeta.phinf.naver.net/album/'.strip()
	link+=coverlocation[0:3].strip()
	link+='/'.strip()
	link+=coverlocation[3:6].strip()
	link+='/'.strip()
	link+=naverAlbumID.strip()
	link+='.jpg'.strip()
	return link

def getAlbumArt(naverAlbumID, artist, albumName):
	link=itunesGetAlbumArt(artist, albumName)
	if link=="":
		link=naverGetAlbumArt(naverAlbumID)
	cover=urllib.request.urlopen(link)
	albumArt = Picture()
	albumArt.type=3
	albumArt.mime='image/jpeg'
	albumArt.data=cover.read()
	return albumArt

def tagToFile(albumTag,albumArt,folderName):
	for i in range (0,len(albumTag)):
		for item in os.listdir(folderName):
			if re.search(albumTag[i]['track'],item):
				audio = File(folderName+'/'+item)
				audio.delete()
				audio.clear_pictures()
				audio.add_picture(albumArt)
				for tag,value in albumTag[i].items():
					audio[tag]=value
				audio.save()
			continue

def main(artist,albumName,folderName):
	naverAlbumID=naverSearch(artist,albumName)
	melonAlbumID=melonSearch(artist,albumName)
	albumTag=getAlbumTags(naverAlbumID,getMelonAlbumData(melonAlbumID))
	albumArt=getAlbumArt(naverAlbumID, artist, albumName)
	tagToFile(albumTag,albumArt,folderName)

artist=input("Artist: ")
albumName=input("Album: ")
folderName=input("Folder: ")
main(artist,albumName,folderName)
