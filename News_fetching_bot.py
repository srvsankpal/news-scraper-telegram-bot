import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

token="2119059351:AAGsX30jA806XJOzkFbULk-4N2Huh6cwsTE"
id="-670987966"
time2=int(datetime.now().timestamp())
text="Good Morning, Select the News You want to read."
text2="Select the sub category of news"

#creating predefined hardcoded buttons
#you can create you own predefined buttons or even dynamically get the links from website
reply_markup={"inline_keyboard":[
    [
        {"text":"City News",
        "callback_data":"news/cities"
        },
        {"text":"Elections",
        "callback_data":"elections"
        }
             
    ],
    [
        {"text":"Sports",
        "callback_data":"sport"
        },
        {"text":"Entertainment",
        "callback_data":"entertainment"
        }
    ],
    [
        {"text":"Society",
        "callback_data":"society"
        },
        {"text":"Lifestyle",
        "callback_data":"life-and-style"
        }
    ],
    [
        {"text":"Technology",
        "callback_data":"sci-tech"
        },
        {"text":"Education",
        "callback_data":"education"
        }
    ],
    [
        {"text":"Business",
        "callback_data":"business"
        }
    ]
    ]}
reply_markup=json.dumps(reply_markup)

news_url="https://www.thehindu.com/"
url="https://api.telegram.org/bot{}/".format(token)


def send_buttons(text,id,reply_markup):
    send_url = url + "sendMessage?text={}&chat_id={}&reply_markup={}".format(text, id, reply_markup)
    time=int(datetime.now().timestamp())
    r=requests.post(send_url)
    return(time)

def send_msg(text,id):
    r=requests.post(url + "sendMessage?text={}&chat_id={}".format(str(text), id) )


def get_subnews(topic):
    sublinks=[] #list to store scraped sublinks
    buttons=[] #list to store text for sub category buttons
    r=requests.get(news_url + str(topic)+"/")
    data=r.text
    soup = BeautifulSoup(data, "html.parser")
    atags=soup.find_all('a')
    for links in atags:
        href=links.get("href")
        var="^(https://www.thehindu.com/{}/.+?/).*".format(topic)
        l=re.findall(var, str(href))
        if len(l)!=0 :
            #verifying if the sublinks are actually sublinks and not the links to articles
            verify="^"+str(l[0])+"article"
            if l[0] not in sublinks and re.search(verify, href)==None:
                sublinks.append(l[0])
                if topic=="news/cities":
                    buttons.append(l[0].split("/")[5])
                else:
                    buttons.append(l[0].split("/")[4])
    return(buttons, sublinks)

def hear_response(time):
    while True:
        r1=requests.get(url + "getUpdates")
        response=r1.text
        response=json.loads(response)
        info = response["result"][len(response["result"])-1]#parsing the json
        try:
            #filtering the json response with threshold as the date generated while sending buttons
            if int(info["callback_query"]["message"]["date"])+1>=int(time):
                response=info["callback_query"]["data"]
                #print(response)
                break
            else:
                continue
        except:
            continue
    return(str(response))

def create_sub_buttons(buttons):
    reply_markup2={"inline_keyboard":[]}
    for button in buttons:
        each_button={}
        each_button["text"]=button
        each_button["callback_data"]=button
        reply_markup2["inline_keyboard"].append([each_button])
    return(reply_markup2)

def fetch_news(topic,response2):
    news=[] #to store urls for articles
    all_articles=[] #to store all data of articles (links & dates)
    r=requests.get(news_url + str(topic)+"/" + str(response2)+"/")
    data=r.text
    soup = BeautifulSoup(data, "html.parser")
    atags=soup.find_all('a')
    for links in atags:
        href=links.get("href")
        if re.search("^https://www.thehindu.com/{}/{}.*-.*".format(topic, response2), str(href))!=None and str(href) not in news:
            news.append(str(href))
    for new in news:
        articles=[]
        r1=requests.get(new)
        info=r1.text
        soup = BeautifulSoup(info, "html.parser")
        #title = soup.find('title')
        #finding dates of articles
        meta=soup.find_all("meta")
        for tags in meta:
            if tags.get("name", None) == "modified-date":
                rawdate=tags.get("content", None)
                date=rawdate.split("T")[0]
                articles.append(date)
        articles.append(new)
        all_articles.append(articles)
        #sorting the articles according to date
        sorted_articles=sorted(all_articles,key=lambda x:datetime.strptime(x[0],"%Y-%m-%d"), reverse=True)
        #returning latest 10 articles
    if len(sorted_articles)<10:
        return(sorted_articles)
    else:
        return(sorted_articles[0:10])

while True:
    r=requests.get(url+"getUpdates")
    updates=json.loads(r.text)
    try:
        command=updates["result"][len(updates["result"])-1]["message"]["text"]
        msg_time=updates["result"][len(updates["result"])-1]["message"]["date"]
        if command=="/start" and msg_time>time2:
            #sending intial hardcoded buttons
            time=send_buttons(text, id, reply_markup)

            #returning the response from clicked button
            response=hear_response(time)

            #fetching urls and button text for sub-categories
            buttons,sublinks=get_subnews(response)

            #creating the sub-category buttons
            reply_markup2=create_sub_buttons(buttons)
            reply_markup2=json.dumps(reply_markup2)

            #sending the sub-category buttons
            time2=send_buttons(text2, id, reply_markup2)

            #returning the response from clicked button
            response2=hear_response(time2)

            send_msg("Fetching the latest news for you in a minute\nPlease Wait ^_^", id)

            #scraping the articles
            final_articles=fetch_news(response, response2)

            #sending the latest articles
            for articles in final_articles:
                message="Date(yy/mm/dd): " + str(articles[0])+"\n\n"+str(articles[1]+"\n")
                send_msg(message, id)
    except:
        continue

#Telegram by default shows the preview of the articles, but for some reason if it does not show you can append the title of news
#uncomment line 135 and append title.string to articles list
#also concat the title in the variable message, on line 186

