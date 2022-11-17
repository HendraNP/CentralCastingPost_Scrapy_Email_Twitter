# -*- coding: utf-8 -*-
import scrapy
import smtplib
import MySQLdb
from datetime import datetime

from scrapy.mail import MailSender

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_email = "sender"

conn = MySQLdb.connect(host='localhost',database='lacc',user='root',password='')

cursor = conn.cursor()
cursor.execute("""select email from list_email""")
list_email = cursor.fetchall()



class LACCSpider(scrapy.Spider):
    name = 'LACCSpider'
    start_urls = ['https://centralcasting.com/jobs/?location=losangeles']


    def parse(self, response):

        print("procesing:"+response.url)
        #Extract data using css selectors
        job=response.css('.cff-text').extract()
        job = [w.replace('<span class="cff-text" data-color="">', "") for w in job]
        job = [w.replace("&amp","&") for w in job]
        job = [w.replace("</span>","") for w in job]
        #job = response.xpath("//span[@class='cff-text']/text()").extract()
        jobdate=response.css('div.cff-item::attr(data-cff-timestamp)').extract()

        row_data=zip(job,jobdate)

        #Making extracted data row wise
        for item in row_data:
            #create a dictionary to store the scraped info
            timestamp = datetime.fromtimestamp(int(item[1]))
            scraped_info = {
                'timestamp' : timestamp,
                'job' : item[0]
            }
            cursor.execute("""select job_desc from job_list""")
            first_job = cursor.fetchone()
            print(first_job)
            if(first_job != item[0]):
                sql = "INSERT INTO job_list (job_desc, date) VALUES (%s, %s)"
                val = (item[0], timestamp)
                cursor.execute(sql, val)
                conn.commit()
                yield scraped_info

        #server = smtplib.SMTP('smtp.gmail.com', 587)
        #server.starttls()
        # server.login(from_email, "credential")
        # for mail in job:
            # for email in list_email:
                # msg = ""
                # msg = MIMEMultipart()
                # msg['From'] = from_email
                # msg['To'] = email[0]
                # msg['Subject'] = 'New Job Posted at Central Casting for ' + email[0]
                # msg['Content-Type'] = 'text/html'
                # for x in mail.split("<br>"):         
                    # msg.attach(MIMEText(x))
                    # msg.attach(MIMEText('\n'))
                # text = msg.as_string()
                # #server.sendmail(from_email, email[0], text)
        # server.quit()
        
        
        #yield or give the scraped info to scrapy
        #yield scraped_info

