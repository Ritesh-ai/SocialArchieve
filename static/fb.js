alert("first");
// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
alert("second");

    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
        // Logged into your app and Facebook.
        testAPI();
    } else {
        // The person is not logged into your app or we are unable to tell.
        document.getElementById('status').innerHTML = 'Please log ' +
            'into this app.';
    }
}


// This function is called when someone finishes with the Login
// Button.  See the onlogin handler attached to it in the sample
// code below.
function checkLoginState() {
    FB.getLoginStatus(function (response) {
        statusChangeCallback(response);
    });
}


window.fbAsyncInit = function () {
    FB.init({
        appId: '269450677187982',
        cookie: true,  // enable cookies to allow the server to access
        // the session
        xfbml: true,  // parse social plugins on this page
        version: 'v2.8' // use graph api version 2.8
    });

    // Now that we've initialized the JavaScript SDK, we call
    // FB.getLoginStatus().  This function gets the state of the
    // person visiting this page and can return one of three states to
    // the callback you provide.  They can be:
    //
    // 1. Logged into your app ('connected')
    // 2. Logged into Facebook, but not your app ('not_authorized')
    // 3. Not logged into Facebook and can't tell if they are logged into
    //    your app or not.
    //
    // These three cases are handled in the callback function.

    FB.getLoginStatus(function (response) {
        statusChangeCallback(response);
    });

};

// Load the SDK asynchronously
(function (d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.
function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function (response) {
        console.log('Successful login for: ' + response.name);
        document.getElementById('status').innerHTML =
            'Thanks for logging in, ' + response.name + '!';

    });
}
var defaultImageUrl = "https://www.visioncritical.com/wp-content/uploads/2014/12/BLG_Andrew-G.-River-Sample_09.13.12.png";

var profileTagVar = document.getElementById('profileInfoTag');
var postTagVar = document.getElementById('poststag');
var pagesTagVar = document.getElementById('hdr');
var adminPagesText = document.getElementById('adminPagesText');

var profile = document.getElementById('profile');
profile.addEventListener("click", getProfile);

var post = document.getElementById('post');
post.addEventListener("click", getPost);

var pages = document.getElementById('pages');
pages.addEventListener("click", getPages);

function setVisibilityOfTags(first, second, third, isAdminPage) {

    if (isAdminPage == 0) {
        adminPagesText.style.display = 'none';
    } else {
        adminPagesText.style.display = 'block';
    }

    first.style.display = 'block';
    second.style.display = 'none';
    third.style.display = 'none';
}


function getProfile() {
    setVisibilityOfTags(profileTagVar, postTagVar, pagesTagVar, 0);

    FB.api(
        '/me', { fields: 'birthday,name,hometown,link,quotes,picture{url}' },
        function (response) {

            if (response && !response.error) {

                document.getElementById('profileInfoTag').style.visibility = 'visible';

                document.getElementById('userName').innerHTML = response.name;
                document.getElementById('userId').innerHTML =
                    'User Id : ' + response.id;

                document.getElementById('userBirthday').innerHTML =
                    'Birthday : ' + response.birthday;

                document.getElementById('profileImage').src = response.picture.data.url;

                $("#userProfileLink").attr("href", response.link);

            }
        }
    );
}

function getPost() {
    $('#poststag').empty();

    setVisibilityOfTags(postTagVar, profileTagVar, pagesTagVar, 1);
    var posttagvar = document.getElementById("poststag");

    FB.api(
        '/me/feed', { fields: 'attachments{media},message' },
        function (response) {
            if (response && !response.error) {

                if(response.data.length == 0){
                    adminPagesText.innerHTML = "No Posts found !!! ";
                }else{
                    adminPagesText.innerHTML = "User Posts !!! ";
                    for (var i = 0; i < response.data.length; i++) {

                        if (response.data[i].attachments != null) {
                            if (response.data[i].attachments.data != null) {
    
                                if (response.data[i].message != null) {
                                    posttagvar.innerHTML = posttagvar.innerHTML + '<div class="imgdataset"><span><img src=' +
                                        response.data[i].attachments.data[0].media.image.src
                                        + ' ></span><span>' + response.data[i].message + ' </span></div>';
                                } else {
                                    posttagvar.innerHTML = posttagvar.innerHTML + '<div class="imgdataset"><span><img  src=' +
                                        response.data[i].attachments.data[0].media.image.src
                                        + ' "></span><span class="textcenter"> No message in this post. </span></div>';
                                }
                            }
                        } else {
                            if (response.data[i].message != null) {
    
                                posttagvar.innerHTML = posttagvar.innerHTML + '<div class="imgdataset"><span><img src=' + defaultImageUrl + '></span><span class="textcenter">' + response.data[i].message + ' </span></div>';
                            } else {
                                posttagvar.innerHTML = posttagvar.innerHTML + '<div class="imgdataset"><span><img src=' + defaultImageUrl + '></span><span class="textcenter"> No message in this post. </span></div>';
                            }
                        }
                    }
                }



               
            }
        }
    );
}

function getPages() {

    $('#hdr').empty();
    setVisibilityOfTags(pagesTagVar, postTagVar, profileTagVar, 1);
    var hdrvar = document.getElementById("hdr");
    FB.api(
        '/me/accounts', { fields: 'about,cover,name,picture{url}' },
        function (response) {
            if (response && !response.error) {
                // download(JSON.stringify(response), 'json.json', 'text/plain');

               
                if(response.data.length == 0){
                    adminPagesText.innerHTML = "No Admin Pages found !!! ";
                }else{
                    adminPagesText.innerHTML = "Admin Pages !!! ";
                    for (var i = 0; i < response.data.length; i++) {
                        hdrvar.innerHTML = hdrvar.innerHTML + '<div class="imgdataset"><span><img src=' + response.data[i].picture.data.url
                            + '></span><span class="textcenter" onClick = "getPageInfo(' + response.data[i].id + ')">' + response.data[i].name + ' </span></div>';
                    }    
                }
            }
        }
    );
}

// new about,feed,cover,link,name,albums{cover_photo},photos,picture

// prev about,cover,description,display_subtext,emails,fan_count,general_info,albums,broadcast_messages{status,insights{description,title,name,values}},conversations{message_count},events,feed,likes

function getPageInfo(pageID) {
    console.log('page id: ' + pageID);

    FB.api("/" + pageID + "/", { fields: 'about,feed,cover,link,name,albums{cover_photo},photos,picture' },
        function (response) {
            if (response && !response.error) {
                // alert("Page information is downloaded");
                  
                // download(JSON.stringify(response), 'pageInfo.json', 'text/plain');
                var responseData = JSON.stringify(response);
                document.getElementById('datajson').value =responseData;
                console.log('admin pages' + responseData);
            }
        }
    );
}

function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}





















// adding elements in a list using append function

//     $("#hdr").append('<div><span><img src=' + response.data[i].picture.data.url
//         + '></span><span>' + response.data[i].name + ' </span></div>');



// code to convert json response into string

 // var responseData = JSON.stringify(response);
 // console.log('admin pages' + responseData);



