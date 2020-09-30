*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${LOGIN URL}    http://127.0.0.1:5000/
${BROWSER}    Firefox
${username}    Caselius.Annika
${password}    annika.caselius
${classgroup}    ptTvTweb3
@{students}    Olli Kurki    Tero Immonen    Janne Kekki    Markus Heinonen    Matthew Simpson    Aki Siltanen
${success}    Läsnäolot merkattu!
${wrong_place}    Luvaton pääsy!
${success_date}    Läsnäolot järjestetty laskeutuen päivämäärällä!
${success_name}    Länäolot järjestetty nimijärjestykseen!
${student_name_toolong}    lfkdjsorispiduekslaorusirdksjeladelfkdjfkdjsorispiduekslaorusirdksjeladelfkdjfkdjsorispiduekslaorusirdksjeladelfkdjsorispiduekslaorusirdksjeladelfkdjsorispiduekslaorusirdksjeladelfkdjsorispiduekslaorusirdksjeladelfkdjsorispiduekslaorusirdksjeladelfkdjsorispiduekslaorusirdksjelade
${start_date}    2020.09.13
${end_date}    2020.09.20
${start_date_toolong}    2020,.094.132
${end_date_toolong}    2020,.094.202
${student_name}    Olli Kurki

*** Test Cases ***
Mark Attendance
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change To Attendance Marking Page
    Select ClassGroup
    Mark Students Present
    Log Out
    [Teardown]    Close Browser

Check Attendance
    Open Browser To Login Page
    Input Username
    Input Password
    Submit Credentials
    Change To Attendance Checking Page
    Check By Date
    Check By Name
    Check By Student Name
    Check By Date Span
    Log Out
    [Teardown]    Close Browser

Page Restrictions
    Open Browser To Login Page
    Input username
    Input Password
    Submit Credentials
    Change Page To User Control
    Change Page To Student Control
    Change Page To Group Control
    Change Page To User
    Log Out
    [Teardown]    Close Browser

Input Restrictions
    Open Browser To Login Page
    Input username
    Input Password
    Submit Credentials
    Change To Attendance Checking Page
    Input Too Long Student Name
    Input Too Long Date
    Log Out
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Title Should Be    Kirjaudu sisään - Janus

Input Username
    Input Text    username    ${username}

Input Password
    Input Text    password    ${password}

Submit Credentials
    Click Button    submit

Change To Attendance Marking Page
    Click Link    Läsnäolon kirjaus
    Title Should Be    Läsnäolo - Janus

Select ClassGroup
    Select From List By Label    group_select    ${classgroup}
    Click Button    submit

Mark Students Present
    Select From List By Label    attendance    @{students}
    Click Button    submit
    Element Text Should Be    class=alert    ${success}

Log Out
    Click Link    Kirjaudu Ulos
    Title Should Be    Kirjaudu sisään - Janus

Change To Attendance Checking Page
    Click Link    Läsnäolon tarkistus
    Title Should Be    Läsnäolo tarkistus - Janus

Check By Date
    Select From List By Label    group_select    ${classgroup}
    Click Button    by_date
    Element Text Should Be    class=alert    ${success_date}
    ${count} =    Get Element Count    student
    Should Be True    ${count} > 1

Check By Name
    Select From List By Label    group_select    ${classgroup}
    Click Button    by_student
    Element Text Should Be    class=alert    ${success_name}

Check By Student Name
    Input Text    student_name    ${student_name}
    Click Button    by_name
    Element Should Contain    name=name    ${student_name}

Check By Date Span
    Input Text    specific_date_start    ${start_date}
    Input Text    specific_date_end    ${end_date}
    Click Button    by_specific_date
    Element Should Be Visible    name=attendance

Change Page To User Control
    Go To    http://127.0.0.1:5000/admin/create_user
    Title Should Be    Koti - Janus
    Element Text Should Be    class=alert    ${wrong_place}

Change Page To Student Control
    Go To    http://127.0.0.1:5000/admin/add_student
    Title Should Be    Koti - Janus
    Element Text Should Be    class=alert    ${wrong_place}

Change Page To Group Control
    Go To    http://127.0.0.1:5000/add_groups
    Title Should Be    Koti - Janus
    Element Text Should Be    class=alert    ${wrong_place}

Change Page To User
    Click Link    Käyttäjä
    Title Should Be    Käyttäjä - Janus

Input Too Long Student Name
    Input Text    student_name    ${student_name_toolong}
    Click Button    by_name
    Element Text Should Be    name=student_name_error    max 160 merkkiä

Input Too Long Date
    Input Text    specific_date_start    ${start_date_toolong}
    Input Text    specific_date_end    ${end_date}
    Click Button    by_specific_date
    Element Text Should Be    name=date_start_error    vvvv.kk.pp
    Input Text    specific_date_start    ${start_date}
    Input Text    specific_date_end    ${end_date_toolong}
    Click Button    by_specific_date
    Element Text Should Be    name=date_end_error    vvvv.kk.pp
