import requests
import re
import urllib.request
class YoutubeMp3Downloader:
    """
    Класс принимает строковый запрос, как обычный запрос в строку поиска https://www.youtube.com/results?search_query={}
    Метод get_videoId парсит ID видио по заапросу и возвращает его.
    Метод get_dwnld_link парсит сайт-конвертер и возвращает ссылку на скачивание mp3 в качестве 128 kbps.
    ---
    Планируется добавить возврат размера файла и ограничить размер больших файлов >20Mb https://core.telegram.org/bots/faq#handling-media
    """
    URL_YTB_SEARCH = 'https://www.youtube.com/results?search_query={}'
    URL_CONVERTER = 'https://newconverter.online/convert?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{}'
    URL_DOWNLOADER = 'https://newconverter.online/download/{}'
    URL_SEGMENT = '/mp3/128'
    RAW_LEN_STR = 10  # the raw string looks like this: videoId":"iZEca2A3tS4. the length of the string videoId":" is 10
    YTB_VIDEO_ID_DISTANCE = 30  # https://stackoverflow.com/questions/6180138
    RAW_NAME_TRACK = "<h2 class=\"text-lg text-blue-600 font-bold m-2 text-center\">"
    LEN_RNT = len(RAW_NAME_TRACK)

    def get_videoId(self, query):
        """
        Принимает строку. Простой запрос пользователя. Возвращает строку идентификатор видео с ютуба.
        :param query: string
        :return: string (Id video from youtube)
        """
        r = requests.get(self.URL_YTB_SEARCH.format(query))
        text = r.text
        start = text.find('videoId')
        row_str = text[start + self.RAW_LEN_STR:start + self.YTB_VIDEO_ID_DISTANCE]
        videoID = re.search(r'^[A-Za-z0-9_-]*', row_str).group(0)

        return videoID

    def get_dwnld_link(self, videoId):
        """
        Принимает строку идентификатор видео с ютуба. Возвращает ссылку на скачивание.
        :param videoId: string like that eLa685J5uA8  from https://www.youtube.com/watch?v=eLa685J5uA8
        :return: tuple (link: string, track_name: string, file_size ). Download link like that https://newconverter.online/download/eLa685J5uA8/mp3/128/1674116870/2c3b745627dcb269f9328ce998fd67ac18698967f4bcdf9e2e0e1387e9aac6f7/0
        """
        p = requests.get(self.URL_CONVERTER.format(videoId))
        df = p.text
        start_dl = df.find(self.URL_DOWNLOADER.format(videoId + self.URL_SEGMENT))  # start position of download link
        dl_raw = df[start_dl:start_dl + 150]
        dl = re.search(r'[^\"]*', dl_raw).group(0)
        start_dl = df.find(self.RAW_NAME_TRACK)
        raw_track_name = df[start_dl + self.LEN_RNT:]
        end_track_name = raw_track_name.find('</h2')
        track_name = raw_track_name[:end_track_name]

        #show file size
        fs = df[:]
        for _ in range(8):
            fs = fs[fs.find("<div class=\"text-shadow-1\">") + 27:]
        fs = fs[:fs.find("</div>")]
        return dl, track_name, fs
