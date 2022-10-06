class LoginPage {
    async check() {

        let data = new FormData()
        data.append('username', document.querySelector('#loginInput').value)
        data.append('password', document.querySelector('#loginPassword').value)

        const response = await fetch(`/v1/login`, {
            method: 'POST',
            body: data
        });

        if (response.status !== 200) {
            errorPage.render(response);
        } else {
            
            loginPage.reset();
            window.location.pathname = userListPage.url;
        }
    }

    reset() {
        ROOT_LOGIN.innerHTML = `<div ></div>`;
    }

    render() {
        ROOT_LOGIN.innerHTML = String.raw`   
            <form method="post">
                <h1 class="h3 mb-3 fw-normal">Введите логин или пароль</h1>

                <div class="w-50  align-center form-floating " >
                <input type="text"  name="username" class="form-control" id="loginInput"  placeholder="Логин">
                <label for="floatingInput">Логин</label>
                </div>
                <div class="w-50 align-center form-floating" >
                <input type="password"  name="password" class="form-control"  id="loginPassword" placeholder="Пароль">
                <label for="floatingPassword">Пароль</label>
                </div>
                <div class="checkbox mb-3">
                </div>
                <button class="w-50 align-center btn btn-lg btn-primary" 
                    type="button" onclick="loginPage.check();">Войти</button>
                <p class="mt-5 mb-3 text-muted">2022</p>
            </form>        
        `;
    }
}

const loginPage = new LoginPage();