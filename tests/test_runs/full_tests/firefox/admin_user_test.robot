*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${LOGIN URL}    http://127.0.0.1:5000/
${BROWSER}    Firefox
${name}    Larppi.Jarppi
${wrong_place}    Luvaton pääsy!
${new_user_fname}    Jarppi
${new_user_lname}    Larppi
${new_user_uname}    Larppi.Jarppi
${new_user_password}    jarppi.jarppi
${user_case}    Opettaja
${student_fname}    Niko
${student_lname}    Keurulainen
${class_group}    ptTvTweb4
${current_username}    admin
${current_password}    admin
${student_fname_toolong}    kjlfjskrisurnmksoaprusitdksorsuts
${student_lname_toolong}    kjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutsd
${class_group_toolong}    ldksorjfuidieksop
${user_fname_toolong}    lfkdjsorispiduekslaorusirdksjelade
${user_lname_toolong}    kjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutskjlfjskrisurnmksoaprusitdksorsutsd
${user_password_tooshort}    ksjrid

*** Test Cases ***
Create User
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change To User Management Page
    Input NewUserFirstname
    Input NewUserLastname
    Input NewUserPassword
    Repeat NewUserPassword
    Select User Case
    Submit User
    Log Out
    Login With New User
    Input NewUsername
    Input NewPassword
    Submit NewCredentials
    Welcome Page Should Be Open
    [Teardown]    Close Browser

Add Student
    Open Browser To Login Page
    Input Username
    Input Password
    Submit adminCredentials
    Change To Student Creation Page
    Input Student Firstname
    Input Student Lastname
    Select Class Group
    Submit Student
    Log Out
    [Teardown]    Close Browser

Remove User
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change To User Management Page
    Check Users
    Remove User
    Check If User Removed
    Log Out
    [Teardown]    Close Browser

Page Restrictions
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change Page To Attendance Checking Page
    Change Page To Attendance Marking Page
    Change Page To User
    Log Out
    [Teardown]    Close Browser

Insert Restrictions
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change To Student Creation Page
    Input Too Long Student Fname
    Input Too Long Student Lname
    Change To ClassGroup Creation Page
    Input Too Long Group Marking
    Change To User Management Page
    Input Too Long User Fname
    Input Too Long User Lname
    Input Too Short Password
    Log Out
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Title Should Be    Kirjaudu sisään - Janus

Input Username
    Input Text    username    ${current_username}

Input Password
    Input Text    password    ${current_password}

Submit Credentials
    Click Button    submit

Change To User Management Page
    Click Link    Käyttäjänhallinta
    Title Should Be    Käyttäjänhallinta - Janus

Input NewUserFirstname
    Input Text    firstname    ${new_user_fname}

Input NewUserLastname
    Input Text    lastname    ${new_user_lname}

Input NewUserPassword
    Input Text    password    ${new_user_password}

Repeat NewUserPassword
    Input Text    password2    ${new_user_password}

Select User Case
    Select From List By Label    clearance    ${user_case}

Submit User
    Click Button    user_submit

Log Out
    Click Link    Kirjaudu Ulos
    Title Should Be    Kirjaudu sisään - Janus

Login With New User
    Title Should Be    Kirjaudu sisään - Janus

Input NewUsername
    Input Text    username    ${new_user_uname}

Input NewPassword
    Input Text    password    ${new_user_password}

Submit NewCredentials
    Click Button    submit

Welcome Page Should Be Open
    Title Should Be    Koti - Janus

Submit adminCredentials
    Click Button    submit
    Title Should Be    Koti - Janus

Change To Student Creation Page
    Click Link    Lisää oppilas
    Title Should Be    Lisää oppilas - Janus

Input Student Firstname
    Input Text    firstname    ${student_fname}

Input Student Lastname
    Input Text    lastname    ${student_lname}

Select Class Group
    Select From List By Label    group    ${class_group}

Submit Student
    Click Button    submit

Check Users
    Click Button    get_users
    Element Should Be Visible    name=user_table

Remove User
    Click Link    ${name}

Check If User Removed
    Click Button    get_users
    Element Should Not Contain    name=name    ${name}

Change Page To Attendance Checking Page
    Go To    http://127.0.0.1:5000/attendance/check_attendance
    Title Should Be    Koti - Janus
    Element Text Should Be    class=alert    ${wrong_place}

Change Page To Attendance Marking Page
    Go To    http://127.0.0.1:5000/attendance/group_select
    Title Should Be    Koti - Janus
    Element Text Should Be    class=alert    ${wrong_place}

Change Page To User
    Click Link    Käyttäjä
    Title Should Be    Käyttäjä - Janus

Input Too Long Student Fname
    Input Text    firstname    ${student_fname_toolong}
    Input Text    lastname    ${student_lname}
    Click Button    submit
    Element Text Should Be    class=help-block    max 32 merkkiä

Input Too Long Student Lname
    Input Text    firstname    ${student_fname}
    Input Text    lastname    ${student_lname_toolong}
    Click Button    submit
    Element Text Should Be    class=help-block    max 128 merkkiä

Change To ClassGroup Creation Page
    Click Link    Lisää ryhmä

Input Too Long Group Marking
    Input Text    marking    ${class_group_toolong}
    Click Button    submit
    Element Text Should Be    class=help-block    max 16 merkkiä

Input Too Long User Fname
    Input Text    firstname    ${user_fname_toolong}
    Input Text    lastname    ${new_user_lname}
    Input Text    password    ${new_user_password}
    Input text    password2    ${new_user_password}
    Select From List By Label    clearance    ${user_case}
    Click Button    user_submit
    Element Text Should Be    class=help-block    max 32 merkkiä

Input Too Long User Lname
    Input Text    firstname    ${new_user_fname}
    Input Text    lastname    ${user_lname_toolong}
    Input Text    password    ${new_user_password}
    Input text    password2    ${new_user_password}
    Select From List By Label    clearance    ${user_case}
    Click Button    user_submit
    Element Text Should Be    class=help-block    max 128 merkkiä

Input Too Short Password
    Input Text    firstname    ${new_user_fname}
    Input Text    lastname    ${new_user_lname}
    Input Text    password    ${user_password_tooshort}
    Input text    password2    ${user_password_tooshort}
    Select From List By Label    clearance    ${user_case}
    Click Button    user_submit
    Element Text Should Be    class=help-block    Vähintään 8 merkkiä



