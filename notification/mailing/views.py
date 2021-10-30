from django.shortcuts import render
from django.core.mail import send_mail
import json
from django.http import HttpResponse
from datetime import datetime, timedelta
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from smtplib import SMTPException
from collections import defaultdict

mails = {}
mail_sent = []

## Sending email using the send_mail functionilty of Django
def send_email(subject,message,to):
    send_mail(
        subject=subject,
        message=message,
        recipient_list=to,
        from_email=settings.EMAIL_HOST_USER,
        fail_silently=False
    )

@csrf_exempt
def send_notification(request):
    if request.method=='POST':
        error_log = {}
        responsedata = {}
        try:
            request_data = json.loads(request.body)
        except Exception as e:
            ## If the request data was not in Json Format or was incorrect
            return HttpResponse(json.dumps("invalid Json String for request"),status=400,content_type='application/json')
        ## For multiple emails sent via same request, we iterate the dictionary
        for d,values in request_data.items():
            notification_data = {}
            mail_time = datetime.now()
            message = values['message']
            to = values['to']
            ## The recipents of the mail needs to be in a list
            if isinstance(to,list):
                to = to
            else:
                to = [to]
            subject = values['subject']
            retry = 0
            sent = False
            ## Implementing mailing with 3 retries
            while retry<4 and not sent:
                if retry>0:
                    print('retrying....')
                retry+=1
                try:
                    send_email(subject,message,to)
                    sent = True
                except SMTPException as e:
                    if retry==4:
                        error_log[d] = [to,str(e)]
                except Exception as e:
                    if retry==4:
                        error_log[d] = [to,str(e)]
            if sent:
                for client in to:
                    notification_data[client] = "Mail sent successfully!"
                    if mails.get(client,None) is not None:
                        mails[client][mail_time]['subject'] = subject
                        mails[client][mail_time]['message'] = message
                        mails[client][mail_time]['success'] = True
                    else:
                        new_client_data = defaultdict(dict)
                        new_client_data[mail_time]['subject'] = subject
                        new_client_data[mail_time]['message'] = message
                        new_client_data[mail_time]['success'] = True
                        mails[client] = new_client_data
                    mail_sent.append((mail_time,client))
            else:
                for client in to:
                    notification_data[client] = "Mail failed! Please check the error log!"
                    if mails.get(client,None) is not None:
                        mails[client][mail_time]['subject'] = subject
                        mails[client][mail_time]['message'] = message
                        mails[client][mail_time]['success'] = False
                    else:
                        new_client_data = defaultdict(dict)
                        new_client_data[mail_time]['subject'] = subject
                        new_client_data[mail_time]['message'] = message
                        new_client_data[mail_time]['success'] = False
                        mails[client] = new_client_data
                    mail_sent.append((mail_time,client))
            responsedata[d] = notification_data
        responsedata['error_log'] = error_log
        ## Assumption for sending 200 Status Code, if we are sending more than one notification, it maybe that the mailing service
        ## may fail for one of the message but succeed for others, so I'm sending status code 200 that this API was successfully hit
        ## but error logs will show the failed response for that particular message
        return HttpResponse(json.dumps(responsedata),status=200,content_type='application/json')
    ## If request type was not post
    return HttpResponse(json.dumps('Invalid request type'),status=400,content_type='application/json')


