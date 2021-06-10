from .models import FileSection, SectionCategory, StatusData, StatusSection, User, Directory
from django.utils import timezone
from collections import deque
import subprocess
import os

#creates model object to be pushed
def endSection(text, f, begin, end):
    splitted = text.split()
    cat = splitted[1]
    if cat == "loop":
        cat = splitted[2]
    sectCat = SectionCategory.objects.create (
        category=cat,
        lastUpdated=timezone.now(),
        validity=True
    )
    sectCat.save()
        

    sect = FileSection.objects.create (
        name=cat,
        description=text,
        creationDate=timezone.now(),
        category=sectCat,
        parentFile=f,
        lastUpdated=timezone.now(),
        sectBegin=begin,
        sectEnd=end,
        validity=True
    )

    sect.save()


def notFramaSect(f, line, begin, currLine, text, framaSect):
    if line.find("//@") != -1:
        text = line[line.find("//@")+2:]
        endSection(text, f, currLine, currLine)
        text = ''
    elif line.find("/*@") != -1:
        framaSect = True
        begin = currLine
        text = line[line.find("/*@")+2:]
        framaEnd = text.find(";")
        if text.find("*/") != -1:
            framaSect = False
        if framaEnd != -1:
            text = text[:framaEnd]
            endSection(text, f, currLine, currLine)
            text = ''
    return begin, text, framaSect

def inFramaSect(f, line, begin, currLine, text, framaSect):
    if text == '':
        begin = currLine
    if line.find("*/") != -1:
        framaSect = False
    framaEnd = line.find(";")
    if framaEnd != -1:
        text += line[:framaEnd]
        endSection(text, f, begin, currLine)
        text = ''
    else:
        text += line
    return begin, text, framaSect

#divides file into sections and pushes them to database
def createSections(f):
    with open(f.ffile.path, 'r') as currFile:
        ffile = currFile.readlines()
    currFile.close()
    framaSect = False
    text = ''
    begin = 1
    currLine = 1

    for line in ffile:
        if framaSect == False:
            begin, text, framaSect = notFramaSect(f, line, begin, currLine, text, framaSect)
        else:
            begin, text, framaSect = inFramaSect(f, line, begin, currLine, text, framaSect)
        currLine += 1

#adds some extras to directory model object used in directory tree determination
def addExtra(dire, username):
    if dire.parentDirectory is None:
        dire.path = dire.name + "/"
    else:
        dire.path = dire.parentDirectory.path + dire.name + "/"
    lines = ""
    parent = dire
    while parent.parentDirectory is not None:
        lines += "--"
        parent = parent.parentDirectory
    dire.level = lines
    currentUser = User.objects.get(login=username)
    newDire = Directory.objects.create (
        name=dire.name,
        description=dire.description,
        creationDate=timezone.now(),
        owner=currentUser,
        parentDirectory=dire.parentDirectory,
        path=dire.path,
        level=dire.level,
        lastUpdated=timezone.now(),
        validity=True
    )
    return newDire

#disactivates all entites in selected directory sub-tree
def disableChildren(dire):
    q = deque()
    q.appendleft(dire)
    dirdelete = []
    filedelete = []
    curr = dire
    for f in curr.files.all():
        filedelete.append(str(f.pk))
    while len(q) != 0:
        for ch in curr.children.all():
            q.appendleft(ch)
            dirdelete.append(str(ch.pk))
            for f in ch.files.all():
                filedelete.append(str(f.pk))
        curr.availability = False
        curr.save()
        curr = q.pop()

    return [dirdelete, filedelete]

#runs frama command on file under fpath path, with options specified in prover, rte, prop
def runFrama(fpath, prover, rte, prop):
    
    if (prover == "None" and rte == "No" and prop == "None"):
        result = subprocess.run (
            ['frama-c', '-wp', '-wp-print', fpath],
            capture_output=True,
            text=True
        )
        d = "------------------------------------------------------------"
        result = result.stdout

        dividResult = result.split(d)
        del dividResult[0]
        return dividResult, False

    stream = os.popen (
        getCommand(prover, rte, prop, fpath),
    )
    d = "[wp]"
    result = stream.read()
    dividResult = result.split(d)
    return dividResult, True


