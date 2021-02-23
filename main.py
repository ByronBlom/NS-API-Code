# Copyright© 2020 Byron Blom for NS
# This is a webhook designed for DialogFlow
from flask import Flask, request
app = Flask(__name__)

@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"

# connecting to webhook - remember to connect DialogFlow to           Fullfilment.
# I work with different if and elif statements. Each elif statement calls a parameter assigned to a specific intent in DialogFlow.
@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  fulfillmentText = ''
  import http.client, urllib.request, urllib.parse, urllib.error, base64
  query_result = req.get('queryResult')

  #---------------------------------------------------------------------#
  if query_result.get('action') == 'add.numbers': #<- This is the name of the action parameter for the intent in DialogFlow
    num1 = int(query_result.get('parameters').get('number')) # get action parameter from specific intent (num1 & num2)
    num2 = int(query_result.get('parameters').get('number1'))
    
    sum = str(num1 + num2) # create simple formula to sum the parameters

    fulfillmentText =  str(num1)+" plus "+str(num2)+ " is " + sum # always define fulfillmentText, it is the output in DialogFlow

   #---------------------------------------------------------------------#
  elif query_result.get('action') == 'multiply.numbers':
    num1 = int(query_result.get('parameters').get('number'))
    num2 = int(query_result.get('parameters').get('number1'))
    product = str(num1 * num2) # instead of summing the parameters, it now multiplies them
    
    fulfillmentText = str(num1) + " maal " + str(num2)+ " is " + product
   #---------------------------------------------------------------------#
   # Context from departure times to ticket price second class
  elif query_result.get('action') == 'ns.runner':

    num1 = query_result.get('parameters').get('kostengeo-city')
    num2 = query_result.get('parameters').get('kostengeo-city1')
    num1 = str(num1)
    num2 = str(num2)
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64

    headers = {
    # request headers
    'Ocp-Apim-Subscription-Key': '20478f19bbcc411b8e06d306ba760129',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/rio-price-information-api/prices?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
    
      conn.close()
      data = str(data)
      start2 = data.find('"SINGLE_FARE","price":') + 22 # find price single fare ticket second class
      end2 = data.find(',"supplements"', start2)
      price2 = data[start2:end2]
    
      # find single fare price first class
      start1 = data.find('"FIRST","discountType":"NONE","productType":"SINGLE_FARE","price":') + 66
      end1 = data.find(',"supplements":{}},{"classType":"SECOND"') 
      price1 = data[start1:end1] # price single fare ticket first class
      price2 = int(price2)
      
      single_ticket = round((int(price2)/100),1) # single fare ticket second class
      single_ticket40 = round(((int(price2)/100)*0.6),1) # ticket with discount second class
      return_ticket = round(((int(price2)/100)*2),1) # return ticket price second class
    
      
      fulfillmentText = "De prijs voor een enkeltje in klas 2 van " +num1 + " naar " + num2 + " kost " + str(single_ticket) +" euro," + " een enkeltje met 40 procent korting kost " + str(single_ticket40) + " euro " + ", en een retourtje in klas 2 kost " + str(return_ticket) + " euro"


    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))

    



   #---------------------------------------------------------------------#
   # Retrieve actual weather

  elif query_result.get('action') == 'ns.weer':

    num1 = query_result.get('parameters').get('geo-city')
    from py_weernl import weerLive

    place = str(num1)
    my_api = ["f0c94a983e"]
    w = weerLive(api=my_api)

    data = w.getData(place)
    data = str(data)

    location_start = data.find("plaats':") + 10
    location_end = data.find("', 'temp'", location_start)
    location = data[location_start:location_end]

    temp_start = data.find("'temp':") + 9
    temp_end = data.find("', 'gtemp':", temp_start)
    temperature = data[temp_start:temp_end]

    status_start = data.find("'samenv':") + 11
    status_end = data.find("', 'lv':", status_start)
    status = data[status_start:status_end]
    status = status.lower()

    wind_start = data.find("'windkmh':") + 12
    wind_end = data.find("', 'luchtd'", wind_start)
    wind = data[wind_start:wind_end]


    fulfillmentText = "De temperatuur in " + str(location) + " is momenteel " + str(temperature) + " graden. " + " Daarbij " + str(status) + " met windsnelheden van " + str(wind) + " kilometer per uur."
  
   #---------------------------------------------------------------------#
   # Retrieve departure times and associated tracks
   
  elif query_result.get('action') == 'ns.tijden':
    
    num1 = (query_result.get('parameters').get('geo-city'))
    num2 = (query_result.get('parameters').get('geo-city1'))
    import http.client, urllib.request, urllib.parse, urllib.error, base64
    import re

    headers = {
    # request headers
    'Authorization': '',
    'X-Request-ID': '',
    'X-Caller-ID': '',
    'x-api-key': '',
    'Ocp-Apim-Subscription-Key': '37fd02ac8dcf4bbab0099a62b7d47b32',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    'searchForArrival': 'False',
    
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/reisinformatie-api/api/v3/trips?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
      data = str(data)
    
    
      data = data.replace("-","").replace(":","")
      tuples = re.findall('\\bplannedFromTime=\w+\\b', data) 
      tuples1 = tuples
  
      sp0 = []
      sentence = data
      word = "fareLegs"
      for match in re.finditer(word, sentence):
        sp0.append(match.end())
        

        
      x1 = data[(sp0[0]):((sp0[0])+3400)] 

      start_x1 = x1.find(',"transfers"') + 12 # Transfer number
      eind_x1 = x1.find(',"status""', start_x1)
      overstap1 = x1[start_x1:eind_x1]
      
      if "actualTrack" in x1:
        
        start1 = x1.find('actualTrack""') + 13
        end1 = x1.find('","chec', start1)
        spoor1 = x1[start1:end1]
      else:
        start1 = x1.find('plannedTrack""') + 14
        end1 = x1.find('","chec', start1)
        spoor1 = x1[start1:end1]
    
    #
    
      x2 = data[(sp0[1]):((sp0[1])+3400)]

      start_x2 = x2.find(',"transfers"') + 12 # Transfer number
      eind_x2 = x2.find(',"status""', start_x2)
      overstap2 = x2[start_x2:eind_x2]

      if "actualTrack" in x2:
        
        start2 = x2.find('actualTrack""') + 13
        end2 = x2.find('","chec', start2)
        spoor2 = x2[start2:end2]
      else:
        start2 = x2.find('plannedTrack""') + 14
        end2 = x2.find('","chec', start2)
        spoor2 = x2[start2:end2]

    #

    #
    
      x3 = data[(sp0[2]):((sp0[2])+3400)]

      start_x3 = x3.find(',"transfers"') + 12 # Transfer number
      eind_x3 = x3.find(',"status""', start_x3)
      overstap3 = x3[start_x3:eind_x3]

      if "actualTrack" in x3:
        
        start3 = x3.find('actualTrack""') + 13
        end3 = x3.find('","chec', start3)
        spoor3 = x3[start3:end3]
      else:
        start3 = x3.find('plannedTrack""') + 14
        end3 = x3.find('","chec', start3)
        spoor3 = x3[start3:end3]
    
    #
    
      x4 = data[(sp0[3]):((sp0[3])+3400)]

      start_x4 = x4.find(',"transfers"') + 12 # Transfer number
      eind_x4 = x4.find(',"status""', start_x4)
      overstap4 = x4[start_x4:eind_x4]

      if "actualTrack" in x4:
        
        start4 = x4.find('actualTrack""') + 13
        end4 = x4.find('","chec', start4)
        spoor4 = x4[start4:end4]
      else:
        start4 = x4.find('plannedTrack""') + 14
        end4 = x4.find('","chec', start4)
        spoor4 = x4[start4:end4]

    #
    
      x5 = data[(sp0[4]):((sp0[4])+3400)]

      start_x5 = x5.find(',"transfers"') + 12 # Transfer number
      eind_x5 = x5.find(',"status""', start_x5)
      overstap5 = x5[start_x5:eind_x5]

      if "actualTrack" in x5:
        
        start5 = x5.find('actualTrack""') + 13
        end5 = x5.find('","chec', start5)
        spoor5 = x5[start5:end5]
      else:
        start5 = x5.find('plannedTrack""') + 14
        end5 = x5.find('","chec', start5)
        spoor5 = x5[start5:end5]
    
    #
        
      x6 = data[(sp0[5]):((sp0[5])+3400)]
      if "actualTrack" in x6:
        
        start6 = x6.find('actualTrack""') + 13
        end6 = x6.find('","chec', start6)
        spoor6 = x6[start6:end6]
      else:
        start6 = x6.find('plannedTrack""') + 14
        end6 = x6.find('","chec', start6)
        spoor6 = x6[start6:end6]
        
      
      #
    
      new2 = [] 
      new3 = []
      for tup in tuples1:
        if tup not in new2:
            new2.append(tup)
      for tup in new2:  
        
        tup = tup.replace("plannedFromTime=","")
        tup = tup[9:13]
        l = int(len(tup)/2)
        a,b = tup[:l],tup[l:]
        new3.append(a+":"+b)
    
      y0=[]
      y1=[]
      y2=[]
      y3=[]
      y4=[]
      y5=[]


    #
      newlist = sorted(set(new3), key=lambda x:new3.index(x))
    
      for i in newlist[0:1]:
         y0.append(i)
      for i in newlist[1:2]:
         y1.append(i)
      for i in newlist[2:3]:
         y2.append(i)
      for i in newlist[3:4]:
         y3.append(i)
      for i in newlist[4:5]:
         y4.append(i)
      for i in newlist[5:6]:
         y5.append(i)
      
      t0 = (''.join(y0))
      t0 = t0.replace(":","")
      x0 = data.find(t0)

      data1 = data[x0:(x0+1000)]
      if "actualTrack" in data1:
        
        start0 = data1.find('actualTrack""') + 13
        end0 = data1.find('","chec', start0)
        spoor0 = data1[start0:end0]
      else:
        start0 = data1.find('plannedTrack""') + 14
        end0 = data1.find('","chec', start0)
        spoor0 = data1[start0:end0]
       
      
      if spoor1 == spoor2 and spoor1 == spoor3 and spoor1 == spoor4 and spoor1 == spoor5 and spoor1 == spoor0 and overstap1 == overstap2 and overstap2 == overstap3 and overstap3 == overstap4 and overstap4 == overstap5:
        fulfillmentText = "De eerstvolgende vertrektijden van station " + num1 + " naar station " + num2 + " zijn: " + " om " + ''.join(y0) + ", om " + ''.join(y1) + ", om " + ''.join(y2) + ", om " + ''.join(y3)+ ", om "+ ''.join(y4) + ". Alle treinen vertrekken vanaf spoor " + str(spoor1) +", u hoeft " + str(overstap1) + " keer over te stappen."

      

       
      elif spoor1 != spoor2 or spoor1 != spoor3 or spoor1 != spoor4 or spoor1 != spoor5 or spoor1 != spoor0 and overstap1 == overstap2 and overstap2 == overstap3 and overstap3 == overstap4 and overstap4 == overstap5:
        fulfillmentText = "De eerstvolgende vertrektijden van station " + num1 + " naar station " + num2 + " zijn: " + " om " + ''.join(y0) + " vanaf spoor  " + str(spoor0) + ", om " + ''.join(y1) + " vanaf spoor " + str(spoor1) +  ", om " + ''.join(y2) + " vanaf spoor " + str(spoor2) + ", om " + ''.join(y3) + " vanaf spoor " + str(spoor3) + ", en om " + ''.join(y4) + " vanaf spoor " + str(spoor4) + ". U hoeft " + str(overstap1) + " keer over te stappen."

      elif (spoor1 != spoor2 or spoor1 != spoor3 or spoor1 != spoor4 or spoor1 != spoor5 or spoor1 != spoor0) and (overstap1 != overstap2 or overstap2 != overstap3 or overstap3 != overstap4 or overstap4 != overstap5):
        fulfillmentText = "De eerstvolgende vertrektijden van station " + num1 + " naar station " + num2 + " zijn: " + " om " + ''.join(y0) + " vanaf spoor  " + str(spoor0) + "(overstap " + str(overstap1) + " keer)" + ", om " + ''.join(y1) + " vanaf spoor " + str(spoor1) + "(overstap " + str(overstap2) + " keer)" + ", om " + ''.join(y2) + " vanaf spoor " + str(spoor2) + "(overstap " +str(overstap3)+" keer)" + ", om " + ''.join(y3) + " vanaf spoor " + str(spoor3) + "(overstap "+str(overstap4)+" keer)" +", en om " + ''.join(y4) + " vanaf spoor " + str(spoor4) 


     
      #else: 
          #fulfillmentText = "De eerstvolgende vertrektijden van station " + num1 + " naar station " + num2 + " zijn: " + " om " + ''.join(y0) + " vanaf spoor  " + str(spoor0) + "(overstap " + str(overstap1) + " keer)" + ", om " + ''.join(y1) + " vanaf spoor " + str(spoor1) + "(overstap " + str(overstap2) + " keer)" + ", om " + ''.join(y2) + " vanaf spoor " + str(spoor2) + "(overstap " +str(overstap3)+" keer)" + ", om " + ''.join(y3) + " vanaf spoor " + str(spoor3) + "(overstap "+str(overstap4)+" keer)" +", en om " + ''.join(y4) + " vanaf spoor " + str(spoor4) 
       
       
    

      conn.close()
    except Exception as e:
      print("[Errno {0}] {1}".format(e.errno, e.strerror))

   #---------------------------------------------------------------------#
   # Retrieve public transport bicycle information

  elif query_result.get('action') == 'ns.ov-fiets': 
    num1 = (query_result.get('parameters').get('geo-city')) # get city from intent
    import http.client, urllib.request, urllib.parse, urllib.error, base64
    dic = {"Ac":"Abcoude", "Adh":"Leeuwarden Achter de Hoven",
    "Ah":"Arnhem","Ahp":"Arnhem Velperpoort","Ahpr":"Arnhem Presikhaaf",
    "Ahz":"Arnhem Zuid","Akl":"Arkel","Akm":"Akkrum","Alm":"Almere Centrum","Almb":"Almere Buiten",
    "Almm":"Almere Muziekwijk","Almo":"Almere Oostvaarders","Almp":"Almere Parkwijk","Amf":"Amersfoort",
    "Amfs":"Amersfoort Schothorst","Aml":"Almelo","Ampo":"Almere Poort","Amr":"Alkmaar","Amri":"Almelo De Riet","Amrn":"Alkmaar Noord",
    "Ana":"Anna Paulowna","Apd":"Apeldoorn","Apdm":"Apeldoorn De Maten","Apdo":"Apeldoorn Osseveld","Apg":"Appingedam",
    "Apn":"Alphen aan den Rijn","Arn":"Arnemuiden","Asa":"Amsterdam Amstel","Asb":"Amsterdam Bijlmer ArenA","Asd":'Amsterdam Centraal', "Asd":'Amsterdam',
    "Asdl":'Amsterdam Lelylaan',"Asdm":'Amsterdam Muiderpoort',
    "Asdz":'Amsterdam Zuid',"Ashd":'Amsterdam Holendrecht',"Asn":'Assen',"Ass":'Amsterdam Sloterdijk',"Assp":'Amsterdam Science Park',"Atn":'Aalten',"Avat":'Amersfoort Vathorst',"Bd":'Breda',"Bde":'Bunde',
    "Bdg":'Bodegraven',"Bdm":'Bedum',"Bdpb":'Breda-Prinsenbeek',"Bet":'Best',"Bf":'Baflo',"Bgn":'Bergen op Zoom',
    "Bhdv":'Boven Hardinxveld',"Bhv":'Bilthoven',"Bk":'Beek-Elsloo',"Bkf":'Bovenkarspel Flora',
    "Bkg":'Bovenkarspel-Grootebroek',"Bkl":'Breukelen',"Bl":'Beilen',"Bll":'Bloemendaal',"Bmn":'Brummen',"Bmr":'Boxmeer',"Bn":'Borne',
    "Bnc":'Barneveld Centrum',"Bnk":'Bunnik',"Bnn":'Barneveld Noord',"Bnz":'Barneveld Zuid',
    "Bp":"Buitenpost","Br":"Blerick","Brd":'Barendrecht',"Brn":'Baarn',"Bsd":'Beesd',"Bsk":'Boskoop',
    "Bsmz":'Bussum Zuid',"Btl":'Boxtel','Bv':'Beverwijk','Bzl':'Kapelle-Biezelinge','Bzm':'Hardinxveld Blauwe Zoom','Cas':'Castricum','Ck':'Cuijk',
    'Cl':'Culemborg','Co':'Coevorden','Cps':'Capelle Schollevaar','Cvm':'Chevremont','Da':'Daarlerveen',
    'Db':'Driebergen-Zeist','Ddn':'Delden','Ddr':'Dordrecht','Ddrs':'Dordrecht Stadspolders','Ddzd':'Dordrecht Zuid',
    'Dei':'Deinum',"Did":'Didam','Dl':'Dalfsen','Dld':'Den Dolder','Dln':'Dalen','Dmn':'Diemen','Dmnz':'Diemen Zuid','Dn':'Deurne','Dr':'Dieren','Drh':'Driehuis','Dron':'Dronten','Drp':'Dronrijp',"Dt":'Delft','Dtc':'Doetinchem',
    'Dtch':'Doetinchem De Huet','Dtz':'Delft Zuid','Dv':'Deventer','Dvc':'Deventer Colmschate','Dvd':'Duivendrecht','Dvn':'Duiven','Dvnk':'De Vink','Dz':'Delfzijl','Dzw':'Delfzijl West','Ec':'Echt','Ed':'Ede-Wageningen',
    'Edc':'Ede Centrum','Edn':'Eijsden','Egh':'Eygelshoven',
    'Eghm':'Eygelshoven Markt','Ehb':'Eindhoven Beukenlaan','Ehv':'Eindhoven','Ekz':'Enkhuizen','Eml':'Ermelo',
    'Emn':'Emmen','Emnz':'Emmen Zuid','Es':'Enschede','Esd':'Enschede Drienerlo','Ese':'Enschede De Eschmarke',
    'Est':'Elst','Etn':'Etten-Leur','Fn':'Franeker','Gbg':'Gramsbergen','Gbr':'Glanerbrug','Gd':'Gouda','Gdg':'Gouda Goverwelle',
    'Gdk':'Geerdijk','Gdm':'Geldermalsen','Gdr':'Gaanderen','Gerp':'Groningen  Europapark','Gk':'Grijpskerk','Gln':'Geleen Oost',
    'Gn':'Groningen','Gnd':'Hardinxveld-Giessendam','Gnn':'Groningen Noord','Go':'Goor',
    'Gp':'Geldrop','Gr':'Gorinchem','Gs':'Goes',
    'Gv':'Den Haag HS','Gvc':'Den Haag Centraal', 'Gvmv':'Den Haag Mariahoeve','Gvmw':'Den Haag Moerwijk','Gw':'Grou-Jirnsum',
    'Gz':'Gilze-Rijen','Had':'Heemstede-Aerdenhout','Hb':'Hoensbroek','Hd':'Harderwijk','Hdb':'Hardenberg',
    'Hde':"'t Harde",'Hdg':'Hurdegaryp','Hdr':'Den Helder','Hdrz':'Den Helder Zuid','Hfd':'Hoofddorp',
    'Hgl':'Hengelo','Hglg':'Hengelo Gezondheidspark','Hglo':'Hengelo Oost','Hgv':'Hoogeveen','Hgz':'Hoogezand-Sappemeer','Hil':'Hillegom',
    'Hk':'Heemskerk','Hks':'Hoogkarspel','Hld':'Hoek van Holland Haven',
    'Hlds':'Hoek van Holland Strand','Hlg':'Harlingen','Hlgh':'Harlingen Haven',
    'Hlm':'Haarlem','Hlms':'Haarlem Spaarnwoude','Hlo':'Heiloo',
    'Hm':'Helmond','Hmbh':'Helmond Brouwhuis','Hmbv':'Helmond Brandevoort','Hmh':"Helmond 't Hout",'Hmn':'Hemmen-Dodewaard','Hn':'Hoorn','Hnk':'Hoorn Kersenboogerd','Hno':'Heino',
    'Hnp':'Hindeloopen','Hon':'Holten','Hor':'Hollandsche Rading','Hr':'Heerenveen',
    'Hrl':'Heerlen','Hrlk':'Heerlen De Kissel','Hrlw':'Heerlen Woonboulevard',
    "Hrn":"Haren","Hrt":"Horst-Sevenum","Ht":'s-Hertogenbosch',"Htn":"Houten","Htnc":"Houten Castellum",
    "Hto":'s-Hertogenbosch Oost',"Hvl":"Hoevelaken","Hvs":"Hilversum","Hvsm":"Hilversum Media Park",
    "Hvsp":"Hilversum Sportpark","Hwd":"Heerhugowaard",
    "Hwzb":"Halfweg-Zwanenburg","Hze":"Heeze","IJt":"IJlst","Kbd":"Krabbendijke","Kbk":"Klarenbeek","Kbw":"Koog Bloemwijk","Klp":"Veenendaal-De Klomp",
    "Kma":"Krommenie-Assendelft",'Kmr':'Klimmen-Ransdaal','Kmw':'Koudum-Molkwerum','Kpn':'Kampen','Kpnz':'Kampen Zuid','Krd':'Kerkrade Centrum','Krg':'Kruiningen-Yerseke','Ktr':'Kesteren','Kw':'Kropswolde','Kzd':'Koog-Zaandijk','Laa':'Den Haag Laan v NOI','Lc':'Lochem',
    'Ldl':'Leiden Lammenschans','Ldm':'Leerdam','Ledn':'Leiden Centraal','Lg':'Landgraaf',
    'Lls':'Lelystad Centrum','Lp':'Loppersum','Ltn':'Lunteren','Ltv':'Lichtenvoorde-Groenlo','Lut':'Geleen-Lutterade',
    'Lw':'Leeuwarden','Lwc':'Leeuwarden Camminghaburen','Mas':'Maarssen','Mdb':'Middelburg','Mes':'Meerssen','Mg':'Mantgum',
    'Mmlh':'Mook Molenhoek','Mp':'Meppel','Mrb':'Mariënberg','Mrn':'Maarn','Mss':'Maassluis','Msw':'Maassluis West','Mt':'Maastricht','Mth':'Martenshoek',
    'Mtn':'Maastricht Noord','Mtr':'Maastricht Randwyck','Mz':'Maarheeze','Na':'Nieuw Amsterdam','Ndb':'Naarden-Bussum',
    'Nh':'Nuth','Nkk':'Nijkerk','Nm':'Nijmegen',
    'Nmd':'Nijmegen Dukenburg','Nmh':'Nijmegen Heyendaal','Nml':'Nijmegen Lent','Ns':'Nunspeet','Nsch':'Bad Nieuweschans',
    'Nvd':'Nijverdal','Nvp':'Nieuw Vennep','Nwk':'Nieuwerkerk a/d IJssel','Nwl':'Schiedam Nieuwland',
    'O':'Oss','Obd':'Obdam','Odb':'Oudenbosch','Odz':'Oldenzaal','Omn':'Ommen','Op':'Opheusden','Ost':'Olst','Ot':'Oisterwijk','Otb':'Oosterbeek','Ovn':'Overveen',
    'Ow':'Oss West','Pmo':'Purmerend Overwhere','Pmr':'Purmerend','Pmw':'Purmerend Weidevenne',
    'Pt':'Putten','Rai':'Amsterdam RAI','Rat':'Raalte','Rbv':'Rilland-Bath','Rd':'Roodeschool','Rh':'Rheden','Rhn':'Rhenen',
    'Rl':'Ruurlo','Rlb':'Rotterdam Lombardijen','Rm':'Roermond','Rs':'Rosmalen','Rsd':'Roosendaal','Rsn':'Rijssen','Rsw':'Rijswijk','Rta':'Rotterdam Alexander','Rtb':'Rotterdam Blaak',
    'Rtd':'Rotterdam Centraal','Rtn':'Rotterdam Noord','Rtz':'Rotterdam Zuid','Rv':'Reuver','Rvs':'Ravenstein','Sbk':'Spaubeek','Sd':'Soestdijk','Sda':'Scheemda','Sdm':'Schiedam Centrum','Sdt':'Sliedrecht','Sdtb':'Sliedrecht Baanhoek','Sgl':'Houthem-Sint Gerlach',
    'Sgn':'Schagen','Shl':'Schiphol','Sk':'Sneek','Sknd':'Sneek Noord','Sm':'Swalmen','Sn':'Schinnen','Sog':'Schin op Geul','Spm':'Sappemeer Oost','Sptn':'Santpoort Noord',
    'Sptz':'Santpoort Zuid','Srn':'Susteren','Ssh':'Sassenheim','St':'Soest','Std':'Sittard','Stm':'Stedum',
    'Stv':'Stavoren','Stz':'Soest Zuid','Swd':'Sauwerd','Swk':'Steenwijk','Tb':'Tilburg',
    'Tbg':'Terborg','Tbr':'Tilburg Reeshof','Tbu':'Tilburg Universiteit','Tg':'Tegelen','Tl':'Tiel','Tpsw':'Tiel Passewaaij','Twl':'Twello','Uhm':'Uithuizermeeden','Uhz':"Uithuizen",'Ust':"Usquert",'Ut':"Utrecht Centraal",'Utg':"Uitgeest",'Utl':"Utrecht Lunetten",'Utlr':"Utrecht Leidsche Rijn",
    'Utm':"Utrecht Maliebaan",'Uto':"Utrecht Overvecht",'Utt':"Utrecht Terwijde",
    'Utzl':"Utrecht Zuilen",'Vb':"Voorburg",'Vd':"Vorden",'Vdg':"Vlaardingen Centrum",'Vdl':"Voerendaal",'Vdm':"Veendam",'Vdo':"Vlaardingen Oost",'Vdw':"Vlaardingen West",'Vem':"Voorst-Empe",'Vg':"Vught",'Vh':"Voorhout",'Vhp':"Vroomshoop",'Vk':"Valkenburg",'Vl':"Venlo",
    'Vlb':"Vierlingsbeek",'Vndc':"Veenendaal Centrum",'Vndw':"Veenendaal West",'Vp':"Velp",'Vry':"Venray","Vs":"Vlissingen",
    "Vss":"Vlissingen Souburg","Vst":"Voorschoten","Vsv":"Varsseveld","Vtn":"Vleuten","Vwd":"Veenwouden","Vz":"Vriezenveen","Wad":"Waddinxveen","Wadn":"Waddinxveen Noord","Wc":"Wijchen","Wd":"Woerden",
    "Wdn":"Wierden","Wf":"Wolfheze","Wfm":"Warffum","Wh":"Wijhe","Wk":"Workum","Wl":"Wehl","Wm":"Wormerveer","Wp":"Weesp","Ws":'Winschoten',"Wsm":"Winsum","Wt":"Weert","Wtv":"Westervoort","Wv":"Wolvega","Ww":"Winterswijk","Www":"Winterswijk West","Wz":"Wezep","Ypb":"Den Haag Ypenburg","Za":"Zetten-Andelst","Zb":"Zuidbroek","Zbm":"Zaltbommel","Zd":"Zaandam","Zdk":"Zaandam Kogerveld","Zh":"Zuidhorn","Zl":"Zwolle","zlw":"Lage Zwaluwe","Zp":"Zutphen","Ztm":"Zoetermeer",
    "Ztmo":"Zoetermeer Oost","Zv":"Zevenaar",
    "Zvb":"Zevenbergen","Zvt":"Zandvoort aan Zee","Zwd":"Zwijndrecht","Zww":"Zwaagwesteinde",
      } # valuable dictionary with station codes


    headers = {'Ocp-Apim-Subscription-Key': '37fd02ac8dcf4bbab0099a62b7d47b32',
        }

    city_code = ""
    search_city = num1
    for code, city in dic.items(): # transform city to station code
      if city == search_city:
        city_code = code
      
    if city_code == "": # if station doesn't exist, return None
        city_code = "None"
    

    params = urllib.parse.urlencode({
          # Request parameters
          'station_code': city_code,
           })

    

    try:
       conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
       conn.request("GET", "/places-api/v2/ovfiets?%s" % params, "{body}", headers)
       response = conn.getresponse()
       data = response.read()
       data = str(data)
    
       if len(data) < 100: # no ouput is given if there are no public bikes 
        fulfillmentText = "Dit station heeft geen OV-fietsen"
       else:
         start = data.find('rentalBikes":"') +14 #find number of available public bikes in data
         end = data.find('","locationCode":"',start)
         bikes = data[start:end] # get number
         bikes = int(bikes) # convert to integer
         if bikes == 1: # if bikes is 1, sentence with "is" instead of "zijn" - grammar
           fulfillmentText = "Station " + search_city + " beschikt over OV-fietsen, er is momenteel "+ str(bikes)+ " OV-fiets aanwezig."
         elif bikes == 0 or bikes > 1:
           fulfillmentText = "Station " + search_city + " beschikt over OV-fietsen, er zijn momenteel "+ str(bikes)+ " OV-fietsen aanwezig."


        
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

   #---------------------------------------------------------------------#
   # Context to second class ticket

  elif query_result.get('action') == 'ns.prijsklasse2':
    
    num1 = (query_result.get('parameters').get('klasseprijsgeo-city'))
    num2 = (query_result.get('parameters').get('klasseprijsgeo-city1'))
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64

    headers = {
    # request headers
    'Ocp-Apim-Subscription-Key': '20478f19bbcc411b8e06d306ba760129',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/rio-price-information-api/prices?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
    
      conn.close()
      data = str(data)
      start2 = data.find('"SINGLE_FARE","price":') + 22 # find price single fare ticket second class
      end2 = data.find(',"supplements"', start2)
      price2 = data[start2:end2]
    
      # find single fare price first class
      start1 = data.find('"FIRST","discountType":"NONE","productType":"SINGLE_FARE","price":') + 66
      end1 = data.find(',"supplements":{}},{"classType":"SECOND"') 
      price1 = data[start1:end1] # price single fare ticket first class
      price2 = int(price2)
      
      single_ticket = round((int(price2)/100),1) # single fare ticket second class
      single_ticket40 = round(((int(price2)/100)*0.6),1) # ticket with discount second class
      return_ticket = round(((int(price2)/100)*2),1) # return ticket price second class
    
      
      fulfillmentText = "De prijs voor een enkeltje in klas 2 van " +num1+ " naar " +num2+ " kost " + str(single_ticket) +" euro," + " een enkeltje met 40 procent korting kost " + str(single_ticket40) +" euro " + ",en een retourtje in klas 2 kost " + str(return_ticket) + " euro."


    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))
  

   #---------------------------------------------------------------------#
   # Context to second class ticket 2.0

  elif query_result.get('action') == 'NS.2eKlas-2.0':
    
    num1 = (query_result.get('parameters').get('station1'))
    num2 = (query_result.get('parameters').get('station2'))
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64

    headers = {
    # request headers
    'Ocp-Apim-Subscription-Key': '20478f19bbcc411b8e06d306ba760129',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/rio-price-information-api/prices?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
    
      conn.close()
      data = str(data)
      start2 = data.find('"SINGLE_FARE","price":') + 22 # find price single fare ticket second class
      end2 = data.find(',"supplements"', start2)
      price2 = data[start2:end2]
    
      # find single fare price first class
      start1 = data.find('"FIRST","discountType":"NONE","productType":"SINGLE_FARE","price":') + 66
      end1 = data.find(',"supplements":{}},{"classType":"SECOND"') 
      price1 = data[start1:end1] # price single fare ticket first class
      price2 = int(price2)
      
      single_ticket = round((int(price2)/100),1) # single fare ticket second class
      single_ticket40 = round(((int(price2)/100)*0.6),1) # ticket with discount second class
      return_ticket = round(((int(price2)/100)*2),1) # return ticket price second class
    
      
      fulfillmentText = "De prijs voor een enkeltje in klas 2 van " +num1+ " naar " +num2+ " kost " + str(single_ticket) +" euro," + " een enkeltje met 40 procent korting kost " + str(single_ticket40) +" euro " + ",en een retourtje in klas 2 kost " + str(return_ticket) + " euro."


    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))
 
   #---------------------------------------------------------------------#
   # Context to first class ticket

  elif query_result.get('action') == 'ns.prijsklasse1':
    
    num1 = (query_result.get('parameters').get('klasseprijsgeo-city'))
    num2 = (query_result.get('parameters').get('klasseprijsgeo-city1'))
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64

    headers = {
    # request headers
    'Ocp-Apim-Subscription-Key': '20478f19bbcc411b8e06d306ba760129',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/rio-price-information-api/prices?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
    
      conn.close()
      data = str(data)
    
    
      # find single fare price first class
      start1 = data.find('"classType":"FIRST","discountType":"NONE","productType":"SINGLE_FARE","price":') + 78
      end1 = data.find(',"supplements"', start1) 
      price1 = data[start1:end1] # price single fare ticket first class
     
      
      single_ticket = round((int(price1)/100),1) # single fare ticket second class
      single_ticket40 = round(((int(price1)/100)*0.6),1) # ticket with discount second class
      return_ticket = round(((int(price1)/100)*2),1) # return ticket price second class
    
      
      fulfillmentText = "De prijs voor een enkeltje in klas 1 van " +num1+ " naar " +num2+ " kost " + str(single_ticket) +" euro," + " een enkeltje met 40 procent korting kost " + str(single_ticket40) +" euro " + ",en een retourtje in klas 1 kost " + str(return_ticket) + " euro."


    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))

  #---------------------------------------------------------------------#
   # Context to firt class ticket 2.0

  elif query_result.get('action') == 'ns.1eklas2.0':
    
    num1 = (query_result.get('parameters').get('station1'))
    num2 = (query_result.get('parameters').get('station2'))
    
    import http.client, urllib.request, urllib.parse, urllib.error, base64

    headers = {
    # request headers
    'Ocp-Apim-Subscription-Key': '20478f19bbcc411b8e06d306ba760129',
    }

    params = urllib.parse.urlencode({
    # request parameters
    'fromStation': num1,
    'toStation': num2,
    })

    try:
      conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
      conn.request("GET", "/rio-price-information-api/prices?%s" % params, "{body}", headers)
      response = conn.getresponse()
      data = response.read()
    
      conn.close()
      data = str(data)
      start2 = data.find('"SINGLE_FARE","price":') + 22 # find price single fare ticket second class
      end2 = data.find(',"supplements"', start2)
      price2 = data[start2:end2]
    
      # find single fare price first class
      start1 = data.find('"FIRST","discountType":"NONE","productType":"SINGLE_FARE","price":') + 66
      end1 = data.find(',"supplements":null},{"classType":"SECOND","discountType":"FORTY_PERCENT",') 
      price1 = data[start1:end1] # price single fare ticket first class
      price1 = int(price1)
      
      single_ticket = round((int(price1)/100),1) # single fare ticket second class
      single_ticket40 = round(((int(price1)/100)*0.6),1) # ticket with discount second class
      return_ticket = round(((int(price1)/100)*2),1) # return ticket price second class
    
      
      fulfillmentText = "De prijs voor een enkeltje in klas 1 van " +num1+ " naar " +num2+ " kost " + str(single_ticket) +" euro," + " een enkeltje met 40 procent korting kost " + str(single_ticket40) +" euro " + ",en een retourtje in klas 1 kost " + str(return_ticket) + " euro."


    except Exception as e:
         print("[Errno {0}] {1}".format(e.errno, e.strerror))
  
  return {
        "fulfillmentText": fulfillmentText,
        "displayText": '25',
        "source": "webhookdata"
    } # actual output to DialogFlow depending on action parameters
    
   
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
