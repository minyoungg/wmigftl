import urllib2, os

model_url = 'http://minyounghuh.com/papers/analysis/model/918.tar'
model_macro = {'hierarchy': {'1000':,
                             '918':,
                             '753':,
                             '486':,
                             '127':,
                             '79 ':,
                             '9':},
                'class': {'1000':,
                          '500':,
                          '250':,
                          '125':,
                          '50':},
               'split': {'minA':,
                         'minB':,
                         'ranA':,
                         'ranB':,}
               'pascal_removed': }

def main():
    download(model_url, './')

def download(model_url, save_dir):
    filename = model_url.split('/')[-1]
    u = urllib2.urlopen(model_url)
    f = open(filename, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print 'Downloading model from %s to %s' % (model_url, os.path.join(save_dir, filename))
    print "Downloading: %s Bytes: %s" % (filename, file_size)

    file_size_dl, block_sz = 0, 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    f.close()


if __name__ == '__main__':
    main()
