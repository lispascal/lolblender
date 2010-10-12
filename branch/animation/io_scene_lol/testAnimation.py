import lolAnimation

anmFilename = '/var/tmp/downloads/lol/DATA/Characters/Nasus/Animations/Nasus_Laugh.anm'

animation = lolAnimation.importANM(anmFilename)

for frame in animation:
    print(frame['L_toe'])

