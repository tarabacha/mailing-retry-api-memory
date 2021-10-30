# hevodata SDE assignment

**By Vishu Tyagi**

* This assignment is implemented in Python using Django, the requirements.txt file is available in the repo itself can be used for getting necessary requirements *

## Tool used for testing
 [Postman](https://www.postman.com/) is used for testing the APIs.

## Data Structures used

As database is not available, the following the data structures are used to store the data in memory:
[Dictionary](https://docs.python.org/3/tutorial/datastructures.html)

[Default Dictionary](https://docs.python.org/3/library/collections.html)

**dict** is a key-value pair data structure that can store data similar to map in c++ but the type of data can be different.

**defaultdict** is a dictionary-like object which is a subclass of dict class. It can store a number of various datatypes as a part of the dictionary. A defaultdict can store objects like list, dict, int, etc.

## Framework and API Used

**Django:** The Django backend framework for creating the APIs. It is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It is free and open source framework that can be used to create various app. More about the framework can be found on [Django Project](https://www.djangoproject.com/)

**Gmail:** Gmail provides a free of cost mailing service using a user's gmail account. More about the service can be found [here](https://medium.com/@_christopher/how-to-send-emails-with-python-django-through-google-smtp-server-for-free-22ea6ea0fb8e). This is an easy to use functionality. I have discussed how a user can update the credential to use the service in my app in the next section.

## Configuring the project to use GMail service

To use the Gmail Service, one needs to create a *.env* file to make sure that the environment variables to match the setting.py email backend setup. The .env file needs the following two lines:
```
EMAIL_HOST_USER=*your_email_address*
EMAIL_HOST_PASSWORD=*generated_app_password*
```
After updating these two fields, one can run the server and test the API as mentioned in the final section. 

## Notification API

### Send Mail Functionality
**send_mail()** is a django wrapper which can be used to send emails using a mailing backend from one's django app.It is a part of the *django.core.mail*. The exception for SMTPException which is one the checked Exception available with send_mail(). The data is stored as follows:

### Data Structures Used
*mails:* mails is a python dict object that stores a default dictionary as value with the client to which the mail was sent as the key. The defaultdict object contains the datetime on which the mail was sent as the key and a dictionary as the value. The underlying dictionary in defaultdict conatins the subject, message, and whether the mail was successfully sent or not.

*mail_sent*: It is a list of tuples which store a pair of datatime on which mail was sent and client as the values in the list. This list is later used inside the search API.

## Search API

The search API can work for two setups which are discussed below:
**datetime:** The mails can be searched on the basis of a datetime which can be provided in a string format defined as *YYYY/MM/DDTHH:mm:ss*. One can provide two values, one for the *start_date_time* and another as *end_date_time*. By default the values for *start_date_time* is *2021-01-01* and *end_date_time* is the present time when API call was made. This returns a JSON object with 200 HTTP_OK status. **NOTE:** If the datetime is not in the specified format, the API will generate a 400 Bad Request error with the error message being: *Invalid date time format. Please use YYYY/MM/DDTHH:mm:ss (dateTtime)*

**client:** Another method to search the mails is by using the client to which the mail was sent. This is a simple method of searching and returns a JSON object if there is such a client or a 404 NOT FOUND Error if no such user exist.

**NOTE:** If none of these two is used a bad request error with status code 400 is raised with response saying: *only client and datetime based searching is supported (Please check search_on value in request)*

## Report API:
It is a simple GET API in which the metrics are stored in a dictionary (*response_data*) with the client as the key. This dictionary further contains a defaultdict, whose basis is a dictionary. The key of the defaultdict will be the date on which the email was sent and the underlying dictionary stores metrics like *total_messages*, *mail_sent_successfully*, *failed_mails*, and *duplicate_set*. The names are self explantoary.

# USING THE APIs

To use th APIs, I have defined how one can make a request with what the JSON data one needs to pass in the request and what type of request one needs to make. But before that you should run the server as follows. In the directory where *manage.py* is present, please run the following command after setting up the virtualenv using the *requirements.txt*:
```python3 manage.py runserver```

### Notification API:
This is a **PUT** API. Sending any other type of API will generate an error response of type 400 Bad Request with the message saying: *Invalid request type*. The following set of instructions reflect how one can send a request to the server on the notification api.
-To send a request please use POSTMAN with the following url: *http://127.0.0.1:8000/send/*. **NOTE**: I'm assuming the server is running on default 8000 port on the localhost.
-You can send the data to the server using the body with raw input in POSTMAN. An exmaple of the data is provided below:
```
{
	"notification_1":	{
		"to":["vishutyagi018@gmail.com"],
		"message": "hi",
		"subject": "test"},
	"notification_2":	{
		"to":["1"],
		"message": "hi",
		"subject": "test"}
				
}
```
-A successful request looks like:
![Successful API Request from POSTMAN](https://github.com/strider187/hevodataassignment/blob/main/screenshots/successful_notification.png?raw=True)

-A failed request looks like:
![Failed API Request from POSTMAN](https://github.com/strider187/hevodataassignment/blob/main/screenshots/mail_failed.png?raw=True)

-Retrying on a failed request looks like:
![Retrying on failed API Request from POSTMAN](https://github.com/strider187/hevodataassignment/blob/main/screenshots/retry_on_failure.png?raw=True)

-Multiple notifications with one failure and one success:
![Multiple notification with one failure and one success](https://github.com/strider187/hevodataassignment/blob/main/screenshots/multiple_notification_with_failue.png?raw=True)


### Search API
The search API is again a **POST** API, but only for the sake of passing the querying data as JSON. Sending any other type of request will generate an error response of type 400 Bad Request with the message saying: *Invalid request type*. The following set of instructions reflect how one can send a request to the server on the search api.
-To send a request please use POSTMAN with the following url: *http://127.0.0.1:8000/search/*. **NOTE**: I'm assuming the server is running on default 8000 port on the localhost.

-You can send the data to the server using the body with raw input in POSTMAN. An exmaple of the data is provided below:
```
{
	"search_on":"datetime",
	"start_date_time": "2021/08/01T0:0:0"
}
```
In this case, one can choose the value of search between *datetime* and *client*. Based on the same you can send the query data as follows:
  - For the datetime query, you can pass two values:
    -- start_date_time: Define the starting time of the query.
    -- end_date_time: Define the end time of the query.
**NOTE:** By default, the values for these two is set as '2021-01-01' for start_date_time and the datetime when the API call was made for end_date_time. So, passing only one point can also work or not passing either can too.
  - For the client query, you need to pass only one value but that is necessary:
    -- client, the client is actually the email of the client to which emails are being sent.
**NOTE** If no email is provided or if client is not passed, a 404 not found error will be generated with the message: *No such client exists*

-The search looks like:
![Search API Request from POSTMAN](https://github.com/strider187/hevodataassignment/blob/main/screenshots/searching.png?raw=True)


### Report API
The report API is a simple **GET** API, sending any other type of request will generate an error response of type 400 Bad Request with the message saying: *Invalid request type*. For this request no data needs to be passed as this API doesn't take any input data. It can be called from the link: *http://127.0.0.1:8000/report/*

-The report API looks like:
![Report API Request from POSTMAN](https://github.com/strider187/hevodataassignment/blob/main/screenshots/report.png?raw=True)
# mailing-retry-api-memory
