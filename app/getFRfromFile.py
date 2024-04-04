import pathlib
import re

def getFRfromFile(file:str,relativepath:str='frequency_responses') -> tuple[list,list]: #file with extention (.txt)
    path = pathlib.Path(__file__).parents[1] / relativepath / f'{file.replace('.txt','')}.txt'
    lines = open(path,'r').readlines()

    frequencyList = []
    amplitudeList = []
    dico = {}
    for line in lines:
        values = re.findall(r"[-+]?(?:\d*\.*\d+)",line) #trouve float dans un str
        if len(values) == 2:
            dico[float(values[0])] = float(values[1])
    sortedDico = dict(sorted(dico.items())) 
    for fr,amplitude in sortedDico.items():
        frequencyList.append(fr)
        amplitudeList.append(amplitude)
    if amplitudeList[-1]<0:
        for i in range(len(amplitudeList)):
            amplitudeList[i] += 80
    return frequencyList,amplitudeList

