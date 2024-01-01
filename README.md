  

> Step-by-Step guide for migrating courses from the Blackboard Ultra Course package to moodle Course version > 1.9.

  



 
  

> **“_The following process tested on a Blackboard ultra course package and importing that into moodle 3.10 after following below steps”_**

  
### **Objective** :

  

Migrating  **blackboard ultra ** course  to Moodle 3.10, via exporting from Blackboard and importing that into Moodle.



### **Solution :**

  -- This will crerate a moodle1 backup file, which is supported in moodle latest version as well   

To achieve the target , you need to follow the below steps:
 

1 . Setup the Conversion Tool 

  

2. Convert the exported BB (blackboard file) to Moodle 
  

3 . Make some mentioned changes in moodle code and DB for moodle version > 1.9 
  

4 . Import the Converted file into Moodle version > 1.9 

  

#### **Step-1 : –**
* download this repository
Assuming that you are using linux environment.

-  **Pre-requisite : python3 and pip is installed**

  

**If not** , then install python 3 and pip first, steps are –

  

Check for python

  

`>>> python3 --version`

  

If python not found : [https://www.python.org/downloads/](https://www.python.org/downloads/)

  

Install pip and setup tools

  

`>>> sudo apt-get install python-setuptools`

  


Now you have installed Python and pip and I assume that you have downloaded the conversion tool zip file. Let’s say you are under the directory **/var/www/html** and conversion tool is present at **/var/www/html/bbultra_2_moodle.zip**

  

- Unzip that file , the directory **bbultra_2_moodle** should be created.

- Go inside that directory , location /var/www/html/bbultra_2_moodle

- setup.py file will be there

- Run following command `**>>>** **pip install .**`

- Package has been installed, you can cross check via typing  in commandline **`>>> bbultra2moodle`**

- If bbultra2moodle is not found than please try python reteach and try after running following command `**export PATH=$PATH:~/.local/bin**`


  

#### **Step-2 :**

  

You just need to run this command

  

`>>> bbultra2moodle content/bb-sample.zip -o content/moodle-file.zip`

  *OR*
  -- you can define input and ouput path under test.py and run following command
   ``python3  bbultra2moodle/test.py``

_bb-sample.zip is then name of bb course zip file name . I assume that you are currently present under the directory where bb-sample.zip is present_

  

_moodle-file.zip will be converted zip file that will be used to import in moodle.



  

#### **Step-3 : –**

  

If you are utilising moodle > 1.9, Update the following code

  

Line number 1257 File: backup/converter/moodle1/handlerlib.php

  

_// replay the upgrade step 2011060301 – Rename field defaultgrade on table question to defaultmark

$data[‘defaultmark’] = $data[‘defaultgrade’];_

  

```

  

// code to add for for blackboard course

$data['generalfeedbackformat'] = '1';

$data['createdby'] = '2'; // can be change

$data['modifiedby'] = '2'; // can be change

// END

```

  

**And run the query:**  ``ALTER TABLE `mdl_qtype_match_subquestions` CHANGE `answertext` `answertext` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL;``

  

#### **Step -4 :**

  

Import that moodle-file.zip into Moodle setup , and you are done.

 ## DONE ##

  
  ### -- To Convert Blackboard Standard version course, you can go through following url

[https://developerck.com/blackboard-course-migration-to-moodle/](https://developerck.com/blackboard-course-migration-to-moodle/)