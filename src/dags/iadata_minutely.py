import datetime
import scrapy
import time
import os
from scrapy.crawler import CrawlerProcess
from airflow import DAG, models
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email_smtp


def send_available_appointment_alert(available_dates, is_test_mode=False):
    from twilio.rest import Client

    state = "--TEST--" if is_test_mode else ""

    #MAIL
    send_email_smtp(to=os.getenv("AIRFLOW__SMTP__SMTP_MAIL_FROM"),
                    subject=f"{state}IDATA Randevusu bulundu!",
                    html_content=f"<html><body>IDATA Randevu------> {time.ctime()} -> {available_dates}</body></html>")

    
    #SMS
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    message = client.messages.create(
         from_=os.getenv("TWILIO_FROM_PHONE_NUMBER"),
         body=f'{state}IDATA Randevu------> {time.ctime()} -> {available_dates}',
         to=os.getenv("TWILIO_TO_PHONE_NUMBER")
    )
    print(message.sid)


class IdataSpider(scrapy.Spider):
    name = 'idataSpider'
    
    idata_office_variables = models.Variable.get(os.getenv("IDATA_OFFICE_VARIABLE_NAME"), deserialize_json=True)
    idata_country_variables = models.Variable.get("ulke", deserialize_json=True)
    ulke_url_prefix = idata_country_variables[os.getenv("IDATA_COUNTRY_VARIABLE_NAME")]

    start_urls = [f'https://{ulke_url_prefix}-schengen.idata.com.tr/tr/appointment-form']

    def parse(self, response):

        cnt = response.xpath("//meta[@name='csrf-token']/@content")[0].extract()

        yield scrapy.FormRequest(
            url=f"https://{self.ulke_url_prefix}-schengen.idata.com.tr/tr/getcalendarstatus",
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRF-TOKEN':cnt},
            formdata={"getvisaofficeid": f'{self.idata_office_variables["getvisaofficeid"]}',
                      "getservicetypeid":f'{self.idata_office_variables["getservicetypeid"]}',
                      "getvisacountryid":f'{self.idata_office_variables["getvisacountryid"]}'},
            callback=self.parse_page2,
            cb_kwargs={'cnt': cnt}
        )

    def parse_page2(self,response,cnt):

        items = []
        for c in response.headers.getlist('Set-Cookie'):
            for i in str(c).split(';'):
                if i not in items:
                    items.append(i)

        yield scrapy.FormRequest(
            url=f"https://{self.ulke_url_prefix}-schengen.idata.com.tr/tr/getdate",
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     'Accept':'*/*',
                     'Cookie': ';'.join(items),
                     'Referer':f'https://{self.ulke_url_prefix}-schengen.idata.com.tr/tr/appointment-form',
                     'X-Requested-With':'XMLHttpRequest',
                     'Host':f'{self.ulke_url_prefix}-schengen.idata.com.tr',
                     'Origin':f'https://{self.ulke_url_prefix}-schengen.idata.com.tr',
                     'X-CSRF-TOKEN':cnt},
            formdata={"consularid": f'{self.idata_office_variables["consularid"]}',
                      "exitid":f'{self.idata_office_variables["exitid"]}',
                      "servicetypeid":f'{self.idata_office_variables["servicetypeid"]}',
                      "calendarType":f'{self.idata_office_variables["calendarType"]}',
                      "totalperson":f'{self.idata_office_variables["totalperson"]}'},
            callback=self.parse_getdate
        )

    def parse_getdate(self,response):

        import json
        res = json.loads(response.text)

        print(f'AvailableDate------> {time.ctime()} -> {res["firstAvailableDate"]}')

        if res["firstAvailableDate"] != "":
            send_available_appointment_alert(res["firstAvailableDate"])
            print(f'AvailableDate------> {time.ctime()} -> {res["firstAvailableDate"]}')

        if os.getenv("MODE") == "Test":
            print("TEST MODE!!!")
            send_available_appointment_alert(res["firstAvailableDate"],True)
            print(f'AvailableDate------> {time.ctime()} -> {res["firstAvailableDate"]}')

        


default_dag_args = {
    'owner': "cetingokhan",
    'start_date': datetime.datetime.now() - datetime.timedelta(days=1),
    'email': os.getenv("AIRFLOW__SMTP__SMTP_MAIL_FROM"),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1)
}



with DAG(dag_id="idata_dag",
         description='idata Dag',
         schedule_interval=datetime.timedelta(minutes=2),
         max_active_runs=1,
         default_args=default_dag_args,
         catchup=False
         ) as dag:


    crawler_settings={
        "DOWNLOAD_DELAY": 0.05,
        "DOWNLOAD_MAXSIZE": 0,
        "LOG_STDOUT": True,
        "MEMDEBUG_ENABLED": True,
        "TELNETCONSOLE_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_TIMEOUT": 60,
        "CONCURRENT_REQUESTS": 2,
        "LOG_LEVEL":"ERROR"
    }

    def shell_crawler_starter(**context):
        process = CrawlerProcess(settings=crawler_settings)
        process.crawl(IdataSpider)
        process.start()

    crawl_task = PythonOperator(
        dag=dag,
        task_id="shell_crawler_starter",
        python_callable=shell_crawler_starter
    )

    crawl_task