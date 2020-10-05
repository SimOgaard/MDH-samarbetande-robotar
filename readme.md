[google colab for training conv found here](https://colab.research.google.com/drive/1vy0ZHaKx9eAAph-YvTwriSFDLDKpweoz?usp=sharing)

THIS IS DONE: Serverns choose order ska endast ha norr öst syd väst oavsätt om andelen direktioner är 1. THIS IS NOT DONE: Den ska itereras tills en okänd colors har funnits. 

När den kollar på map, ska indexes större än eller mindre än dimensionen för mappen ignoreras och inte ge crash (list index out of range) !!!!!Använd validCoord!!!!!!

Använd statusUpdateHTML där den behövs

Carmap ska innehålla alla fyra rotationer av mappen

Lyckas transfera information från arduino och ta emot information från py

Building: (Stadigare build)
    Fixa så att cameran sitter helt rätt (hur långt ifrån marken, hur långt fram, hur mycket vinklat) 
    3d printa hörn delar som kan hålla i tre balkar åt alla dimensioner
    Använd dessa för att förstärka "kranen"
    idk man prittie obsolite @ this point, its sturdy af with new build, was the axis that messed everything upp.

Ändra p, i, k termer för smooother driving
Ändra thresholds för cameran

Connectar:
Ändra status meddelande på bilen till ”observerar”.
Skicka till arduino att kolla efter hinder. 

Står stilla:
Börja med att säga till maixpy ”hitta legogubbar”. Kolla även vägtyp. Och hinder.

Skicka till servern vägtyp som den ser och att lego gubbar är borta. Samt hinder är borta.
Gå till ”börja köra läge” på maixpy.

Servern skickar till arduino att börja köra. Order = (0,1,2) beroende på den vägtyp den fick. 
Uppdatera car.map där den kollar. 
Ändra status meddelande på bil till kör (norr,öst,väst).

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