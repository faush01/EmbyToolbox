#$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$env:emby_url = "http://localhost:8096"
$env:api_key = ""

$datetime = (Get-Date).ToString('yyyy-MM-dd-HH-mm-ss')
$log_file_path = "C:\Tools\imdb_ratings\logs\$datetime.log"
$scripts_dir = "C:\Tools\imdb_ratings"

$Path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\Library\mingw-w64\bin"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\Library\usr\bin"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\Library\bin"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\Scripts"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\bin"
$Path = $Path + [IO.Path]::PathSeparator + "C:\ProgramData\miniconda3\condabin"
$env:Path=$Path
$env:PYTHONUTF8=1
Set-Location -Path "$scripts_dir"

"**************************************************************************************************************************" >> $log_file_path

$command_started = Get-Date
Invoke-Expression -Command "python $scripts_dir\emby_get_imdb_ids.py 1>> $log_file_path 2>&1"
$time_taken = ((Get-Date) - ($command_started)).TotalMinutes
"TimeTaken: $time_taken" >> $log_file_path
"**************************************************************************************************************************" >> $log_file_path

$command_started = Get-Date
Invoke-Expression -Command "python $scripts_dir\imdb_rating_extract.py 1>> $log_file_path 2>&1"
$time_taken = ((Get-Date) - ($command_started)).TotalMinutes
"TimeTaken: $time_taken" >> $log_file_path
"**************************************************************************************************************************" >> $log_file_path

$command_started = Get-Date
Invoke-Expression -Command "python $scripts_dir\emby_update_ratings.py 1>> $log_file_path 2>&1"
$time_taken = ((Get-Date) - ($command_started)).TotalMinutes
"TimeTaken: $time_taken" >> $log_file_path
"**************************************************************************************************************************" >> $log_file_path