## Api for searching the results, only implemented date time and client
@csrf_exempt
def search(request):
    ## Assuming it to be a post request so I can pass Json Data.
    if request.method=='POST':
        request_data = json.loads(request.body)
        ## to check if the search is based on datetime or client
        if request_data['search_on']=='datetime':
            responsedata = {}
            # Setting the start and end datetime to some values which can be used to search if one of them is absent
            start_date_time = datetime(2021,1,1)
            end_date_time = datetime.now()
            if request_data.get('start_date_time',False):
                start_date_time = request_data['start_date_time']
                start_date_time = start_date_time.replace('/','')
                start_date_time = start_date_time.replace(':','')
                ## Convert string to datetime object for comparison
                try:
                    start_date_time = datetime.strptime(start_date_time,'%Y%m%dT%H%M%S')
                except:
                    ## Since I am only taking in consideration datetime format to YYYY/MM/DDTHH:mm:ss checking if this format is not followed
                    ## Can be easily implemented from the front end
                    return HttpResponse(json.dumps('Invalid date time format. Please use YYYY/MM/DDTHH:mm:ss (dateTtime)'),status=400,content_type='application/json')
            if request_data.get('end_date_time',False):
                end_date_time = request_data['end_date_time']
                end_date_time = end_date_time.replace('/','')
                end_date_time = end_date_time.replace(':','')
                try:
                    end_date_time = datetime.strptime(end_date_time,'%Y%m%dT%H%M%S')
                except:
                    ## Since I am only taking in consideration datetime format to YYYY/MM/DDTHH:mm:ss checking if this format is not followed
                    return HttpResponse(json.dumps('Invalid date time format. Please use YYYY/MM/DDTHH:mm:ss (dateTtime)'),status=400,content_type='application/json')
            ## Checking for all the mails sent till now. All those mails which fall between this datetime range will be added to the results
            for x in mail_sent:
                client_data = {}
                if start_date_time<=x[0]<=end_date_time:
                    if(responsedata.get(x[1],None)) is not None:
                        continue
                    for d,v in mails[x[1]].items():
                        if start_date_time<=d<=end_date_time:
                            dt = d.ctime()
                            client_data[dt] = v
                    if bool(dict):
                        responsedata[x[1]] = client_data
            return HttpResponse(json.dumps(responsedata),status=200)
        elif request_data['search_on']=='client':
            ## Getting the client name to which the mail was sent, e.g., vishutyagi018@gmail.com
            client = request_data['client']
            if mails.get(client,None) is not None:
                responsedata = defaultdict(dict)
                for d,v in mails[client].items():
                    dt = d.ctime()
                    responsedata[dt] = v
                return HttpResponse(json.dumps(responsedata),status=200,content_type='application/json')
            else:
                ## If no such client exist return a not found error
                return HttpResponse(json.dumps('No such client exists'),status=404,content_type='application/json')
    ## If client or datetime based searching is not followed.
    return HttpResponse(json.dumps("only client and datetime based searching is supported (Please check search_on value in request)"),status=400,content_type='application/json')

### generate the complete report of the data.
@csrf_exempt
def report(request):
    if request.method=='GET':
        report_response = {}
        ## Since my mails dictionary uses clients as key, I'll iterate on that
        for client, data in mails.items():
            ## This set tracks the messages and subject for each users to count duplicates
            sent_message = set()
            client_data = mails[client]
            client_report = defaultdict(dict)
            for d, v in client_data.items():
                dt = d.strftime('%d/%m/%Y')
                ## The client report dictionary stores the metrics for each date for each client
                ## If the data is not yet present in the dictionary, I'll add the key for that date and add the various other
                ## metrics here.
                if client_report.get(dt,None) is None:
                    client_report[dt]['total_messages'] = 0
                    client_report[dt]['mail_sent_successfully'] = 0
                    client_report[dt]['failed_mails'] = 0
                    client_report[dt]['duplicate_set'] = 0
                
                ## Updating the message count for that date
                client_report[dt]['total_messages'] += 1

                ## Checking for duplicates
                if (v['subject'],v['message']) in sent_message:
                    client_report[dt]['duplicate_set'] += 1
                sent_message.add((v['subject'],v['message']))

                ## Checking for successful and failed messages
                if v['success']:
                    client_report[dt]['mail_sent_successfully']+=1
                else:
                    client_report[dt]['failed_mails']+=1
            
            ## Adding the client level report by dates to the complete report
            report_response[client] = client_report
        # print(report_response)
        return HttpResponse(json.dumps(report_response),status=200)
    return HttpResponse(json.dumps('Invalid request type, please make a get request'),status=400)