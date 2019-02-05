# pstanalyzer

A tool that analyses a PST File and returns the possible owner of the PST based on the nr. of recurring senders in sent items folders and the nr. of recurring recipients in all the other folders.<br>
The output format is:<br>
<br> possible@owner.com - % (calculated from sent items)
<br> possible@owner.com - % (calculated from all other folders)
 
 
The script utilises the libpff library under LGPLv3+ License.
