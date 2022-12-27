# SUScraper

First replace the X in the configuration.ini.example with your settings, then remove the .example so the file is named configuration.ini

EXAMPLE:

```
[EmailSettings]
port = 587
smtp_server = smtp.MySMTPServer.com
sender_email = This.IsMy@Email.com
receiver_email = This.IsMy@Email.com
password = V3ryStronkhPa55word!
```
If you want to setup the service for multiple people, just add email addresses with commas
```
[EmailSettings]
port = 587
smtp_server = smtp.MySMTPServer.com
sender_email = This.IsMy@Email.com
receiver_email = This.IsMy@Email.com,This.IsMyFriend@Email.com
password = V3ryStronkhPa55word!
```

Have a cronjob call the main.py every X hours (I use two) and adjust the search criteria in the main.py to your needs
```
0 */2 * * * python3 /home/user/SUScraper/main.py > /home/user/suscraper.log 2>&1
```
