# Text_analysis_scrapy

INSTRUCTIONS
1. First, you need to set up a Scrapy project. If you haven't already installed Scrapy,
you can do so via pip:
~$ pip install scrapy
2. Once Scrapy is installed, you can create a new project using the following
command:
~$ scrapy startproject <article_extractor>
Note: You can use any name instead of article_extractor (Be careful to follow the
below steps accordingly)
3. Paste the given python file(text_analysis.py) in article_extractor > article_extractor
> spider.
4. Paste the given ‘requirement.txt’ in article_extractor > article_extractor > spider.
5. Paste the MasterDictionary folder in article_extractor > article_extractor > spider.
6. Paste the StopWords folder in article_extractor > article_extractor > spider.
7. Open terminal in article_extractor > article_extractor > spider
8. Install the required packages
~$ pip install -r requirements.txt
9. Append these below lines in the file article_extractor > article_extractor >
settings.py for sequential output (in same order of input)
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1
10. Run the Scrapy project
~$ scrapy crawl article11. The Location article_extractor > article_extractor > spider > ouput.xlsx contains
the output
Note: The time may vary according to the size of the data.
