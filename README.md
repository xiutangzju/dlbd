### A Demonstration of DLBD: Database Logic Bug Detection System

This repository contains the source code of the frontend and a portion of the backend code for implementing the various datasets and schemes used in our "[A Demonstration of DLBD: Database Logic Bug Detection System](https://www.vldb.org/pvldb/vol16/p3914-wu.pdf)" VLDB demo paper.  

Database management systems (DBMSs) are prone to logic bugs that can result in incorrect query results. Current debugging tools are limited to single table queries and struggle with issues like lack of ground-truth results and repetitive query space exploration. In this paper, we demonstrate DLBD, a system that automatically detects logic bugs in databases. DLBD offers holistic logic bug detection by providing automatic schema and query generation and ground-truth query result retrieval. Additionally, DLBD provides minimal test cases and root cause analysis for each bug to aid developers in reproducing and fixing detected bugs. DLBD incorporates heuristics and domain-specific knowledge to efficiently prune the search space and employs query space exploration mechanisms to avoid the repetitive search. Finally, DLBD utilizes a distributed processing framework to test database logic bugs in a scalable and efficient manner. Our system offers developers a reliable and effec- tive way to detect and fix logic bugs in DBMSs.  

**(1) migrate the database**  
```
python manage.py makemigrations    
python manage.py migrate
```
**(2) startup frontend**
```
python manage.py runserver
```

**(3) open the web page**  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

