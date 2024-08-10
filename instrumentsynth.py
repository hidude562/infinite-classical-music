import math
import os
import random
import mido
import re
import json

def getAImidFromSong(songName):
    class Note:
        def __init__(self, msgOn, msgOff):
            self.note = msgOn.note
            self.length = msgOff.time - msgOn.time
            self.start = msgOn.time
            self.velocity = msgOn.velocity
            self.channel = msgOn.channel
            self.markedDuplicate = False

        def getChannelStrChar(self):
            match self.channel:
                case 0:
                    out_instrument = "%"
                case 1:
                    out_instrument = "^"
                case 2:
                    out_instrument = "&"
                case 3:
                    out_instrument = "*"
                case 4:
                    out_instrument = ";"
                case 5:
                    out_instrument = ":"
                case 6:
                    out_instrument = "'"
                case 7:
                    out_instrument = '"'
                case 8:
                    out_instrument = '"'
                case 9:
                    out_instrument = ")"
                case 10:
                    out_instrument = '{'
                case 11:
                    out_instrument = '}'
                case 12:
                    out_instrument = '['
                case 13:
                    out_instrument = ']'
                case _:
                    out_instrument = "("
            return out_instrument

        def getDynamicsStrChar(self):
            dynamic = "$"
            if (self.velocity > 108):
                dynamic = "$"
            elif self.velocity > 74:
                dynamic = "#"
            elif self.velocity > 40:
                dynamic = "@"
            else:
                dynamic = "!"
            return dynamic

        def toString(self):
            return str(self.note) + " " + str(self.start)

    class Notes:
        def __init__(self):
            self.notes = []

        def add(self, note):
            self.notes.append(note)

        def toAIformat(self):
            aiStr = ""
            notes.sort_notes()
            previousNoteStart = 0
            currentTimeNotes = []
            previousStartTimeGreaterThan0 = 0
            notesLen = len(self.notes)
            for noteIndex in range(notesLen):
                note = self.notes[noteIndex]
                for otherNote in currentTimeNotes:
                    if otherNote.note == note.note and round(otherNote.start) == round(note.start) and (otherNote.channel == note.channel or (note.channel > 13 and otherNote.channel > 13)): #
                        if (not otherNote.markedDuplicate):
                            if (otherNote.length > note.length):
                                note.markedDuplicate = True
                            else:
                                otherNote.markedDuplicate = True
                            # raise Exception("DUPLICATTEEEEEE", note.channel, otherNote.channel)

                if note.start == previousNoteStart:
                    currentTimeNotes.append(note)
                if note.start != previousNoteStart or noteIndex == notesLen - 1:
                    currentTimeNoteTimeKeeper = previousStartTimeGreaterThan0
                    for currentTimeNote in currentTimeNotes:
                        if (not currentTimeNote.markedDuplicate):
                            noteStr = \
                                (str(round(currentTimeNote.start - currentTimeNoteTimeKeeper)) + str(
                                    currentTimeNote.getDynamicsStrChar()) + str(
                                    round(currentTimeNote.length)) + str(currentTimeNote.getChannelStrChar()) + str(
                                    currentTimeNote.note))
                            currentTimeNoteTimeKeeper = currentTimeNote.start
                            aiStr += noteStr + "|"
                    currentTimeNotes = [note]
                    # When the time increases from the previous note more than 0, like 240, it will reset the currentTimeNotes to just the current note since it is the start
                    previousStartTimeGreaterThan0 = previousNoteStart
                previousNoteStart = note.start
            return aiStr

        def sort_notes(self):
            self.notes = sorted(self.notes, key=lambda note: note.start)

    mid = mido.MidiFile(songName)

    if(mid.length < 30):
        raise Exception("Song is too short (probably demo piece)")

    notesOnCount = 0
    tempo = 0
    ticksPerBeat = mid.ticks_per_beat
    tickMultiplier = 480 / ticksPerBeat
    absoluteTime = 0
    notesOn = []
    notes = Notes()

    for i, track in enumerate(mid.tracks):
        for msg in track:
            if str(type(msg)) == "<class 'mido.messages.messages.Message'>":
                if msg.type == "note_off" or getattr(msg, "velocity", None) == 0:
                    msg.time = msg.time * tickMultiplier
                    absoluteTime += msg.time
                    msg.time = absoluteTime
                    for noteOn in range(len(notesOn) - 1, -1, -1):
                        if notesOn[noteOn].channel == msg.channel:
                            if notesOn[noteOn].note == msg.note:
                                note = Note(notesOn[noteOn], msg)
                                notes.add(note)
                                notesOn.pop(noteOn)
                                break
                    notesOnCount -= 1
                elif msg.type == "note_on":
                    msg.time = msg.time * tickMultiplier
                    absoluteTime += msg.time
                    msg.time = absoluteTime

                    # Check if there is already a noteOn message with the same time and note value
                    duplicate_found = False
                    #for noteOn in notesOn:
                    #    if noteOn.time == msg.time and noteOn.note == msg.note and (
                    #            noteOn.channel == msg.channel or (msg.channel > 13 and noteOn.channel > 13)):
                    #        duplicate_found = True
                    #        raise Exception("DUPLICATTEEEEEE", noteOn.channel, msg.channel)

                    notesOn.append(msg)
                    notesOnCount += 1
                elif msg.type == "program_change":
                    absoluteTime += msg.time * tickMultiplier
                else:
                    try:
                        absoluteTime += msg.time * tickMultiplier
                    except:
                        pass
            else:
                if msg.type == "track_name":
                    absoluteTime = msg.time  * tickMultiplier
                elif msg.type == "end_of_track":
                    absoluteTime = 0
                else:
                    try:
                        absoluteTime += msg.time * tickMultiplier
                    except:
                        pass
    #if notesOnCount != 0:
    #    raise Exception("Faulty midi (not enough note_offs)")

    formatted = notes.toAIformat()
    return formatted