#creates result.txt for currently chosen file and returns result.txt content
def getResult(fpath):

    rpath = fpath[:fpath.rfind("/")] + "/result.txt"
    log = '-wp-log="r:' + rpath + '"'
    comm = "frama-c -wp " + log + " -wp-prover Alt-Ergo " + fpath

    os.system(comm)

    result = subprocess.run (
        ['cat', rpath],
        capture_output=True,
        text=True
    )
    return result.stdout

#creates command based on chosen options in tabs
def getCommand(prover, rte, prop, fpath):
    result = "frama-c -wp "
    if (prover != "None"):
        result = result + "-wp-prover " + prover + " "
    if (prop != "None"):
        result = result + '-wp-prop="' + prop + '" '
    if (rte == "Yes"):
        result = result + "-wp-rte "
    result = result + fpath
    return result

#parses compilation results
def parseCompilation(frama, sections, isAdvanced, username):
    result = []
    sectionNames = ["ssert", "variant", "requires", "exits", "continues", "lemma", "ensures", "assigns", "check", "Post-condition"]
    statusNames = ["Valid", "Invalid", "Unknown", "Timeout", "Proved", "Unchecked", "Counterexample"]
    i = 0

    for f in frama:
        if i == len(frama) - 1 and isAdvanced: #due to unusal last compilation section it's better to skip it
            quar = ("None", "", f, "", "")
            result.append(quar)
            return result
        matchst = next((status for status in statusNames if status in f), "None")
        matchse = next((section for section in sectionNames if section in f), "")
        if matchse == "variant" and f[f.find("variant")-1] == 'n':
            matchse = "invariant"
        elif matchse == "ssert":
            matchse = "assert"
        if matchse != "" and matchst != "None":
            begin, end = createStatus(matchse, matchst, f, sections, isAdvanced, username)
        else:
            matchst = "None"
            matchse = ""
            begin = ""
            end = ""
        quar = (matchst, matchse, f, begin, end)
        result.append(quar)
        i += 1
    
    if len(frama) != 0 and frama[-1][0] != 'G': #we shouldnt parse compilation warning, which is usually listed in the last section
        result[-1] = ("None", "", frama[-1], "", "")
    return result

def createStatus(matchse, matchst, f, sections, isAdvanced, username):
    if isAdvanced:
        divid = f.split('_')
        if divid[-1].find(matchse) != -1:
            num = 0
        elif divid[divid.index(matchse) + 1].isnumeric(): 
            num = int(divid[divid.index(matchse) + 1]) - 1
        elif matchse == 'assert' and divid[divid.index(matchse) + 1] == "rte":
            return "rte", ""
        else:
            num = 0

        sectObj = sections.filter(name=matchse).order_by('pk')[num]
        begin = getattr(sectObj, "sectBegin")
        end = getattr(sectObj, "sectEnd")
    else:
        divid = f.split(' ')
        num = divid[divid.index("line") + 1]
        num_filter = filter(str.isdigit, num)
        num = "".join(num_filter)

        try:
            sectObj = sections.get(sectBegin=num)
        except:
            return '', ''
        begin = num
        end = getattr(sectObj, "sectEnd")

    sectStat = StatusSection.objects.create (
        status=matchst,
        lastUpdated=timezone.now(),
        validity=True
    )

    user = User.objects.get(login=username)
    sectData = StatusData.objects.create (
        statusDataField=f, 
        user=user,
        lastUpdated=timezone.now(),
        validity=True
    )

    sectStat.save()
    sectData.save()

    setattr(sectObj, "status", sectStat)
    setattr(sectObj, "statusData", sectData)
    sectObj.save()

    return begin, end 

def addLineNumbers(content):
    offset = len(str(len(content)))
    for i in range(len(content)):
        content[i] = (offset - len(str(i + 1)))*' ' + str(i + 1) + "| " + content[i]
    return ''.join(content)