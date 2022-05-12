import smtplib, ssl

'''port = 465  # For SSL
smtp_server = "smtp.gmail.com"'''
sender_email = "infinityloop_33@hotmail.com"  # Enter your address
receiver_email = "jiimee_games@hotmail.com"  # Enter receiver address
password = "Grupo33ing2"
message = """\
Subject: Hi there

This message is sent from Python."""

'''context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)'''

conn = smtplib.SMTP('smtp-mail.outlook.com',587)  
type(conn)  
conn.ehlo()  
conn.starttls()  
conn.login(sender_email,password)  
conn.sendmail(sender_email,receiver_email,'Subject:Test')  
conn.quit() 