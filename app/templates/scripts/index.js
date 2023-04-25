async function send(name){
    let path, res, data, qmodal;
      // получаем введеные в поля имя и возраст
      const username = document.getElementById("floatingName").value;
      const useremail = document.getElementById("floatingEmail").value;
      const userpassword = document.getElementById("floatingPassword").value;
      
      if (username == "") {
            return alert("Введите логин");
      } else if (useremail == "") {
            return alert("Введите элетронную почту");
      } else if (userpassword == "") {
            return alert("Введите пароль");
      }  
      // отправляем запрос
      if (name == "login") {
              var details = {"username": username, "password": userpassword, "client_secret": useremail}
              var formBody = [];
              for (var property in details) {
                var encodedKey = encodeURIComponent(property);
                var encodedValue = encodeURIComponent(details[property]);
                formBody.push(encodedKey + "=" + encodedValue);
              }
              formBody = formBody.join("&");
              response = await fetch('/auth', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                },
                body: formBody
              })
                  if (response.ok) {
                        const tokenData = await response.json();
                        //console.log(tokenData["refresh_token"])
                        await saveToken(tokenData["refresh_token"]);
                        const res = await fetch('/set_cookie', {
                            method: 'POST',
                            headers: {
                                "Accept": "application/json", "Content-Type": "application/json"
                            },
                            body: JSON.stringify(tokenData)
                        });
                        if (res.ok) {                            
                            await authFetch();
                        } else {
                            console.log(res)
                        }
                        //console.log('tokenData: ', tokenData)
                        //console.log('type tokenData: ', typeof tokenData)
                        //document.cookie = `access_token=${tokenData["access_token"]}`
                        //document.cookie = `refresh_token=${tokenData["refresh_token"]}`
                        //document.cookie = `expires=${tokenData["expires"]}`
                        //document.cookie = `token_type=${tokenData["token_type"]}`
                        //token = document.cookie.split("=");
                          
                  } else {
                        data = await response.json();
                        res = data.detail;
                        qmodal = getDataDetail(res);
                        modal(qmodal);  
                  }    
         } else {
              await regFetch(username, useremail, userpassword);                            
        };
};

async function regFetch(username, useremail, userpassword) {
    response = await fetch("/add_users", {
        method: "POST",
        headers: { "Accept": "application/json", "Content-Type": "application/json"},
        body: JSON.stringify({
        name: username,
        email: useremail,
        password: userpassword
        })                   
    });
    if (response.status == 400) {
        data = await response.json();
        res = data.detail;
        qmodal = getDataDetail(res);
        modal(qmodal);
        document.addEventListener('click', function () {
            window.location.reload();
        })
    } else if (response.status == 200) {
        qmodal = "Зарегистрировано";
        modal(qmodal);
        document.addEventListener('click', function () {
            window.location.assign('/users');
        })      
    } else {
        console.log('response: ', response)
    }
};

async function authFetch() {
    //data = await response.json(); 
    //document.getElementById("message").textContent = data.message;
    access_token = $.cookie("access_token");
    //cookies = document.cookie.split(";")
    //token = cookies[1].split("=");  
    response = await fetch("/users", {
        method: "GET",
        headers: { "Accept": "application/json", "Content-Type": "application/json", 'Authorization': 'Bearer ' + access_token},              
    })
    if (response.status == 400) {
        data = await response.json();
        res = data.detail;
        qmodal = getDataDetail(res);
        modal(qmodal);
        document.addEventListener('click', function () {
            window.location.reload();
        })
    //window.location.href = '/templates/users.html'
    } else if (response.status == 200) {
        console.log('response: ', response);     
        window.location.assign('/users');
        //return Promise.resolve()      
    } else if (response.status == 401) {
        console.log("Not auth");
        //await refreshToken();
        //await authFetch();
    } else {
        console.log('response: ', response);
    }
};

//var response = async() => {
//    await fetch("/users", {
//        method: "GET",
//        headers: { "Accept": "application/json", "Content-Type": "application/json", 'Authorization': 'Bearer ' + access_token},              
//    })
//    .then((resp) => resp.json())
//    .then (async function(data){
//        console.log(data)
//    })
//}
