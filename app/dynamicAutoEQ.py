from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
from pathlib import Path
from app.getFRoT import getFRoTList
from app.getFRfromFile import *
from random import randint
from app.computeFilters import *


def paraToIIR(paraEQ):
    string = ''
    for paras in paraEQ.values():
        string = string + f"iir:type=peak;f={paras[0]};g={paras[1]};q={paras[2]},"
    return string

def createParaEQFile(iem:str,target:str,paraEQ:dict):
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Parametric EQ).txt'

    string = ''
    i = 0
    for paras in paraEQ.values():
        i += 1
        string += f'Filter {i}: ON PK Fc {paras[0]} Hz Gain {paras[1]} dB Q {paras[2]}\n'
    open(filePath,'w').write(string)

def createPAFile(iem:str,target:str,paraEQ:dict):
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Poweramp).json'
    bands = [{"type":0,"channels":0,"frequency":90,"q":0,"gain":0.0,"color":0},{"type":1,"channels":0,"frequency":10000,"q":0,"gain":0.0,"color":0}]
    for paras in paraEQ.values():
        bands.append({"type":3,"channels":0,"frequency":paras[0],"q":paras[2],"gain":paras[1],"color": randint(-16711680,0)})
    string = str([{"name":f"{iem} [{target}]","preamp":0.0,"parametric": True,"bands": bands}]).replace("'",'"').replace("True","true")
    open(filePath,'w').write(string)

def createWaveletFile(iem:str,target:str,iemAQ):
    string = iemAQ.eqapo_graphic_eq()
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Wavelet,Equalizer APO).txt'
    open(filePath,'w').write(string)
    
def autoEQ(iem:str,target:str,config,concha_interference,treble_f_lower,upshift:int=60):
    FRlist = getFRoTList('frequency_responses')
    frequencies,gains = getFRfromFile(f'{FRlist[iem]}.txt',relativepath='frequency_responses')    
    Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets')

    iemAQ = FrequencyResponse(name=iem,frequency=frequencies,raw=gains)
    targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

    iemAQ.interpolate()
    iemAQ.center()
    iemAQ.compensate(targetAQ)
    iemAQ.smoothen()
    iemAQ.equalize(concha_interference=concha_interference,treble_f_lower=treble_f_lower,treble_f_upper=20000,treble_window_size=1/12,treble_gain_k=1,max_gain=99)

    targetAQ.interpolate()
    targetAQ.center()
    targetAQ.smoothen()

    peqs = iemAQ.optimize_parametric_eq(config, 48000)
    #generate paraEQ filters
    i = 0
    paraEQ = {}
    for filt in peqs[0].filters:
        i += 1
        paraEQ[i] = [round(filt.fc),round(filt.gain,1),round(filt.q,1)]
        #{1: [frequency,gain,q]}

    frequencies = list(iemAQ.frequency)
    gains = list(iemAQ.raw)
    newGains = list(iemAQ.raw+iemAQ.parametric_eq)

    Tgains = list(targetAQ.raw)

    for i in range(len(frequencies)):
        gains[i] += upshift
        newGains[i] += upshift
        Tgains[i] += upshift

    #generate IIR string
    IIRstring = paraToIIR(paraEQ)
    #Create files
    createParaEQFile(iem,target,paraEQ)
    createPAFile(iem,target,paraEQ)
    createWaveletFile(iem,target,iemAQ)
    
    return frequencies, gains, newGains, Tgains, paraEQ, IIRstring