def split_string(s):
    # Split the string every 2500 characters or at the next "|"
    splits = re.findall(r'.{1,5000}(?:\||$)', s, re.DOTALL)
    return splits

midi_dir = "/home/nathan/Desktop/NNData2/THE MASSIVE DATASET HAHAHA/MMD_MIDI/"  # @param {type:"string"}

allData = ""
fileIndex = 0

allData = ""
chunk = ""
fileIndex=0
# Open the JSONL file
with open('/home/nathan/Desktop/NNData2/THE MASSIVE DATASET HAHAHA/MMD_scraped_genre.jsonl', 'r') as file:
    # Iterate through each line (each line is a separate JSON object)
    for line in file:
        try:
            # Load the line as a JSON object
            json_obj = json.loads(line)
            songPath = json_obj['md5']
            songPath = midi_dir + songPath[0]+"/"+songPath[1]+"/"+songPath[2]+"/"+songPath+".mid"

            fileSize = os.path.getsize(songPath)
            if (fileSize > 60000 or fileSize < 10000):
                raise Exception("Too big/too small midi")

            genres = ' '.join(str(item) for innerlist in json_obj['genre'] for item in innerlist)

            genres = genres.replace("---", " ")
            genres = genres.replace("%2c", " ")
            genres = genres.replace(",", " ")
            songData = " . start |" + getAImidFromSong(songPath)
            splitSongData = split_string(songData)
            for part in splitSongData:
                noLabel = random.random() > 0.99
                if noLabel:
                    chunk += ". nan |" + part + "\n"
                else:
                    chunk+=". " + genres + " |" +part + "\n"

        except Exception as e:
            print(e)
        fileIndex += 1
        if (fileIndex % 1000 == 0):
            with open("labelledFinal.txt", "a") as dataFile:
                print("WRITING")
                dataFile.write(chunk)
                chunk = ""


with open("anew8=9.txt", "a") as dataFile:
    print("WRITING")
    dataFile.write(chunk)
    chunk = ""