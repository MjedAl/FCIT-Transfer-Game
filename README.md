Hi. this was my submission for my college summer contest it was about converting the transferring rules to a python code in anyway (see poster.jpg).  
thankfully i got the first place out of 46 submissions.  
what i made was a game using PyGame library where player have to move around and reach the top based on his grades (rules)  

![Screenshot](Screenshot-1.JPG)

if a player pass the game it means that he can transfer so in that case we will check if the transfer is available this semester by reading the status from a google firebase database  
if it's open we will add his grades to the DB ( it's better to take it from ODUS to validate it but since i dont have access i'll ask the user to put it)  
there's a web-page where you can log in and see the students who are edible for the transfer and open or close the transfer  
https://www.a-fa.sa/FCIT_Transfer/ (or just open HTMLPART/index.html)  
Email: 1@mjed.xyz  
Password: 123321 (i know it's bad password, it's just for demo)  
With that being said i have also two notes.  
1- the code might not run as a .py because i used multiple libraries and edited in their code so it's better to open the .exe file  
2- i have tried using Arabic with printing other than the usual issues with LTR and RTL it's completely not supported in the windows console (when opening it from .exe)  
   so that's why i'll be printing in English :(.  

# Author: Abdulmajeed alahmadi
