import requests
import json
from contextlib import contextmanager
import time
from itertools import chain, combinations, permutations
import instaloader
from instaloader.exceptions import ConnectionException, InstaloaderException, LoginRequiredException
import re


class Bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    WHITE = '\033[37m'


@contextmanager
def FileManager(path, methods, encod):
    try:
        file = open(path, methods, encoding=encod)
        yield file
    finally:
        file.close()

class Scanner:
    
    def __init__(self):
        self.instagram_usernames = list()
        self.loader = instaloader.Instaloader()
    
    def kullanici_bilgileri(self):
        
        with open("olasi_kullanici_adlari.txt", "r") as file:
            lines = file.readlines()
            self.instagram_usernames = [line.split("https://instagram.com/")[1].strip() for line in lines if "https://instagram.com/" in line]

        for kullanici_adi in self.instagram_usernames:
            try:
                profile = instaloader.Profile.from_username(self.loader.context, kullanici_adi)
                with FileManager("olasi_kullanici_bilgileri.txt" , "a+", "utf-8") as file:
                    file.write("Kullanıcı Adı: " + str(profile.username) + '\n')
                    file.write("Takipçi Sayısı: " + str(profile.followers) + '\n')
                    file.write("Takip Edilen Sayısı: " + str(profile.followees) + '\n')
                    file.write("Gönderi Sayısı: " + str(profile.mediacount) + '\n')
                    file.write("Biografisi: " + str(profile.biography) + '\n')
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
                    file.write("                                 AJANX TOOLS                               \n")
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            except instaloader.exceptions.ProfileHasNoPicsException:
                print(Bcolors.RED +f"Kullanıcı adı bulunamadı: {kullanici_adi}" + Bcolors.ENDC)
                
                
    def gonderileri_indir(self):
        
        for kullanici_adi in self.instagram_usernames:
            try:
                profile = instaloader.Profile.from_username(self.loader.context, kullanici_adi)
            
                for post in profile.get_posts():
                    self.loader.download_post(post, target=profile.username)
            except instaloader.exceptions.ProfileHasNoPicsException:
                print(Bcolors.RED + f"Kullanıcı adı bulunamadı: {kullanici_adi}" + Bcolors.ENDC)
                
    def hastag(self, hastag):
        
        for post in self.loader.get_hashtag_posts(hastag):
            self.loader.download_post(post, target=hastag)
            
            
    def post_detayli_bilgi(self, post_url):
        match = re.search(r'/p/([^/?]+)', post_url)
        try:
            username = input( Bcolors.YELLOW +"Lütfen kullanıcı adınızı giriniz: " + Bcolors.ENDC)
            password = input( Bcolors.YELLOW + "Lütfen şifrenizi giriniz: " + Bcolors.ENDC)
            self.loader.context.login(username,password)
            if match:
                post = instaloader.Post.from_shortcode(L.context, match)
            
                with FileManager("post_detayli_bilgi.txt", "w", "utf-8") as file:
                    file.write("Gönderiyi Beğenen Kullanıcılar\n\n")
                    for like in post.get_likes():
                        file.write(like.username)
                    
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
                    file.write("                                 AJANX TOOLS                               \n")
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n")

                with FileManager("post_detayli_bilgi.txt", "w", "utf-8") as file:
                    file.write("Gönderiye Gelen Yorumlar\n\n")
                
                    for comment in post.get_comments():
                        file.write(comment.owner.username, comment.text)
                    
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
                    file.write("                                 AJANX TOOLS                               \n")
                    file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
        
        except InstaloaderException as ex:
            print(Bcolors.RED + f"Giriş başarısız. Hata: {ex}" + Bcolors.ENDC)
            exit()       

        
class Instagram:

    def __init__(self, config, permutations_list):
        self.delay = config['plateform']['instagram']['rate_limit'] / 1000
        self.format = config['plateform']['instagram']['format']
        self.permutations_list = permutations_list
        self.kullanici_adi_listesi = list()

    def possible_usernames(self):
        possible_usernames = []
        for permutation in self.permutations_list:
            possible_usernames.append(self.format.format(permutation=permutation))
        return possible_usernames

    def search(self):
        instagram_usernames = {"accounts": []}
        bibliogram_URL = "https://bibliogram.art/u/{}"
        possible_usernames_list = self.possible_usernames()

        for username in possible_usernames_list:
            try:
                bibliogram_formatted_URL = bibliogram_URL.format(username.replace("https://instagram.com/", ""))
                r = requests.get(bibliogram_formatted_URL)
            except requests.ConnectionError:
                print(Bcolors.RED +"Failed to connect to Instagram"+ Bcolors.ENDC)

            if r.status_code == 200:
                instagram_usernames["accounts"].append({"value": username})
                print(Bcolors.RED + f"Found username: {username}"+ Bcolors.ENDC)

            time.sleep(self.delay)

        with FileManager("olasi_kullanici_adlari.txt", "w", "utf-8") as file:
            for kullanici_adi in instagram_usernames["accounts"]:
                file.write(kullanici_adi["value"] + '\n')
        with FileManager("olasi_kullanici_adlari.txt", "a+", "utf-8") as file:
            icerik = file.read()
            icerik.strip("https://instagram.com/")
        
        print("Finished searching")

