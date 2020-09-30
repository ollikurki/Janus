*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${LOGIN URL}    http://127.0.0.1:5000/
${BROWSER}    Chrome
${invalid_username}    paavo
${invalid_password}    paavo
${username}    admin
${password}    admin

*** Test Cases ***
Check Login Invalid Username
    Open Browser To Login Page
    Input Invalid Username
    Submit Credentials

Check Login Invalid Password
    Input Invalid Password
    Submit Credentials
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Title Should Be    Kirjaudu sisään - Janus

Input Invalid Username
    Input Text    username    ${invalid_username}
    Input Text    password    ${password}

Input Invalid Password
    Input Text    username    ${username}
    Input Text    password    ${invalid_password}

Submit Credentials
    Click Button    submit
    Element Should Contain    class=alert    Invalid username or password