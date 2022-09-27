class UserCreationPage {
    render() {
        ROOT_USER_CREATION.innerHTML = String.raw`   
            <h1>Создание пользователя</h1>
            <form method="post">
                <input type="text" name="username"  id="username" class="form-control" placeholder="Имя пользователя"><br>
                <input name="email" id="email" type="text"  class="form-control" placeholder="Введите емайл"><br>
                <input name="password" id="password" type="text" class="form-control" placeholder="Введите пароль"><br>
                <div class="form-check" name="admin"><input class="form-check-input" name="admin" type="checkbox"  id="admin"/>
                    <label class="form-check-label "  for="flexCheckDefault">Администратор</label>
                </div>
                <button type="submit" class="btn btn-success">Отправить</button>
            </form>
            </div>    
        `;
    }
}

const userCreationPage = new UserCreationPage();