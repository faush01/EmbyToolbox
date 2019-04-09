import os
import errno

def mirror_strm_files(sourceDir, destinationDir):

    for dirName, subdirList, fileList in os.walk(sourceDir):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            if fname.find(".mkv") > -1 or fname.find(".mp4") > -1:
                #print('\t%s' % fname)

                media_path = os.path.join(dirName, fname)

                dest_path = dirName.replace(sourceDir, "")
                dest_path = os.path.join(destinationDir, dest_path, fname + ".strm")

                if not os.path.exists(dest_path):
                    print('\t%s' % media_path)
                    print('\t%s' % dest_path)
                    print('')

                    try:
                        os.makedirs(os.path.dirname(dest_path))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                    with open(dest_path, "w") as f:
                        f.write(media_path)


source = "C:\\Data\\media\\MoviesSmallList\\"
destination = "C:\\Data\\media\\EmbyStrmMedia\\MoviesSmallList\\"
mirror_strm_files(source, destination)

source = "C:\\Data\\media\\MoviesMedia\\"
destination = "C:\\Data\\media\\EmbyStrmMedia\\MoviesMedia\\"
mirror_strm_files(source, destination)

source = "C:\\Data\\media\\Drive02\\"
destination = "C:\\Data\\media\\EmbyStrmMedia\\TvShows\\"
mirror_strm_files(source, destination)
