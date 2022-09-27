class UserListPage {
    constructor() {
        this.url = '/api/v1/users/list';
    }
   
    user_creation() {
        alert("ok");

    }

    user_update() {
        alert("ok");

    }

    async fill_data() {
        // Описание таблицы
        let table_template = [
            { "head": "Логин", "row": "name" },
            { "head": "Электронная почта", "row": "email" },
            { "head": "Пол", "row": "gender" },
            { "head": "Дата создания", "row": "created_at" },
            { "head": "Возраст", "row": "age" },
            { "head": "Описание", "row": "description" },
            { "head": "Полные права", "row": "is_admin" },
            { "head": "Аккаунт активирован", "row": "is_active" }]

        const response = await fetch(`/api/v1/users/`, {
            method: 'GET'
        });

        if (response.status !== 200) {
            errorPage.render(response);
        } else {
            let user_list = await response.json();
            let table_users = document.querySelector("#table_users");
            let table_thead = table_users.querySelector("thead");
            let tr_head =  table_thead.querySelector("tr");

            let table_tbody = table_users.querySelector("tbody");
            let tr_body =  table_tbody.querySelector("tr");
            for (let row_tmpl of table_template) {
                let th = document.createElement("th");
                th.innerHTML = row_tmpl.head;
                tr_head.append(th);

                let td = document.createElement("td");
                td.setAttribute("data-value", row_tmpl.row);
                tr_body.append(td);
            }
        
            let table_row = table_tbody.querySelector("tr");
            for (let row of user_list) {
                let tmpl_row = table_row.cloneNode(true);
                for (let td of tmpl_row.querySelectorAll("td")) {
                    td.innerHTML = row[td.dataset.value];
                }

                table_tbody.append(tmpl_row);
                console.log(row);
            }
            // Удаляем шаблон
            table_row.remove();
        }
    }

    render() {
        let buttonUserCreation = String.raw`
        <button onclick="userListPage.user_creation();" class="btn btn-info">          
            <span> Создать нового пользователя </span>
       </button>
       `;

        let buttonUserUpdate = String.raw`
        <button onclick="userListPage.user_update();" class="btn btn-info">          
            <span> Создать нового пользователя </span>
        </button>
        `;

        ROOT_USER_LIST.innerHTML = String.raw`   
            ${buttonUserCreation}
            ${buttonUserUpdate}
            <hr>
            <div>
                <h1>Список пользователей</h1>
                <table id="table_users" class="table table-bordered">
                <thead>
                    <tr>            
                    </tr>
                </thead>
                <tbody>
                    <tr>                 
                    </tr>
                </tbody>
                </table>
            </div>       
        `;
              
        userListPage.fill_data();
    }
}

const userListPage = new UserListPage();