[ipynb file for training conv found here](https://colab.research.google.com/drive/1vy0ZHaKx9eAAph-YvTwriSFDLDKpweoz?usp=sharing)


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


ipynb
# TODO:
1.   Distort the shit outta images: (gritty, dark, noise) using prolly imgaug cuz u know it
2.   Retrain on theese fuckt up sony smart fridge looking ass images
3.   Test the old CNN agaisnt the new ones on theese fuckt up images

it is done and this is the results u fuck

weakest model did this when trained on fuckt up images

{'fscore': 0.8493919550982226, 'precision': 0.8598484848484849, 'recall': 0.8391866913123844}
Average prediction time:5.35787731768137 ms

less weak model did this when trained on fuckt up images

{'fscore': 0.9339449541284405, 'precision': 0.9271402550091075, 'recall': 0.9408502772643254}
Average prediction time:5.5791603992263 ms

weakest model did this when trained on normal images

{'fscore': 0.5445462114904247, 'precision': 0.4954545454545455, 'recall': 0.6044362292051756}
Average prediction time:5.511541443177495 ms

strongest model did this when trained on normal images

{'fscore': 0.5556831228473019, 'precision': 0.7333333333333333, 'recall': 0.44731977818853974}
Average prediction time:6.131902755982426 ms
