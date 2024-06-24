started after making the menu previously added on github, it took me a little less than 1 month to finish the whole game so i finished at the end of may (without sprite, just the map was made) then i wanted to create images myself (i'm very bad at drawing so i took my time to like it a minimum) and then i made the code to integrate and animate these images, where by the way i wanted to add a save option which took me 1 week. By trying to add things bit by bit, i ended up taking 2 weeks to post the code (some sprites and animations are still missing, but the main thing is there).

_________________________________

**An endless survivors game**

A defined time between each round, at each round you can:
- choose a bonus and continue
- save and exit (the current round will not be taken into consideration)
 
Save management:
- a continue button will appear if a save is available
- temporarily saved in a variable
- if you quit completely, it will be written to a JSON file
- if a save is available at game launch, retrieve it
- the save file will be deleted if you die
 
enemies (3 differents monster available) : 
managed by a spawner, every 10 seconds the spawner will assign a random time for the monsters to appear, for example at [12, 16, 17, 18, 20] seconds.
- mushroom -> will follow you no matter what
- golem -> as long as you don't approach it, it will have random moves
- goblin -> will stay at a distance from you, making random moves to dodge and throw projectiles at you

https://github.com/PheY29/Survivor_games/assets/131706411/0849a39a-96e5-4db7-b59b-8ebf804cd072

 
Current item:
- heal collectable at 75% drop on monsters (no sprite for the moment)
    
Others:
- most collisions are handled by sprite masks

![mask](https://github.com/PheY29/Survivor_games/assets/131706411/89198bd1-1032-44fa-8418-47b8b87c990e)