class Core:

    def __init__(self, config_path, items):
        with open(config_path, 'r') as f:
            self.CONFIG = json.load(f)
        self.items = items
        self.permutations_list = []

    def config(self):
        return self.CONFIG

    def get_permutations(self):
        combinations_list = list(chain(*map(lambda x: combinations(self.items, x), range(1, len(self.items) + 1))))
        for combination in combinations_list:
            for perm in list(permutations(combination)):
                self.permutations_list.append("".join(perm))

    def instagram(self):
        try:
            Instagram(self.CONFIG, self.permutations_list).search()
        except ConnectionException as e:
            print(Bcolors.RED + f"Hata: {e}" + Bcolors.ENDC)
            print(Bcolors.RED + "Çok fazla istek gönderdiğiniz için geçici olarak engellendiniz. Lütfen bir süre sonra tekrar deneyin." + Bcolors.ENDC)
        except LoginRequiredException as e:
            print(Bcolors.RED + f"Hata: {e}" + Bcolors.ENDC)
            print(Bcolors.RED +"Instagram hesabınıza giriş yapmanız gerekiyor." + Bcolors.ENDC)
            self.login_instaloader()


def userosint():
    ad_soyad_username = input( Bcolors.YELLOW + "Lütfen ad, soyad ve kullanıcı adınızı boşluk bırakarak girin: " + Bcolors.ENDC)
    items = ad_soyad_username.split()
    config_path = "config.json"  # Replace with your config file path
    core = Core(config_path, items)
    core.get_permutations()
    print(Bcolors.RED +"\nOlası Kullanıcı Adları Oluşturuluyor!!" + Bcolors.ENDC)
    core.instagram()

    getir = Scanner()
    try:
        print(Bcolors.RED +"Kullanıcı bilgileri getiriliyor....\n" + Bcolors.ENDC)

        getir.kullanici_bilgileri()
        
        print(Bcolors.RED +"Kullanıcı Bilgileri TXT Dosyasına Kayıt Edildi.\n" + Bcolors.ENDC)
        print(Bcolors.RED +"Kullanıcı Gönderileri İndiriliyor...\n" + Bcolors.ENDC)
        
        getir.gonderileri_indir()
        
        print(Bcolors.YELLOW +"Kullanıcı Gönderileri İndirildi.\n" + Bcolors.ENDC)
    except instaloader.exceptions.LoginRequiredException:
        print(Bcolors.RED + "Fazla istek gönderdiğiniz için yetkisizleştirildiniz lütfen giriş yapın." + Bcolors.ENDC)
        try:
            L = instaloader.Instaloader()
            username = input(Bcolors.YELLOW +"Lütfen kullanıcı adınızı giriniz: " + Bcolors.ENDC)
            password = input(Bcolors.YELLOW +"Lütfen şifrenizi giriniz: "+ Bcolors.ENDC )
            L.context.login(username, password)
            
                
            print(Bcolors.RED + "Kullanıcı bilgileri getiriliyor....\n"+ Bcolors.ENDC )
    
            getir.kullanici_bilgileri()
    
            print(Bcolors.GREEN + "Kullanıcı Bilgileri TXT Dosyasına Kayıt Edildi.\n" + Bcolors.ENDC)
            print(Bcolors.RED + "Kullanıcı Gönderileri İndiriliyor...\n" + Bcolors.ENDC)
            getir.gonderileri_indir()
            print(Bcolors.GREEN  + "Kullanıcı Gönderileri İndirildi.\n" + Bcolors.ENDC )
            
        except InstaloaderException as ex:
            print(Bcolors.RED + f"Giriş başarısız. Hata: {ex}" + Bcolors.ENDC)
            exit()


def hastagosint(hastag):
    getir = Scanner()
    try:
        print(Bcolors.RED +f"{hastag} ile ilgili veriler çekiliyor....\n" + Bcolors.ENDC)
        getir.hastag(hastag)
        print(Bcolors.GREEN + f"{hastag} ile ilgili veriler çekildi!" + Bcolors.ENDC)
    except Exception as e:
        print(Bcolors.RED + f"Veriler Çekilemedi. HATA: {e}" + Bcolors.ENDC)
    
def detayli_post_osint(post_url):
    getir = Scanner()
    try:
        print(Bcolors.RED +"Gönderiye ait detaylı bilgiler çekiliyor..." + Bcolors.ENDC)
        getir.post_detayli_bilgi(post_url)
        print(Bcolors.GREEN + "Gönderiye ait detaylı bilgiler çekildi" + Bcolors.ENDC)
    except Exception as e:
        print(Bcolors.RED + f"Veriler Çekilemedi. HATA: {e}" + Bcolors.ENDC)

    
    
    