######################################################################################
#
#	XMovies8.tv - v0.01
#
######################################################################################

TITLE = "XMovies8"
PREFIX = "/video/xmovies8"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://xmovies8.co"
MOVIES_URL = "http://xmovies8.co"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
	HTTP.Headers['Referer'] = 'xmovies8.co'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	page_data = HTML.ElementFromURL(BASE_URL)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	
	for each in page_data.xpath("//li[contains(@class,'cat-item')]"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/text()")[0]

		if title != "Animation":
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, category = title, page_count=1),
				title = title,
				thumb = R(ICON_MOVIES)
				)
			)
	return oc

######################################################################################
@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page_data = HTML.ElementFromURL(BASE_URL + '/movie-genre/' + str(category) + '/page/' + str(page_count))
	
	for each in page_data.xpath("//div[@class='article-image']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/@title")[0]
		thumb = each.xpath("./a/img/@src")[0]

		if "Season" in title:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-series.png')
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = BASE_URL + thumb
				)
			)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = category, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Creates page url from tv episodes and creates objects from that page

@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page_data = HTML.ElementFromURL(url)
	thumb = page_data.xpath("//div[@class='article-image']/img/@src")[0]
	maintitle = page_data.xpath("//meta[@property='og:title']/@content")[0].replace('Xmovies8: ','',1).replace(' full movie Putlocker HD','',1).strip()
	for each in page_data.xpath("//ul[@class='movie-parts']/li"):
		url = each.xpath("./a/@href")[0]
		title = maintitle + 'Episode ' + each.xpath("./a/text()")[0]
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
	
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page_data = HTML.ElementFromURL(url)
	title = page_data.xpath("//meta[@property='og:title']/@content")[0].replace('Xmovies8: ','',1).replace(' full movie Putlocker HD','',1).strip()
	try:
		description = page_data.xpath("//span[@class='metaContent'][3]/text()")[0]
	except:
		description = page_data.xpath("//span[@class='metaContent'][2]/text()")[0]
	thumb = page_data.xpath("//div[@class='article-image']/img/@src")[0]
	
	oc.add(VideoClipObject(
		url = url,
		title = title,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
		summary = description
		)
	)	

	return oc

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(BASE_URL + '/?s=%s' % String.Quote(query, usePlus=True), headers="").content

	html = HTML.ElementFromString(data)

	for movie in html.xpath("//div[@class='post-panel']"):
		url = movie.xpath("./div/a/@href")[0]
		title = movie.xpath("./div[@class='inner']/h2/a/text()")[0]
		thumb = movie.xpath("./div[@class='post-thumbnail']/a/img/@src")[0]
		if "Season" in title:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-series.png')
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = BASE_URL + thumb
				)
			)

	return oc
