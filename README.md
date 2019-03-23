# EmbyWatchedBackup
Backup and restore Emby watched status

These scripts will allow you to back up and restore your users watched statues for their movies and tv shows.
For movies it uses the item name and external URLs (imdb, trakt etc) to match your media with backed up watched statues.
For TV Shows it uses the show name, season, episode number and external URLs (imdb, trakt etc) to match media to the backed up watched statuses.

Because it uses the names and external URLs you need to make sure your media is fully scanned in and identified. This will give the backup the best chance of matching your loaded media.

### Usage:

#### Backup
Create a config.json file with your user and server details
Run the backup.py script
 - backup.py config.json

This will produce the backup file

This backup file is in JSON format and contains the user details including the password.

#### Restore
Run the restore.py script
 - restore.py [path to the backup file from above]
 
 This will try to find items in your library for the user that the back was made from and if the matched item has a different watched status will set the items watched status to what is in the backup.
 
