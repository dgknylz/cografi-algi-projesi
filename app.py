import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.affinity import translate
import os
import altair as alt 
import pandas as pd

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Coğrafi Algı Farkındalık", layout="wide", page_icon="🌍")

# --- 2. TASARIM ---
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #E63946; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    .sub-title { font-size: 1.5rem; color: #457b9d; text-align: center; margin-bottom: 20px; }
    .info-box { background-color: #F1FAEE; padding: 25px; border-radius: 15px; border-left: 5px solid #E63946; text-align: justify; font-size: 1.1rem; color: #1D3557; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); line-height: 1.6; }
    .fact-box { background-color: #e0f7fa; padding: 15px; border-radius: 10px; border: 1px solid #4dd0e1; color: #006064; font-size: 1rem; margin-top: 10px; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; text-align: center; color: #000000 !important; }
    div[data-testid="stMetricLabel"] p { color: #000000 !important; }
    div[data-testid="stMetricValue"] div { color: #000000 !important; }
    .sidebar-title { font-size: 1.5rem; font-weight: bold; color: #1D3557; }
</style>
""", unsafe_allow_html=True)

# --- 3. BAŞLIK VE AÇIKLAMA (GÜNCELLENDİ) ---
st.markdown('<p class="main-title">Coğrafi Algı Yanılsamasına Yönelik<br>Farkındalık Uygulaması</p>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    "Bu web Uygulaması, <b>Türkiye Merkezli Gerçek Alanlı Harita Oluşturma Çalışması</b>" kapsamında geliştirilmiştir.<br><br>
    Ülkelerin ekvator referanslı gerçek alanlarının, bazı harita projeksiyonlarına göre çizimleri sonucunda oluşan görüntüleriyle karşılaştırma yapmak ve bu konuda farkındalık oluşturmak amacıyla kullanılmaktadır.
</div>
""", unsafe_allow_html=True)

# --- 4. VERİ YÜKLEME ---
@st.cache_data
def load_data():
    if not os.path.exists("dunya.json"):
        st.error("⚠️ 'dunya.json' dosyası bulunamadı! Lütfen GitHub'a yüklediğinden emin ol.")
        return gpd.GeoDataFrame()

    world = gpd.read_file("dunya.json")
    world = world[world.geometry.notnull()]

    # Alan Hesaplamaları
    gdf_equal = world.to_crs({'proj':'cea'}) 
    world['gercek_alan_km2'] = gdf_equal.geometry.area / 10**6
    
    gdf_merc = world.to_crs("EPSG:3857")
    world['mercator_alan_km2'] = gdf_merc.geometry.area / 10**6
    
    world['bozulma_orani'] = ((world['mercator_alan_km2'] - world['gercek_alan_km2']) / world['gercek_alan_km2']) * 100
    world['kat_farki'] = world['mercator_alan_km2'] / world['gercek_alan_km2']
    
    return world

gdf = load_data()

# --- 5. ÜLKE LİSTESİ ---
ulke_listesi = [
    {"dosya": "1.Türkiye-removebg-preview.png", "geo_name": "Turkey", "ad": "Türkiye 🇹🇷", "bilgi": "Asya ve Avrupa'yı birbirine bağlayan köprüdür. Mercator haritasında olduğundan biraz daha büyük görünür."},
    {"dosya": "ABD-removebg-preview.png", "geo_name": "United States of America", "ad": "ABD", "bilgi": "Dünyanın en büyük 4. ülkesidir. Alaska eyaleti haritalarda devasa görünse de aslında o kadar büyük değildir."},
    {"dosya": "Alaska-removebg-preview.png", "geo_name": "United States of America", "ad": "Alaska (ABD)", "bilgi": "Haritalarda Afrika kıtası kadar büyük görünür ama aslında Türkiye'nin sadece 2 katı büyüklüğündedir."},
    {"dosya": "Afganistan-removebg-preview.png", "geo_name": "Afghanistan", "ad": "Afganistan", "bilgi": "Asya'nın kalbinde yer alan dağlık bir ülkedir."},
    {"dosya": "Almanya-removebg-preview.png", "geo_name": "Germany", "ad": "Almanya", "bilgi": "Avrupa'nın sanayi devidir. Haritada konumu gereği olduğundan biraz daha büyük algılanır."},
    {"dosya": "Angola-removebg-preview.png", "geo_name": "Angola", "ad": "Angola", "bilgi": "Afrika'nın güneybatısında yer alır. Ekvator'a yakın olduğu için haritadaki boyutu gerçeğe çok yakındır."},
    {"dosya": "Antarktika-removebg-preview.png", "geo_name": "Antarctica", "ad": "Antarktika", "bilgi": "Dünyanın en büyük yanılgısıdır! Haritada bütün alt tarafı kaplar ama aslında o kadar devasa değildir."},
    {"dosya": "Arjantin-removebg-preview.png", "geo_name": "Argentina", "ad": "Arjantin", "bilgi": "Güney Amerika'nın en güney ucundadır. Kutuplara yakın olduğu için haritada olduğundan büyük görünür."},
    {"dosya": "Avustralya-removebg-preview.png", "geo_name": "Australia", "ad": "Avustralya", "bilgi": "Kıta büyüklüğünde bir ülkedir. Genellikle haritada olduğundan daha küçük olduğu sanılır ama devasadır."},
    {"dosya": "Avusturya-removebg-preview.png", "geo_name": "Austria", "ad": "Avusturya", "bilgi": "Orta Avrupa'da yer alan, Alplerle kaplı dağlık bir ülkedir."},
    {"dosya": "BAE-removebg-preview.png", "geo_name": "United Arab Emirates", "ad": "Birleşik Arap Emirlikleri", "bilgi": "Çöl üzerine kurulmuş modern şehirleriyle tanınır. Ekvator'a yakın sayılır."},
    {"dosya": "Bangladeş-removebg-preview.png", "geo_name": "Bangladesh", "ad": "Bangladeş", "bilgi": "Dünyanın nüfus yoğunluğu en yüksek ülkelerinden biridir. Haritada küçük görünür ama nüfusu devasadır."},
    {"dosya": "Belarus-removebg-preview.png", "geo_name": "Belarus", "ad": "Belarus", "bilgi": "Doğu Avrupa'da denize kıyısı olmayan, ormanlarla kaplı bir ülkedir."},
    {"dosya": "Belçika-removebg-preview.png", "geo_name": "Belgium", "ad": "Belçika", "bilgi": "Batı Avrupa'nın küçük ama siyasi açıdan önemli merkezidir."},
    {"dosya": "Bolivya-removebg-preview.png", "geo_name": "Bolivia", "ad": "Bolivya", "bilgi": "Dünyanın en yüksek rakımlı başkentine (La Paz) sahip ülkesidir."},
    {"dosya": "Bostvana-removebg-preview.png", "geo_name": "Botswana", "ad": "Botsvana", "bilgi": "Afrika'da fillerin en yoğun yaşadığı ülkelerden biridir."},
    {"dosya": "Brezilya-removebg-preview.png", "geo_name": "Brazil", "ad": "Brezilya", "bilgi": "Güney Amerika'nın devi. Ekvator üzerinde olduğu için haritadaki boyutu gerçeği yansıtır."},
    {"dosya": "Bulgaristan-removebg-preview.png", "geo_name": "Bulgaria", "ad": "Bulgaristan", "bilgi": "Balkanların tarihi ve doğasıyla ünlü komşumuzdur."},
    {"dosya": "Burkina_Faso-removebg-preview.png", "geo_name": "Burkina Faso", "ad": "Burkina Faso", "bilgi": "Batı Afrika'da yer alan, denize kıyısı olmayan bir ülkedir."},
    {"dosya": "Cazeyir-removebg-preview.png", "geo_name": "Algeria", "ad": "Cezayir", "bilgi": "Afrika kıtasının yüzölçümü bakımından en büyük ülkesidir."},
    {"dosya": "Çad-removebg-preview.png", "geo_name": "Chad", "ad": "Çad", "bilgi": "Orta Afrika'da yer alır, adını büyük Çad Gölü'nden alır."},
    {"dosya": "Çek_Cumhuriyeti-removebg-preview.png", "geo_name": "Czech Republic", "ad": "Çek Cumhuriyeti", "bilgi": "Orta Avrupa'nın kalbinde, kaleleriyle ünlü bir ülkedir."},
    {"dosya": "Çin-removebg-preview.png", "geo_name": "China", "ad": "Çin", "bilgi": "Dünyanın en kalabalık ülkelerinden biridir. Haritada boyutu genelde doğru algılanır."},
    {"dosya": "Danimarka-removebg-preview.png", "geo_name": "Denmark", "ad": "Danimarka", "bilgi": "Küçük bir ülkedir ama Grönland adası ona bağlı olduğu için haritada devasa bir alana hükmeder."},
    {"dosya": "Demokratik_Kongo_Cumhuriyeti-removebg-preview.png", "geo_name": "Democratic Republic of the Congo", "ad": "Demokratik Kongo Cum.", "bilgi": "Afrika'nın tam kalbinde, yağmur ormanlarıyla kaplı devasa bir ülkedir."},
    {"dosya": "Ekvador-removebg-preview.png", "geo_name": "Ecuador", "ad": "Ekvador", "bilgi": "İsmini Ekvator çizgisinden alır. Haritada bozulmanın en az olduğu ülkelerden biridir."},
    {"dosya": "Ekvator_Ginesi-removebg-preview.png", "geo_name": "Equatorial Guinea", "ad": "Ekvator Ginesi", "bilgi": "Afrika'nın en küçük ama petrol zengini ülkelerinden biridir."},
    {"dosya": "Endonezya-removebg-preview.png", "geo_name": "Indonesia", "ad": "Endonezya", "bilgi": "Binlerce adadan oluşan dünyanın en büyük ada ülkesidir. Ekvator üzerindedir."},
    {"dosya": "Eritre-removebg-preview.png", "geo_name": "Eritrea", "ad": "Eritre", "bilgi": "Kızıldeniz kıyısında, Doğu Afrika'da yer alan tarihi bir ülkedir."},
    {"dosya": "Estonya-removebg-preview.png", "geo_name": "Estonia", "ad": "Estonya", "bilgi": "Baltık ülkelerinin dijitalleşmede en ileri olanıdır."},
    {"dosya": "Etiyopya-removebg-preview.png", "geo_name": "Ethiopia", "ad": "Etiyopya", "bilgi": "Afrika'nın sömürgeleştirilememiş ender ülkelerinden biridir, kahvenin ana vatanıdır."},
    {"dosya": "Fas-removebg-preview.png", "geo_name": "Morocco", "ad": "Fas", "bilgi": "Afrika'nın Avrupa'ya en yakın noktasıdır. Çölleri ve pazarlarıyla ünlüdür."},
    {"dosya": "Filipinler-removebg-preview.png", "geo_name": "Philippines", "ad": "Filipinler", "bilgi": "Pasifik Okyanusu'nda 7.000'den fazla adadan oluşur."},
    {"dosya": "Filistin-removebg-preview.png", "geo_name": "Palestine", "ad": "Filistin", "bilgi": "Ortadoğu'nun tarihi ve kutsal topraklarına ev sahipliği yapar."},
    {"dosya": "Finlandiya-removebg-preview.png", "geo_name": "Finland", "ad": "Finlandiya", "bilgi": "Kuzeyde olduğu için haritada olduğundan çok daha büyük görünür. Göller ülkesidir."},
    {"dosya": "Fransa-removebg-preview.png", "geo_name": "France", "ad": "Fransa", "bilgi": "Batı Avrupa'nın yüzölçümü bakımından en büyük ülkesidir."},
    {"dosya": "Gabon-removebg-preview.png", "geo_name": "Gabon", "ad": "Gabon", "bilgi": "Doğası çok iyi korunmuş, ormanlarla kaplı bir Afrika ülkesidir."},
    {"dosya": "Grönland-removebg-preview.png", "geo_name": "Greenland", "ad": "Grönland (Devasa Hata!)", "bilgi": "Mercator haritasının en büyük yalanıdır! Afrika kadar görünür ama aslında Afrika'nın 14'te 1'idir."},
    {"dosya": "Guatamala-removebg-preview.png", "geo_name": "Guatemala", "ad": "Guatemala", "bilgi": "Orta Amerika'da Maya medeniyetinin beşiğidir."},
    {"dosya": "Güney_Afrika-removebg-preview.png", "geo_name": "South Africa", "ad": "Güney Afrika", "bilgi": "Afrika kıtasının en güney ucundadır. Üç farklı başkenti vardır."},
    {"dosya": "Güney_Kore-removebg-preview.png", "geo_name": "South Korea", "ad": "Güney Kore", "bilgi": "Teknoloji devidir. Haritada küçük görünse de etkisi büyüktür."},
    {"dosya": "Güney_Sudan-removebg-preview.png", "geo_name": "South Sudan", "ad": "Güney Sudan", "bilgi": "Dünyanın en genç ülkelerinden biridir (2011'de kuruldu)."},
    {"dosya": "Gürcistan-removebg-preview.png", "geo_name": "Georgia", "ad": "Gürcistan", "bilgi": "Kafkaslarda yer alan, doğasıyla ünlü komşumuzdur."},
    {"dosya": "Hindistan-removebg-preview.png", "geo_name": "India", "ad": "Hindistan", "bilgi": "Dünyanın en kalabalık ülkesidir. Ekvator'a yakındır, haritada boyutu nispeten doğrudur."},
    {"dosya": "Hırvatistan-removebg-preview.png", "geo_name": "Croatia", "ad": "Hırvatistan", "bilgi": "Adriyatik Denizi kıyısındaki adalarıyla ünlüdür. 'Game of Thrones' burada çekilmiştir."},
    {"dosya": "Honduras-removebg-preview.png", "geo_name": "Honduras", "ad": "Honduras", "bilgi": "Orta Amerika'da, Karayip Denizi'ne kıyısı olan tropikal bir ülkedir."},
    {"dosya": "Irak-removebg-preview.png", "geo_name": "Iraq", "ad": "Irak", "bilgi": "Mezopotamya medeniyetlerinin doğduğu topraklardır."},
    {"dosya": "İngiltere-removebg-preview.png", "geo_name": "United Kingdom", "ad": "İngiltere", "bilgi": "Kuzeyde yer aldığı için haritada olduğundan daha büyük görünür."},
    {"dosya": "İran-removebg-preview.png", "geo_name": "Iran", "ad": "İran", "bilgi": "Ortadoğu'nun yüzölçümü büyük ve dağlık ülkelerinden biridir."},
    {"dosya": "İrlanda-removebg-preview.png", "geo_name": "Ireland", "ad": "İrlanda", "bilgi": "Yeşil doğasıyla 'Zümrüt Ada' olarak bilinir."},
    {"dosya": "İspanya-removebg-preview.png", "geo_name": "Spain", "ad": "İspanya", "bilgi": "Avrupa'nın güneybatısında yer alır, turizm merkezidir."},
    {"dosya": "İsveç-removebg-preview.png", "geo_name": "Sweden", "ad": "İsveç", "bilgi": "İskandinav ülkesidir. Kutuplara yakınlığı nedeniyle haritada devasa görünür ama o kadar büyük değildir."},
    {"dosya": "İsviçre-removebg-preview.png", "geo_name": "Switzerland", "ad": "İsviçre", "bilgi": "Alplerin zirvesinde yer alan tarafsızlığıyla ünlü ülkedir."},
    {"dosya": "İtalya-removebg-preview.png", "geo_name": "Italy", "ad": "İtalya", "bilgi": "Haritada çizme şekliyle hemen tanınır. Tarih ve sanat merkezidir."},
    {"dosya": "İzlanda-removebg-preview.png", "geo_name": "Iceland", "ad": "İzlanda", "bilgi": "Ateş ve buz ülkesi. Kuzeyde olduğu için haritada olduğundan çok daha büyük görünür."},
    {"dosya": "Japonya-removebg-preview.png", "geo_name": "Japan", "ad": "Japonya", "bilgi": "Pasifik'te bir ada ülkesidir. Haritada küçük dursa da uzunluğu Türkiye'den fazladır."},
    {"dosya": "Kamerun-removebg-preview.png", "geo_name": "Cameroon", "ad": "Kamerun", "bilgi": "Coğrafi çeşitliliği nedeniyle 'Minyatür Afrika' olarak bilinir."},
    {"dosya": "Kamboçya-removebg-preview.png", "geo_name": "Cambodia", "ad": "Kamboçya", "bilgi": "Angkor Wat tapınaklarıyla ünlü Güneydoğu Asya ülkesidir."},
    {"dosya": "Kanada-removebg-preview.png", "geo_name": "Canada", "ad": "Kanada (Devasa Hata!)", "bilgi": "Haritada Güney Amerika kadar görünür ama aslında çok daha küçüktür. En büyük bozulmalardan biridir."},
    {"dosya": "Kazakistan-removebg-preview.png", "geo_name": "Kazakhstan", "ad": "Kazakistan", "bilgi": "Dünyanın denize kıyısı olmayan en büyük ülkesidir."},
    {"dosya": "Kenya-removebg-preview.png", "geo_name": "Kenya", "ad": "Kenya", "bilgi": "Ekvator çizgisinin tam üzerinden geçtiği, safarileriyle ünlü ülkedir."},
    {"dosya": "Kırgızistan-removebg-preview.png", "geo_name": "Kyrgyzstan", "ad": "Kırgızistan", "bilgi": "Orta Asya'nın İsviçre'si olarak bilinen dağlık bir ülkedir."},
    {"dosya": "Kolombiya-removebg-preview.png", "geo_name": "Colombia", "ad": "Kolombiya", "bilgi": "Güney Amerika'nın kuzeyinde, kahvesiyle ünlü Ekvatoral bir ülkedir."},
    {"dosya": "Kongo-removebg-preview.png", "geo_name": "Republic of the Congo", "ad": "Kongo", "bilgi": "Orta Afrika'da nehirleriyle ünlü bir ülkedir."},
    {"dosya": "Kosta_Rika-removebg-preview.png", "geo_name": "Costa Rica", "ad": "Kosta Rika", "bilgi": "Ordusu olmayan ve doğayı korumaya adamış nadir ülkelerdendir."},
    {"dosya": "Kuveyt-removebg-preview.png", "geo_name": "Kuwait", "ad": "Kuveyt", "bilgi": "Basra Körfezi'nde küçük ama petrol zengini bir ülkedir."},
    {"dosya": "Kuzey_Kore-removebg-preview.png", "geo_name": "North Korea", "ad": "Kuzey Kore", "bilgi": "Dünyanın en kapalı ve gizemli ülkelerinden biridir."},
    {"dosya": "Küba-removebg-preview.png", "geo_name": "Cuba", "ad": "Küba", "bilgi": "Karayiplerin en büyük adasıdır. Klasik arabalarıyla ünlüdür."},
    {"dosya": "Libya-removebg-preview.png", "geo_name": "Libya", "ad": "Libya", "bilgi": "Kuzey Afrika'da yer alan, büyük kısmı çöl olan bir ülkedir."},
    {"dosya": "Madagaskar-removebg-preview.png", "geo_name": "Madagascar", "ad": "Madagaskar", "bilgi": "Dünyanın en büyük 4. adasıdır. Canlı türlerinin çoğu sadece burada bulunur."},
    {"dosya": "Malezya-removebg-preview.png", "geo_name": "Malaysia", "ad": "Malezya", "bilgi": "Güneydoğu Asya'da iki parçadan oluşan tropikal bir ülkedir."},
    {"dosya": "Mali-removebg-preview.png", "geo_name": "Mali", "ad": "Mali", "bilgi": "Batı Afrika'da yer alır, tarihi Timbuktu şehrine ev sahipliği yapar."},
    {"dosya": "Meksika-removebg-preview.png", "geo_name": "Mexico", "ad": "Meksika", "bilgi": "Kuzey Amerika'nın güneyinde yer alır. Aztek ve Maya medeniyetlerinin yurdudur."},
    {"dosya": "Mısır-removebg-preview.png", "geo_name": "Egypt", "ad": "Mısır", "bilgi": "Piramitleri ve Nil Nehri ile ünlü, tarihin en eski medeniyetlerinden biridir."},
    {"dosya": "Moğolistan-removebg-preview.png", "geo_name": "Mongolia", "ad": "Moğolistan", "bilgi": "Dünyanın en seyrek nüfuslu ülkesidir. Bozkırlarıyla ünlüdür."},
    {"dosya": "Moritanya-removebg-preview.png", "geo_name": "Mauritania", "ad": "Moritanya", "bilgi": "Batı Afrika'da büyük bölümü Sahra Çölü ile kaplı bir ülkedir."},
    {"dosya": "Mozambik-removebg-preview.png", "geo_name": "Mozambique", "ad": "Mozambik", "bilgi": "Güneydoğu Afrika'da uzun bir sahil şeridine sahip ülkedir."},
    {"dosya": "Myanmar-removebg-preview.png", "geo_name": "Myanmar", "ad": "Myanmar", "bilgi": "Güneydoğu Asya'da, altın kaplı tapınaklarıyla bilinen bir ülkedir."},
    {"dosya": "Namibya-removebg-preview.png", "geo_name": "Namibia", "ad": "Namibya", "bilgi": "Dünyanın en eski çölü olan Namib Çölü'ne ev sahipliği yapar."},
    {"dosya": "Nepal-removebg-preview.png", "geo_name": "Nepal", "ad": "Nepal", "bilgi": "Dünyanın zirvesi Everest Tepesi bu ülkededir."},
    {"dosya": "Nijer-removebg-preview.png", "geo_name": "Niger", "ad": "Nijer", "bilgi": "Batı Afrika'da ismini Nijer Nehri'nden alan bir ülkedir."},
    {"dosya": "Nijerya-removebg-preview.png", "geo_name": "Nigeria", "ad": "Nijerya", "bilgi": "Afrika'nın en kalabalık ülkesi ve en büyük ekonomisidir."},
    {"dosya": "Nikaragua-removebg-preview.png", "geo_name": "Nicaragua", "ad": "Nikaragua", "bilgi": "Orta Amerika'nın en büyük yüzölçümüne sahip ülkesidir."},
    {"dosya": "Norveç-removebg-preview.png", "geo_name": "Norway", "ad": "Norveç", "bilgi": "Fiyortlarıyla ünlüdür. Kutuplara çok yakın olduğu için haritada olduğundan çok daha uzun görünür."},
    {"dosya": "Orta_Africa_Cumhuriyeti-removebg-preview.png", "geo_name": "Central African Republic", "ad": "Orta Afrika Cum.", "bilgi": "Afrika kıtasının tam merkezinde yer alır."},
    {"dosya": "Özbekistan-removebg-preview.png", "geo_name": "Uzbekistan", "ad": "Özbekistan", "bilgi": "Tarihi İpek Yolu şehirleri Semerkant ve Buhara buradadır."},
    {"dosya": "Pakistan-removebg-preview.png", "geo_name": "Pakistan", "ad": "Pakistan", "bilgi": "Dünyanın en kalabalık Müslüman nüfuslu ülkelerinden biridir."},
    {"dosya": "Panama-removebg-preview.png", "geo_name": "Panama", "ad": "Panama", "bilgi": "Ünlü Panama Kanalı ile Atlas ve Pasifik Okyanusunu birbirine bağlar."},
    {"dosya": "Papua_Yeni_Gine-removebg-preview.png", "geo_name": "Papua New Guinea", "ad": "Papua Yeni Gine", "bilgi": "Dünyada en fazla dilin konuşulduğu (800+) ülkedir."},
    {"dosya": "Paraguay-removebg-preview.png", "geo_name": "Paraguay", "ad": "Paraguay", "bilgi": "Güney Amerika'nın kalbinde, denize kıyısı olmayan bir ülkedir."},
    {"dosya": "Peru-removebg-preview.png", "geo_name": "Peru", "ad": "Peru", "bilgi": "Machu Picchu antik kentine ev sahipliği yapan İnka medeniyetinin yurdudur."},
    {"dosya": "Polonya-removebg-preview.png", "geo_name": "Poland", "ad": "Polonya", "bilgi": "Orta Avrupa'da yer alır. Haritada konumu gereği biraz büyük görünür."},
    {"dosya": "Portekiz-removebg-preview.png", "geo_name": "Portugal", "ad": "Portekiz", "bilgi": "Avrupa'nın en batı ucundaki ülkedir, kaşifleriyle tanınır."},
    {"dosya": "Romanya-removebg-preview.png", "geo_name": "Romania", "ad": "Romanya", "bilgi": "Drakula efsanesinin doğduğu Transilvanya bölgesi buradadır."},
    {"dosya": "Rusya-removebg-preview.png", "geo_name": "Russia", "ad": "Rusya (Devasa Yanılgı!)", "bilgi": "Dünyanın en geniş ülkesidir ama haritada Afrika'dan büyük görünür, oysa Afrika Rusya'dan çok daha büyüktür."},
    {"dosya": "Senegal-removebg-preview.png", "geo_name": "Senegal", "ad": "Senegal", "bilgi": "Afrika'nın en batı ucu buradadır."},
    {"dosya": "Sırbistan-removebg-preview.png", "geo_name": "Republic of Serbia", "ad": "Sırbistan", "bilgi": "Balkanların merkezinde yer alan tarihi bir ülkedir."},
    {"dosya": "Slovakya-removebg-preview.png", "geo_name": "Slovakia", "ad": "Slovakya", "bilgi": "Orta Avrupa'da, kaleler ve mağaralar ülkesidir."},
    {"dosya": "Slovenya-removebg-preview.png", "geo_name": "Slovenia", "ad": "Slovenya", "bilgi": "Avrupa'nın yeşil kalbi olarak bilinir, ormanlarla kaplıdır."},
    {"dosya": "Somali-removebg-preview.png", "geo_name": "Somalia", "ad": "Somali", "bilgi": "Afrika Boynuzu'nun ucunda yer alır, en uzun sahil şeridine sahiptir."},
    {"dosya": "Sudan-removebg-preview.png", "geo_name": "Sudan", "ad": "Sudan", "bilgi": "Piramit sayısı Mısır'dan daha fazla olan bir Afrika ülkesidir."},
    {"dosya": "Suriye-removebg-preview.png", "geo_name": "Syria", "ad": "Suriye", "bilgi": "Tarihin en eski yerleşim yerlerinden biri olan Şam'a ev sahipliği yapar."},
    {"dosya": "Suudi_Arabistan-removebg-preview.png", "geo_name": "Saudi Arabia", "ad": "Suudi Arabistan", "bilgi": "İslam dininin kutsal toprakları Mekke ve Medine buradadır."},
    {"dosya": "Şili-removebg-preview.png", "geo_name": "Chile", "ad": "Şili", "bilgi": "Dünyanın en uzun ve ince ülkesidir. Haritada boyu olduğundan biraz daha uzun görünür."},
    {"dosya": "Tacikistan-removebg-preview.png", "geo_name": "Tajikistan", "ad": "Tacikistan", "bilgi": "Orta Asya'nın %90'ı dağlarla kaplı ülkesidir."},
    {"dosya": "Tanzanya-removebg-preview.png", "geo_name": "United Republic of Tanzania", "ad": "Tanzanya", "bilgi": "Kilimanjaro Dağı ve Serengeti Milli Parkı ile ünlüdür."},
    {"dosya": "Tayland-removebg-preview.png", "geo_name": "Thailand", "ad": "Tayland", "bilgi": "Güneydoğu Asya'nın turizm cennetidir, 'Gülümsemeler Ülkesi' olarak bilinir."}
]

# --- 6. FONKSİYONLAR ---
def get_true_size_geometry(geo_name, target_lat=0):
    if gdf.empty: return None
    country = gdf[gdf['name'] == geo_name]
    if country.empty: return None
    geom = country.geometry.iloc[0]
    centroid = geom.centroid
    shift_y = target_lat - centroid.y
    return translate(geom, yoff=shift_y)

if gdf.empty: st.stop()

# --- 7. SOL MENÜ ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙️ Kontrol Paneli</p>', unsafe_allow_html=True)
    
    # REFERANS HARİTA
    if os.path.exists("referans_harita.jpeg"):
        st.image("referans_harita.jpeg", caption="Referans Harita (Projeksiyon Kıyaslama)", use_container_width=True)
    elif os.path.exists("referans_harita.jpg"):
         st.image("referans_harita.jpg", caption="Referans Harita (Projeksiyon Kıyaslama)", use_container_width=True)
    
    st.markdown("---")
    
    # Ülke Seçimi (HATA KORUMASI)
    if ulke_listesi:
        secilen_ulke_adi = st.selectbox("🏳️ Bir Ülke Seçin:", options=[u["ad"] for u in ulke_listesi], index=0)
        secilen_item = next(item for item in ulke_listesi if item["ad"] == secilen_ulke_adi)
    else:
        st.error("Ülke listesi yüklenemedi.")
        st.stop()
    
    st.markdown("---")
    if os.path.exists(secilen_item["dosya"]):
        st.image(secilen_item["dosya"], caption=f"{secilen_item['ad']} İzdüşümü")
    
    if "bilgi" in secilen_item:
        st.markdown(f'<div class="fact-box">🧐 <b>Biliyor muydunuz?</b><br><br>{secilen_item["bilgi"]}</div>', unsafe_allow_html=True)
        
    st.markdown("---")
    harita_tipi = st.selectbox("Harita Görünümü", ["Sade (CartoDB)", "Detaylı (OpenStreetMap)", "Karanlık (CartoDB Dark)"])
    opacity = st.slider("Katman Şeffaflığı", 0.1, 1.0, 0.5, 0.1)

# --- 8. ANA EKRAN ---
target_geo_name = secilen_item["geo_name"]
row = gdf[gdf['name'] == target_geo_name]

if not row.empty:
    data = row.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seçilen Ülke", secilen_item["ad"])
    c2.metric("Gerçek Alan", f"{data['gercek_alan_km2']:,.0f} km²")
    hata_renk = "normal"
    if data['bozulma_orani'] > 50: hata_renk = "inverse"
    c3.metric("Bozulma (Hata)", f"+%{data['bozulma_orani']:.1f}", delta_color=hata_renk)
    c4.metric("Yanılgı Kat sayısı", f"{data['kat_farki']:.2f} KAT", "Büyütülmüş")
    
    tiles_dict = {"Sade (CartoDB)": "CartoDB positron", "Detaylı (OpenStreetMap)": "OpenStreetMap", "Karanlık (CartoDB Dark)": "CartoDB dark_matter"}
    
    m = folium.Map(location=[39.93, 32.85], zoom_start=2, tiles=None)
    folium.TileLayer(tiles=tiles_dict[harita_tipi], attr=" ").add_to(m)
    
    folium.GeoJson(data.geometry, style_function=lambda x: {'fillColor': '#ff0000', 'color': '#ff0000', 'weight': 1, 'fillOpacity': opacity}, tooltip="Haritadaki Hali (Mercator)").add_to(m)
    real_geom = get_true_size_geometry(target_geo_name)
    if real_geom:
        folium.GeoJson(gpd.GeoSeries([real_geom]).set_crs("EPSG:4326"), style_function=lambda x: {'fillColor': '#00ff00', 'color': 'green', 'weight': 2, 'fillOpacity': opacity + 0.1}, tooltip="Gerçek Boyutu").add_to(m)
    
    folium.Marker([39.93, 32.85], popup="Merkez: Türkiye", icon=folium.Icon(color="red", icon="star")).add_to(m)
    st_folium(m, width=1200, height=600)
    st.info(f"💡 **Analiz:** {secilen_item['ad']}, haritada olduğundan **{data['kat_farki']:.1f} kat** daha büyük görünmektedir.")

    # --- 9. BİLİMSEL GRAFİK ---
    st.markdown("---")
    st.subheader("📊 Bilimsel Analiz: Hangi Ülke Ne Kadar 'Yalan' Söylüyor?")
    
    plot_data = []
    for item in ulke_listesi:
        row_g = gdf[gdf['name'] == item['geo_name']]
        if not row_g.empty:
            d = row_g.iloc[0]
            plot_data.append({
                "Ülke": item['ad'],
                "Hata Oranı (%)": round(d['bozulma_orani'], 1),
                "Kat Farkı": round(d['kat_farki'], 2)
            })
    
    df_plot = pd.DataFrame(plot_data)
    
    chart = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X('Hata Oranı (%):Q', title='Boyut Bozulma Oranı (%)'),
        y=alt.Y('Ülke:N', sort='-x', title='Ülkeler'),
        color=alt.Color('Hata Oranı (%):Q', scale=alt.Scale(scheme='reds'), legend=None),
        tooltip=['Ülke', 'Hata Oranı (%)', 'Kat Farkı']
    ).properties(height=800)
    
    st.altair_chart(chart, use_container_width=True)

else:
    st.error(f"Veri bulunamadı: {target_geo_name}. Lütfen dunya.json dosyasını kontrol et.")
