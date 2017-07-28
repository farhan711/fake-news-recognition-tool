# Each time you run this script (which requires Pattern),
# it collects articles from known sources and their bias,
# and appends to a CSV-file (/data/news1.csv)

from pattern.db  import Datasheet
from pattern.db  import pd
from pattern.web import Newsfeed
from pattern.web import URL
from pattern.web import DOM
from pattern.web import plaintext

# To estimate the level of bias:
# https://mediabiasfactcheck.com
# http://www.fakenewschecker.com

sources = { 

    (4, 'right', 'fake', 'Departed'                  ) : 'http://www.ndtv.com/rss',
    (4, 'right', 'fake', 'Reuters'          ) : 'http://in.reuters.com/tools/rss',
    (4, 'right', 'fake', 'BBC News'              ) : 'http://www.bbc.com/news/10628494',
    (4, 'right', 'fake', 'Truth Revolt'              ) : 'http://www.truthrevolt.org/rss.xml',
    (4, 'right', 'fake', 'news 18 Conservatives'       ) : 'http://www.news18.com/rss/',
    (4, 'right', 'fake', 'American Free Press'       ) : 'http://americanfreepress.net/feed/',
    (4, 'right', 'fake', 'Times of india'      ) : 'http://timesofindia.indiatimes.com/rss.cms',


}

PATH = pd('..', 'data', 'news1.csv')

try:
    csv = Datasheet.load(PATH)
    seen = set(csv.columns[-2]) # use url as id
except:
    csv = Datasheet()
    seen = set()

for (level, bias, label, name), url in sources.items():
    try:
        f = Newsfeed()
        f = f.search(url, cached=False)
    except:
        continue

    for r in f:

        # 1) Download source & parse the HTML tree:
        try:
            src = URL(r.url).download(cached=True)
            dom = DOM(src)
        except Exception as e:
            continue

        # 2) Find article text w/ CSS selectors:
        for selector in (
      "article[class*='node-article']",            # The Hill
         "span[itemprop='articleBody']",
          "div[itemprop='articleBody']",
          "div[id='rcs-articleContent'] .column1", # Reuters
          "div[class='story-body']",
          "div[class='article-body']",
          "div[class='article-content']",
          "div[class^='tg-article-page']",
          "div[class^='newsArticle']",
          "div[class^='article-']",
          "div[class^='article_']",
          "div[class*='article']",
          "div[id*='storyBody']",                  # Associated Press
          "article",
          ".story"):
            e = dom(selector)
            if e:
                e = e[0]
                break

        # 3) Remove ads, social links, ...
        try:
            e("div[id='rightcolumn']")[0]._p.extract()
            e("div[class='section-blog-right']")[0]._p.extract()
            e("div[class='blog-sidebar-links']")[0]._p.extract()
            e("div[role='complementary']")[0]._p.extract()
        except:
            pass

        # 4) Remove HTML tags:
        try:
            s = plaintext(e)
            s = s.strip()
        except:
            continue

        #if not s:
        #    print r.url
        #    print
        #    continue

        # 5) Save to CSV:
        if r.url not in seen:
            seen.add(r.url)
            csv.append((
                name, 
                label, 
                bias, 
                str(level), 
                r.title, 
                s, 
                r.url, 
                r.date
            ))
            print name, r.title
            print

    csv.save(pd(PATH))

# To read the dataset:
# for name, label, bias, level, title, article, url, date in Datasheet.load(PATH):
#     level = int(level)