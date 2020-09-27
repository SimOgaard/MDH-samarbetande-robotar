[google colab for training conv found here](https://colab.research.google.com/drive/1vy0ZHaKx9eAAph-YvTwriSFDLDKpweoz?usp=sharing)



Max av storleken på banan • 2 för bilars individuella karta

sätt opacitet på bilden på ögat och bilen. Så man ser under den.

Serverns choose order ska endast ha norr öst syd väst oavsätt om andelen direktioner är 1. Den ska itereras tills en okänd colors har funnits. 

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





building
    fixa så att cameran sitter helt rätt
    3d printa hörn delar som kan hålla i tre balkar åt alla dimensioner
    använd dessa för att förstärka "kranen"
    stadigare 


arduino 
    kolla om snyggare kod funkar
    ändra variablerna så den kan åka på en rak väg fint
    gör så den kan ta svängar


hemsidan
// make a better plan'd route (send 1,2 or 3 depending on best choise)
// mby a* algorythm

// after the order is sent:
// we will place an transparant image of the car over the newly changed car coord that is correctly rotated

// add status message for each car, aka im cleaning, or im driving etc


openmv
### TODO:
    # laneAppropiateImage               Copy binary version of image, invertera (not), använd som mask för mörkning. Tanken är att bara det ljusa ska bli mörkare. Fler itterationer? så att det ljusaste blir mörare än det lite ljusa
    #                                   Testa även multipy add subtract divide images, kolla om de gör som ovan om inte bättre
    # Snabbare funktioner               Tex image.clear() "verry fast" till skillnad från drawsquare. Även hur du använder numpy "vertecees" kunde adderas ihop tusen ggr snabbare än for loopar
    # Värden på:
    #           tresholds,
    #           osv
