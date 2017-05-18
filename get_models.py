import urllib2, os, httplib, json, argparse

def load_metafile():
    with open('metadata.json', 'r') as fp:
        data = json.load(fp)
    return data

def main():
    download(model_url, './')

def download(model_url, save_dir):
    filename = os.path.join(save_dir, model_url.split('/')[-1])
    u = urllib2.urlopen(model_url)
    f = open(filename, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print 'Downloading model from %s to %s' % (model_url, filename)
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
        break
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download trained models for WMIGFT")
    parser.add_argument("-d", "--directory", help="Directory to download the models to.")
    parser.add_argument("-e", "--experiment",help="Choose experiment to download.")
    parser.add_argument("-s", "--specific",  help="Specific experiment.")
    args = parser.parse_args()
    metafile_base_url = load_metafile()['base_url']
    metafile_flags    = load_metafile()['flags']
    to_download = []

    if args.experiment:
        assert args.experiment in metafile_flags.keys()
        if args.specific:
            assert args.specific in metafile_flags[args.experiment].keys()
            to_download.append(os.path.join(metafile_base_url, metafile_flags[args.experiment][args.specific]))
        else:
            # Download all
            if type(metafile_flags[args.experiment]) is dict:
                for s in metafile_flags[args.experiment].values():
                    to_download.append(os.path.join(metafile_base_url, s))
            else:
                to_download.append(os.path.join(metafile_base_url, metafile_flags[args.experiment]))
    else:
        if args.specific:
            print 'Cannot use -s flag alone, provide a -e flag'
            exit()
        else:
            for k,e in metafile_flags.iteritems():
                if type(e) is not dict:
                    to_download.append(os.path.join(metafile_base_url, e))
                else:
                    for s in e.values():
                        to_download.append(os.path.join(metafile_base_url, s))

    print to_download
    save_dir = args.directory if args.directory else './models'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for url in to_download:
        print url
        try:
            r = urllib2.urlopen(url)
        except urllib2.URLError as e:
            r = e
        if r.code == 404:
            print 'Request rejected, the server may be down, try again later.'
            continue
        download(url, save_dir)

    #main()
