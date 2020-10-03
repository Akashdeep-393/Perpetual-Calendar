My Project is a Perpetual Calendar website for the years 2001-2099.

A Perpetual Calendar is a calendar that is valid for many years and is usually used to look up the day of the week for any given date. My calendar website displays a perpetual calendar for the 21st century and includes the days of the week for each date and the dates of new and full moons as well. I have also included 5 festivals - Christmas, New Year, Chinese New Year, Diwali and Eid-al-Fitr. The last three are lunar festivals which require complex algorithms to compute.

My website uses some of the documentation from the CS50 distribution code for Finance. However, I have added my own algorithms to add and delete events to my calendar as well as delete the users account. The user's account and tale of events is maintained using a SQL database and manipulated using Flask. Jinja, HTML and CSS have been used to create the webpage templates.

My Python algorithm takes the user input username and password, validates them and enters them into the SQL users table during registration. At the point of registration, the algorithm generates the perpetual calendar.

The algorithm calculates the number of days from 1st Jan 2001 to the beginning of the current month of the current year, divides by the length of a lunar month, and takes the remainder to find the number of days till the next new moon and full moon.

It checks whether the new moon is the second after the winter solstice and if it is, then the corresponding date is entered as the date of Chinese New Year.

Otherwise it checks whether the new moon is the second after the autumn equinox and if it is, then the corresponding date is entered as the date of Diwali.

It calculates the date of Eid-Al-Fitr by calculating the number of days from the first Eid-Al-Fitr of the century to the beginning of the current year, dividing this by the length of a lunar year and taking the remainder to find the number of days since the last Eid-Al-Fitr, and calculating the number of days till the next Eid-Al-Fitr.

The website then allows the user to login by taking the user input username and password and searching for them in the SQL database.

The index page of my website prompts the user to type in a month and a year and it displays the corresponding calendar and events table by querying the SQL events database which has the user's username.

The algorithm calculates the number of days from 1st Jan 2001 to the beginning of the current month of the current year, divides by 7, and takes the remainder to find the day of the week that the month begins on and displays the calendar for that month accordingly.

The Add Events and Delete Events link enables users to add and delete events from their SQL events table by inputting the name and date of the event.

The Log Out link enables the user to logout by clearing the session cache.

The Delete Account link enables the user to delete their account by deleting their username and password from the users table, deleting their entire events table, and clearing the session cache.
