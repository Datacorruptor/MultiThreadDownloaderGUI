import os
import winsound

import requests
import concurrent.futures
import random
import threading
import time

CHUNK_SIZE = 1024*1024*100
CHUNK_POOL = 16
FILE_POOL = 4
#1:52 1024*1024*10 32 4 1gb

COOKIE = None

USERAGENT = 'newandfresh'


HEADERS = {
    'user-agent':USERAGENT
}

if COOKIE!=None:
    HEADERS['cookie']=COOKIE

info = {}


executor = concurrent.futures.ThreadPoolExecutor(FILE_POOL)


def startDownloadBatch(urls=None):
    if urls is None:
        urls = [defaulturl]*10
    print(urls)
    x = threading.Thread(target=downloadBatch,args=(urls,))
    x.start()

def downloadBatch(urls=None):
    print(urls)
    if urls is None:
        urls = [defaulturl]*10
    executor.map(downloadFile, urls)


def downloadFile(url,dir = "downloads",filename = None):
    r = requests.head(url,headers=HEADERS)
    print(r.headers)

    if not os.path.exists(dir):
        os.mkdir(dir)
    if filename is None:
        rnd = str(random.randint(1000000, 9999999))
        filename=rnd+'_'+url.split("/")[-1]
        if 'Content-Disposition' in r.headers:
            if r.headers['Content-Disposition'].find('filename=') != -1:
                filename = r.headers['Content-Disposition'].split('filename="')[1].split('"')[0]


    total_length = int(r.headers.get('content-length'))
    try:
        print(r.headers['Accept-Ranges'])

        chunk_size = total_length//CHUNK_POOL +1
        es = total_length // chunk_size + 1
        info[filename] = 0
        info[filename + '.size'] = es
        c = 0
        bytesstrings = []

        print(total_length)
        print(chunk_size)
        for i in range(0,total_length,chunk_size):
            bytesstrings.append('bytes='+str(i)+'-'+str(min(i+chunk_size-1,total_length-1)))
            c+=1

        print(c)
        inner_executor = concurrent.futures.ThreadPoolExecutor(max_workers=CHUNK_POOL)
        inner_executor.map(downloadFileChunk,[url]*c,bytesstrings,range(c),[filename]*c)

        inner_executor.shutdown()

        with open(os.path.join(dir, filename), "wb") as file:
            for i in range(0,c):
                chunk = open(filename+".part"+str(i), 'rb').read()
                file.write(chunk)
                print("Joining " + str(i))
                os.remove(filename+".part"+str(i))




    except Exception:
        chunk_size = 1024*1024*1
        es = total_length // chunk_size + 1
        info[filename] = 0
        info[filename + '.size'] = es

        r = requests.get(url,headers=HEADERS, stream=True)
        info[filename] = 0
        info[filename + '.size'] = es
        print('started ' + filename)
        with open(os.path.join(dir, filename), "wb") as file:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    print('chunking')
                    file.write(chunk)
                    info[filename] = info[filename]+1
                    file.flush()


    print('DONE ' + filename)
    duration = 1000  # milliseconds
    freq = 440  # Hz
    winsound.Beep(freq, duration)
    info.pop(filename)
    info.pop(filename + '.size')

def downloadFileChunk(url,bytes,index,name):
    global update
    print(str(url)+" ||| "+str(bytes)+" ||| "+str(index)+" ||| "+str(name))
    update = True
    try:
        ok = False
        info[name+".part"+str(index)] = 0
        size = int(bytes.split('-')[1]) - int(bytes.split('-')[0].split('=')[1])+1
        chunk_size = 1024 * 1024 * 1
        es = size // chunk_size +1
        info[name+".part"+str(index) + '.size'] = es
        while not ok:
            #print('started chunk',index,'of',name)
            with open(os.path.join(name+".part"+str(index)), "wb") as file:
                headers = {'Range': bytes, 'user-agent':USERAGENT}
                if COOKIE!=None:
                    headers['cookie']=COOKIE
                r = requests.get(url,headers=headers,stream=True)
                #print(str(url) + " ||| " + str(bytes) + " ||| " + str(index) + " ||| " + str(name) + " ||| " + str(r.status_code))
                #print(r.headers)
                if r.status_code == 200 or r.status_code == 206:
                    update = True
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            info[name+".part"+str(index)] = info[name+".part"+str(index)] + 1
                            file.flush()
                    info.pop(name+".part"+str(index))
                    info.pop(name+".part"+str(index) + '.size')
                    info[name]+=1
                    ok= True
                else:
                    time.sleep(10)
    except Exception as e:
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")
        print(e)
        print(str(url) + " ||| " + str(bytes) + " ||| " + str(index) + " ||| " + str(name))
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")
        print("EXCEPTIONNNNNNNNNNNN")


def Info():
    global update
    info_copy = info.copy()
    updatestring = ""
    updatestring += 'currently working on ' + str(len(info_copy)//2) + ' downloads\n'
    for k in info_copy:
        if not k.endswith('.size'):
            updatestring += str(k)+" "+str(info_copy[k])+"/"+str(info_copy[k+'.size'])+'\n'

    if len(info_copy)==0:
        update = False

    return updatestring

def InfoF(FormatLength):
    global update
    pool_size = FormatLength//CHUNK_POOL

    info_copy = info.copy()
    updatestring = ""
    updatestring += 'currently working on ' + str(len(info_copy)//2) + ' download threads\n'
    for k in info_copy:
        if not k.endswith('.size') and not k.split(".")[-1].startswith("part"):
            size_str = str(info_copy[k+'.size'])
            down_str = str(info_copy[k]).zfill(len(size_str))
            name = str(k)
            updatestring += name +" "+down_str+"/"+size_str+'\n▛'
            for i in range(int(size_str)):
                name = k+".part"+str(i)
                if name in info_copy:
                    progress = int(int(info_copy[name]) / int(info_copy[name + '.size']) * (pool_size))
                    progress_block_i = int(int(info_copy[name]) / int(info_copy[name + '.size']) * (pool_size*3)) % 3
                    '''
                    size_str = str(info_copy[name + '.size'])
                    down_str = str(info_copy[name]).zfill(len(size_str))
                    updatestring += down_str+"/"+size_str+' '
                    '''
                    
                    blocks = [' ','▌','█']
                    
                    progress_block = blocks[progress_block_i]
                    
                    updatestring+=progress*'█'+ progress_block +((pool_size-1)-progress)*' '
                else:
                    updatestring+=(pool_size)*'█'
            updatestring += "▟\n"
                


    if len(info_copy)==0:
        update = False

    return updatestring

def GetInfo():
    return info.copy()

def AddNewLink(link):
    links = [link]
    startDownloadBatch(links)

update = True

defaulturl = 'http://speedtest.ftp.otenet.gr/files/test1Gb.db'
#defaulturl = 'http://speedtest.ftp.otenet.gr/files/test100Mb.db'