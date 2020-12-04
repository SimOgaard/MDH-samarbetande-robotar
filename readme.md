[google colab for training conv found here](https://colab.research.google.com/drive/1vy0ZHaKx9eAAph-YvTwriSFDLDKpweoz?usp=sharing)

find pedestrian doesnt find walkover
servo push/shove doesnt work
hallelement gives too many valuez



crop image or only use roi for line regresion 


ändra middle line roi efter de längre linjerna, aka remove crossing och småpluppar, kanske nor,xor,and på två binära bilder

styr med mittlinjen, när du ser att du håller på att åka över ett övergångställe, byt till vänster och höger linjer
ändra find pedestriancrossover så att den filtrerar ut små väglinjer från bilden med errode och sedan dilate, för att sist find blobs med stor margin
kolla hur bred pedestirancrossover är för att veta om den är middle pedestriancrossover, om de inte är bred kolla dens cx position, om den ligger åt vänster är den left pedestrian, ligger den åt höger är den right pedestrian
finns nu right och left eller middle pedestrian så ska du byta till vänster och höger linjer annars mittlinjen 

Dämpad regritions linje, som i opencv. Eller större roi när du kollar efter linjen (y-axeln)

KVARSTÅENDE BIL
Ta hallelement kontrollern från er förra och lägg in i den nya, ändra även då resistorn

TVÅ BILAR
ALLA BILAR ATT KÖRA PÅ BATTERI

BUGG:
Fixa reglering för svängningar
Hårdkodad sväng för order 1, 2

Reglera efter ett övergångsställe/antalet väglinejer








find vit blob med nästan ingen blob to blob distance, gör det helt svart. Den ska ha pixel threshold > väglinje

Serverns choose order ska itereras tills en okänd väg har funnits. 

Carmap ska innehålla alla fyra rotationer av mappen IS IT SMART THOE?

Building: (Stadigare build)
    Fixa så att cameran sitter helt rätt (hur långt ifrån marken, hur långt fram, hur mycket vinklat) 

Ändra p, i, k termer för smooother driving
Ändra thresholds för cameran

När den kör:
Sväng vid höger/vänster sväng:
    1. Använd linjen för att reglera svängen.
    2. Reglera position och hård koda sväng.
Sväng vid korsning:
    1. (använd övergångsställen för att reglera position) sedan (sväng hård kodad sväng)
Följ linjen kommer vid alternativ 1, 1:
    Använda samma reglering för att hålla sig till vägen.
Följ linjen kommer vid alternativ 2, 1:
    Använda reglering som vid alternativ 1, 1 men icke när det är vänster/höger sväng

För att veta distans:
Använd hallellement.
Använd reglering när övergångsställen syns.

Efter distansen är känd och vi vet att det är en ny vägtyp som vi reglerat oss till att stå perfekt på:
Stå stilla.
Skicka till serven ”jag har kört klart”.
Ändra i serven HTML sådant att bilen har förflyttats.